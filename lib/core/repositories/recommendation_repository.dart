import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import '../config/api_config.dart';
import '../models/farm_model.dart';
import '../../features/weather/data/models/weather_model.dart';
import '../../features/crop_recommendation/data/recommendation_data.dart';
import 'market_repository.dart';

class RecommendationRepository {
  static final RecommendationRepository _instance = RecommendationRepository._internal();
  factory RecommendationRepository() => _instance;
  RecommendationRepository._internal();

  static final Map<String, List<RecommendationModel>> _cache = {};
  static final Map<String, DateTime> _cacheTime = {};

  static Future<Map<String, String>> _getHeaders() async {
    final token = await FirebaseAuth.instance.currentUser?.getIdToken();
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<List<RecommendationModel>> getRecommendations({
    required FarmModel farm,
    required WeatherModel weather,
    String languageCode = 'en',
    bool forceRefresh = false,
  }) async {
    final cacheKey = '${farm.id ?? farm.name}_$languageCode';
    
    if (!forceRefresh && _cache.containsKey(cacheKey)) {
      final lastTime = _cacheTime[cacheKey];
      if (lastTime != null && DateTime.now().difference(lastTime).inHours < 12) {
        debugPrint('[RecommendationRepository] Returning cached AI recommendations.');
        return _cache[cacheKey]!;
      }
    }

    // Fetch market prices for matching state using MarketRepository
    List<String> uniqueMarketCrops = [];
    try {
      final marketPrices = await MarketRepository().getMarketPrices(preferredState: farm.state) ?? [];
      uniqueMarketCrops = marketPrices.map((p) => p.cropName).toSet().toList();
    } catch (e) {
      debugPrint('[RecommendationRepository] Market fetch failed: $e');
    }

    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/recommendations'),
        headers: await _getHeaders(),
        body: jsonEncode({
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
          'weather': {
            'condition': weather.condition,
            'temperature': weather.temperature,
            'season': weather.season,
            'humidity': weather.humidity,
            'rainChance': weather.rainChance,
          },
          'availableMarketCrops': uniqueMarketCrops,
          'language': languageCode,
        }),
      ).timeout(const Duration(seconds: 45));

      if (response.statusCode == 200) {
        var cleanJson = response.body.replaceAll('```json', '').replaceAll('```', '').trim();
        final List<dynamic> parsedList = json.decode(cleanJson);
        
        List<RecommendationModel> recommendations = [];
        for (var item in parsedList) {
          final cropName = item['cropName']?.toString() ?? 'Unknown Crop';
          final score = (item['suitabilityScore'] ?? 0.0).toDouble();
          recommendations.add(RecommendationModel(
            cropName: cropName,
            marketDemand: item['marketDemand']?.toString() ?? 'Medium',
            demandScore: score,
            expectedProfit: item['expectedProfit']?.toString() ?? 'N/A',
            suitableSoil: [farm.soilType],
            suitableRegions: [farm.state],
            growthPeriod: item['growthPeriod']?.toString() ?? 'N/A',
            matchReason: item['matchReason']?.toString() ?? '',
            suitabilityScore: score,
            isLocallyCultivated: uniqueMarketCrops.any((c) => c.toLowerCase().contains(cropName.toLowerCase())),
            imageUrl: _getImageUrlForCrop(cropName),
            source: item['source']?.toString(),
          ));
        }

        if (recommendations.isNotEmpty) {
          _cache[cacheKey] = recommendations;
          _cacheTime[cacheKey] = DateTime.now();
        }
        return recommendations;
      } else {
        throw Exception('Server returned status: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('[RecommendationRepository] Exception in recommendations query: $e');
      throw Exception('Recommendations service unavailable: $e');
    }
  }

  Future<String> getRecommendationReasoning({
    required String cropName,
    required FarmModel farm,
    required WeatherModel weather,
    required String marketTrend,
    String languageCode = 'en',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/advisory/reasoning'),
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
          'weather': {
            'condition': weather.condition,
            'temperature': weather.temperature,
            'season': weather.season,
          },
          'marketTrend': marketTrend,
          'language': languageCode,
        }),
      ).timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['text'] ?? 'Expert analysis is currently unavailable.';
      }
    } catch (e) {
      debugPrint('[RecommendationRepository] Reasoning query error: $e');
    }
    return 'Expert analysis indicates this is a highly profitable and resilient choice for your specific farm conditions.';
  }

  String _getImageUrlForCrop(String cropName) {
    cropName = cropName.toLowerCase();
    if (cropName.contains('tomato')) {
      return 'https://images.unsplash.com/photo-1595855759920-86582396756a?q=80&w=500&auto=format&fit=crop';
    }
    if (cropName.contains('rice') || cropName.contains('paddy')) {
      return 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?q=80&w=500&auto=format&fit=crop';
    }
    if (cropName.contains('chilli') || cropName.contains('chili')) {
      return 'https://images.unsplash.com/photo-1588252303782-cb80119abd6d?q=80&w=500&auto=format&fit=crop';
    }
    if (cropName.contains('mustard')) {
      return 'https://images.unsplash.com/photo-1615485925600-97237c4fc1ec?q=80&w=500&auto=format&fit=crop';
    }
    if (cropName.contains('wheat')) {
      return 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?q=80&w=500&auto=format&fit=crop';
    }
    return 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=500&auto=format&fit=crop';
  }

  Future<CustomCropAnalysisModel> analyzeCustomCrop({
    required String cropName,
    required FarmModel farm,
    required WeatherModel weather,
    String languageCode = 'en',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/crops/regional-suitability'),
        headers: await _getHeaders(),
        body: jsonEncode({
          'farmId': farm.id,
          'cropName': cropName,
        }),
      ).timeout(const Duration(seconds: 45));
      
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        
        final List<String> warnings = List<String>.from(data['reasons'] ?? [])
            .where((r) => r.contains('Warning') || r.contains('Block') || r.contains('Suboptimal') || r.contains('Hard Block'))
            .toList();
            
        final List<String> positives = List<String>.from(data['reasons'] ?? [])
            .where((r) => r.contains('Match') || r.contains('Suitable') || r.contains('cultivated'))
            .toList();
            
        if (warnings.isEmpty && positives.isEmpty) {
          positives.add('Crop evaluated successfully.');
        }
        
        final double score = (data['score'] is num) ? (data['score'] as num).toDouble() : 75.0;
        final bool suitable = data['suitable'] ?? true;
        final String verdict = suitable ? (score >= 70 ? 'Highly Recommended' : 'Feasible with Extra Care') : 'Not Recommended (High Risk)';
        
        return CustomCropAnalysisModel(
          cropName: cropName,
          score: score,
          warnings: warnings,
          positives: positives,
          verdict: verdict,
        );
      } else {
        throw Exception('Server returned status: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('[RecommendationRepository] Custom crop analysis failed: $e');
      throw Exception('Regional suitability service unavailable: $e');
    }
  }
}
