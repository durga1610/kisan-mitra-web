import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import '../config/api_config.dart';
import '../models/farm_model.dart';
import '../../features/weather/data/models/weather_model.dart';

class AdvisoryRepository {
  static final AdvisoryRepository _instance = AdvisoryRepository._internal();
  factory AdvisoryRepository() => _instance;
  AdvisoryRepository._internal();

  static Future<Map<String, String>> _getHeaders() async {
    final token = await FirebaseAuth.instance.currentUser?.getIdToken();
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<Map<String, String>> getResponse({
    required String message,
    required String languageCode,
    FarmModel? selectedFarm,
    WeatherModel? weather,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/advisory/chat'),
        headers: await _getHeaders(),
        body: jsonEncode({
          'message': message,
          'language': languageCode,
          'farm': selectedFarm != null ? {
            'id': selectedFarm.id,
            'ownerId': selectedFarm.ownerId,
            'name': selectedFarm.name,
            'location': '${selectedFarm.village}, ${selectedFarm.district}, ${selectedFarm.state}',
            'soilType': selectedFarm.soilType,
            'waterAvailability': selectedFarm.waterAvailability,
            'landArea': selectedFarm.landArea,
            'plantedCrops': selectedFarm.plantedCrops.map((c) => c.cropName).toList(),
          } : null,
          'weather': weather != null ? {
            'condition': weather.condition,
            'temperature': weather.temperature,
            'season': weather.season,
            'humidity': weather.humidity,
            'windSpeed': weather.windSpeed,
            'rainChance': weather.rainChance,
          } : null,
        }),
      ).timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'text': data['text'] ?? 'The AI Advisory service is temporarily unavailable. Please try again.',
          'source': data['source'] ?? 'LOCAL_ENGINE',
        };
      }
    } catch (e) {
      if (kDebugMode) print('Error in AdvisoryRepository getResponse: $e');
    }
    return {
      'text': 'The AI Advisory service is temporarily offline. Please check your internet connection.',
      'source': 'LOCAL_ENGINE',
    };
  }

  Future<String> generateAdvisory({
    required String crop,
    required String soil,
    required String location,
    required String weather,
    required String languageCode,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/advisory/generate'),
        headers: await _getHeaders(),
        body: jsonEncode({
          'crop': crop,
          'soil': soil,
          'location': location,
          'weather': weather,
          'language': languageCode,
        }),
      ).timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['text'] ?? 'Expert advisory is currently unavailable for $crop.';
      }
    } catch (e) {
      if (kDebugMode) print('Error in AdvisoryRepository generateAdvisory: $e');
    }
    return 'Expert advisory is currently offline. Please check your network connection.';
  }

  Future<String> generateDailyGuidance({
    required String cropName,
    required int cropAgeDays,
    required String state,
    required String soilType,
    required String languageCode,
    String? plantingDate,
    double? farmSize,
    String? waterAvailability,
    String? weatherCondition,
    double? temperature,
    double? humidity,
    double? rainfallForecast,
    double? windSpeed,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/advisory/daily-guidance'),
        headers: await _getHeaders(),
        body: jsonEncode({
          'cropName': cropName,
          'cropAgeDays': cropAgeDays,
          'state': state,
          'soilType': soilType,
          'language': languageCode,
          'plantingDate': plantingDate,
          'farmSize': farmSize,
          'waterAvailability': waterAvailability,
          'weatherCondition': weatherCondition,
          'temperature': temperature,
          'humidity': humidity,
          'rainfallForecast': rainfallForecast,
          'windSpeed': windSpeed,
        }),
      ).timeout(const Duration(seconds: 45));

      if (response.statusCode == 200) {
        return response.body;
      }
    } catch (e) {
      if (kDebugMode) print('Error in AdvisoryRepository generateDailyGuidance: $e');
    }
    return '[]';
  }

  Future<String?> checkCropSuitability({
    required String cropName,
    required FarmModel farm,
    required String languageCode,
  }) async {
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
          'language': languageCode,
        }),
      ).timeout(const Duration(seconds: 45));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['text'];
      }
    } catch (e) {
      if (kDebugMode) print('Error in AdvisoryRepository checkCropSuitability: $e');
    }
    return null;
  }
}
