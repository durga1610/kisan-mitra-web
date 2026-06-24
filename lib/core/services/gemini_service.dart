import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http_parser/http_parser.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import '../config/api_config.dart';
import '../models/farm_model.dart';
import '../../features/weather/data/models/weather_model.dart';
import '../repositories/advisory_repository.dart';
import '../repositories/recommendation_repository.dart';

class GeminiService {
  final FarmModel? selectedFarm;
  final String languageCode;
  final WeatherModel? weather;

  GeminiService({this.selectedFarm, this.languageCode = 'en', this.weather});

  static Future<Map<String, String>> _getHeaders() async {
    final token = await FirebaseAuth.instance.currentUser?.getIdToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<void> _initModel() async {
    // Dummy initialization method for compatibility
  }

  Future<Map<String, String>> getResponse(String message) async {
    return AdvisoryRepository().getResponse(
      message: message,
      languageCode: languageCode,
      selectedFarm: selectedFarm,
      weather: weather,
    );
  }

  Future<Map<String, dynamic>> detectDisease(List<int> imageBytes, {String? filename, String? crop}) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) {
        throw Exception('FirebaseAuth.instance.currentUser is null. User must be authenticated to run disease analysis.');
      }

      final token = await user.getIdToken(true);
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/disease/detect'),
      );
      
      request.headers['Authorization'] = 'Bearer $token';
      request.headers['Accept'] = 'application/json';
      
      String mimeType = 'image/jpeg';
      final actualFilename = filename ?? 'image.jpg';
      final lowerFilename = actualFilename.toLowerCase();
      if (lowerFilename.endsWith('.png')) {
        mimeType = 'image/png';
      } else if (lowerFilename.endsWith('.webp')) {
        mimeType = 'image/webp';
      }
      
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          imageBytes,
          filename: actualFilename,
          contentType: MediaType.parse(mimeType),
        ),
      );
      
      request.fields['language'] = languageCode;
      if (crop != null) {
        request.fields['crop'] = crop.toLowerCase();
      }
      
      final streamedResponse = await request.send().timeout(const Duration(seconds: 90));
      final response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        return data;
      } else {
        throw Exception('Server returned status code ${response.statusCode}. Body: ${response.body}');
      }
    } catch (e) {
      if (kDebugMode) print('Error in custom API detectDisease: $e');
      throw Exception('Failed to analyze image: $e');
    }
  }

  Future<String> generateAdvisory({
    required String crop,
    required String soil,
    required String location,
    required String weather,
  }) async {
    return AdvisoryRepository().generateAdvisory(
      crop: crop,
      soil: soil,
      location: location,
      weather: weather,
      languageCode: languageCode,
    );
  }

  Future<String> generateRecommendationReasoning({
    required String cropName,
    required FarmModel farm,
    required WeatherModel weather,
    required String marketTrend,
  }) async {
    return RecommendationRepository().getRecommendationReasoning(
      cropName: cropName,
      farm: farm,
      weather: weather,
      marketTrend: marketTrend,
      languageCode: languageCode,
    );
  }

  Future<String> generateDynamicRecommendations({
    required FarmModel farm,
    required WeatherModel weather,
    required List<String> availableMarketCrops,
  }) async {
    final recs = await RecommendationRepository().getRecommendations(
      farm: farm,
      weather: weather,
      languageCode: languageCode,
    );
    
    final jsonList = recs.map((r) => {
      'cropName': r.cropName,
      'marketDemand': r.marketDemand,
      'expectedProfit': r.expectedProfit,
      'growthPeriod': r.growthPeriod,
      'matchReason': r.matchReason,
      'suitabilityScore': r.suitabilityScore,
    }).toList();
    
    return jsonEncode(jsonList);
  }

  Future<String> generateDailyGuidance({
    required String cropName,
    required int cropAgeDays,
    required String state,
    required String soilType,
    String? plantingDate,
    double? farmSize,
    String? waterAvailability,
    String? weatherCondition,
    double? temperature,
    double? humidity,
    double? rainfallForecast,
    double? windSpeed,
  }) async {
    return AdvisoryRepository().generateDailyGuidance(
      cropName: cropName,
      cropAgeDays: cropAgeDays,
      state: state,
      soilType: soilType,
      languageCode: languageCode,
      plantingDate: plantingDate,
      farmSize: farmSize,
      waterAvailability: waterAvailability,
      weatherCondition: weatherCondition,
      temperature: temperature,
      humidity: humidity,
      rainfallForecast: rainfallForecast,
      windSpeed: windSpeed,
    );
  }

  static Future<String?> checkCropSuitability(String cropName, FarmModel farm) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/advisory/suitability'),
        headers: await _getHeaders(),
        body: jsonEncode({
          'cropName': cropName,
          'farm': {
            'id': farm.id,
            'ownerId': farm.ownerId,
            'name': farm.name,
            'location': '${farm.village}, ${farm.district}, ${farm.state}',
            'soilType': farm.soilType,
            'waterAvailability': farm.waterAvailability,
            'landArea': farm.landArea,
            'plantedCrops': farm.plantedCrops.map((c) => c.cropName).toList(),
          },
        }),
      ).timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['suitable'] == true) {
          return null;
        }
        return data['reason'];
      }
    } catch (e) {
      if (kDebugMode) print('Error in checkCropSuitability: $e');
    }
    return null;
  }

  static Future<Map<String, dynamic>?> validateCropSuitability(String cropName, String farmId) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/crops/validate-before-planting'),
        headers: await _getHeaders(),
        body: jsonEncode({
          'farmId': farmId,
          'cropName': cropName,
        }),
      ).timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
    } catch (e) {
      if (kDebugMode) print('Error in validateCropSuitability: $e');
    }
    return null;
  }

  static Future<void> logSuitabilityAudit(
    String farmId,
    String cropName,
    double score,
    String reasons,
    bool ignoredWarning,
  ) async {
    try {
      await http.post(
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/crops/audit-log'),
        headers: await _getHeaders(),
        body: jsonEncode({
          'farmId': farmId,
          'cropName': cropName,
          'suitabilityScore': score,
          'reasons': reasons,
          'ignoredWarning': ignoredWarning,
        }),
      ).timeout(const Duration(seconds: 30));
    } catch (e) {
      if (kDebugMode) print('Error in logSuitabilityAudit: $e');
    }
  }
}
