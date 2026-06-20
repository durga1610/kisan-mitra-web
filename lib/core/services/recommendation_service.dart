import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../../features/crop_recommendation/data/recommendation_data.dart';
import '../../features/weather/data/models/weather_model.dart';
import '../models/farm_model.dart';
import 'gemini_service.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import '../config/api_config.dart';
import '../../features/market/data/services/market_service.dart';
import '../../features/market/data/models/market_price.dart';

class RecommendationService {
  // Maps our crop names to possible Mandi API commodity names
  static const Map<String, List<String>> _cropAliases = {
    'Paddy Rice': ['paddy', 'rice', 'paddy(common)', 'paddy(dhan)(common)'],
    'Tomato': ['tomato'],
    'Onion': ['onion'],
    'Potato': ['potato'],
    'Green Chilli': ['green chilli', 'chilli', 'chili', 'green chilly'],
    'Mango': ['mango'],
    'Maize': ['maize', 'corn'],
    'Sugarcane': ['sugarcane', 'gur(jaggery)', 'gur', 'jaggery'],
    'Organic Wheat': ['wheat'],
    'Hybrid Cotton': ['cotton', 'kapas'],
    'Yellow Mustard': ['mustard', 'rapeseed'],
    'Soybean': ['soybean', 'soyabean', 'soya'],
    'Banana': ['banana'],
    'Groundnut': ['groundnut', 'peanut'],
    'Turmeric': ['turmeric', 'haldi'],
  };

  static bool _cropMatchesMarket(String cropName, String marketCommodity) {
    final cropLower = cropName.toLowerCase();
    final marketLower = marketCommodity.toLowerCase();
    // Direct contains
    if (marketLower.contains(cropLower) || cropLower.contains(marketLower)) return true;
    // Alias match
    final aliases = _cropAliases[cropName];
    if (aliases != null) {
      return aliases.any((alias) => marketLower.contains(alias) || alias.contains(marketLower));
    }
    // Try reverse: check all aliases to find this market commodity
    for (final entry in _cropAliases.entries) {
      if (entry.value.any((a) => marketLower.contains(a))) {
        if (entry.key.toLowerCase() == cropLower) return true;
      }
    }
    return false;
  }

  static final Map<String, List<RecommendationModel>> _cache = {};
  static final Map<String, DateTime> _cacheTime = {};

  static Future<List<RecommendationModel>> getRecommendations({
    required FarmModel farm,
    required WeatherModel weather,
    String languageCode = 'en',
    bool forceRefresh = false,
  }) async {
    final cacheKey = '${farm.id ?? farm.name}_$languageCode';
    
    if (!forceRefresh && _cache.containsKey(cacheKey)) {
      final lastTime = _cacheTime[cacheKey];
      // Cache valid for 12 hours to keep it stable but fresh enough
      if (lastTime != null && DateTime.now().difference(lastTime).inHours < 12) {
        if (kDebugMode) print('Returning cached AI recommendations for $cacheKey');
        return _cache[cacheKey]!;
      }
    }

    // Fetch market prices for matching state
    List<MarketPrice> marketPrices = [];
    try {
      marketPrices = await MarketService().getMarketPrices(preferredState: farm.state) ?? [];
    } catch (e) {
      if (kDebugMode) print('Market fetch failed in recommendation service: $e');
    }

    final uniqueMarketCrops = marketPrices.map((p) => p.cropName).toSet().toList();
    
    // Leverage Gemini AI to dynamically analyze all factors and suggest crops
    final geminiService = GeminiService(selectedFarm: farm, languageCode: languageCode);
    final jsonResponse = await geminiService.generateDynamicRecommendations(
      farm: farm,
      weather: weather,
      availableMarketCrops: uniqueMarketCrops,
    );

    List<RecommendationModel> recommendations = [];
    
    try {
      // Clean up markdown in case the model ignored instructions
      var cleanJson = jsonResponse.replaceAll('```json', '').replaceAll('```', '').trim();
      final List<dynamic> parsedList = json.decode(cleanJson);
      
      for (var item in parsedList) {
        final cropName = item['cropName']?.toString() ?? 'Unknown Crop';
        
        // Pick an image dynamically or fallback to generic farm field
        String imageUrl = 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=500&auto=format&fit=crop';
        try {
          final extended = _getExtendedCropList().firstWhere(
             (c) => c.cropName.toLowerCase().contains(cropName.toLowerCase()) || cropName.toLowerCase().contains(c.cropName.toLowerCase())
          );
          imageUrl = extended.imageUrl;
        } catch (_) {}

        recommendations.add(
          RecommendationModel(
            cropName: cropName,
            imageUrl: imageUrl,
            marketDemand: item['marketDemand']?.toString() ?? 'Medium',
            demandScore: (item['suitabilityScore'] is num) ? (item['suitabilityScore'] as num).toDouble() : 0.8,
            expectedProfit: item['expectedProfit']?.toString() ?? 'Variable',
            suitableSoil: [farm.soilType],
            suitableRegions: [farm.state],
            growthPeriod: item['growthPeriod']?.toString() ?? '90-120 Days',
            matchReason: '🤖 AI: ${item['matchReason']?.toString() ?? 'Highly suitable based on live data.'}',
            suitabilityScore: (item['suitabilityScore'] is num) ? (item['suitabilityScore'] as num).toDouble() : 0.8,
            isLocallyCultivated: uniqueMarketCrops.any((c) => c.toLowerCase().contains(cropName.toLowerCase())),
            source: item['source'],
          )
        );
      }
    } catch (e) {
      if (kDebugMode) print('Failed to parse dynamic recommendations: $e. Falling back to local algorithm.');
      final fallback = _getExtendedCropList().take(3).toList();
      _cache[cacheKey] = fallback;
      _cacheTime[cacheKey] = DateTime.now();
      return fallback;
    }

    // Save to cache
    _cache[cacheKey] = recommendations;
    _cacheTime[cacheKey] = DateTime.now();

    return recommendations;
  }

  static Future<CustomCropAnalysisModel> analyzeCustomCrop({
    required String cropName,
    required FarmModel farm,
    required WeatherModel weather,
    String languageCode = 'en',
  }) async {
    try {
      final token = await FirebaseAuth.instance.currentUser?.getIdToken();
      final headers = {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };
      
      final response = await http.post(
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/crops/regional-suitability'),
        headers: headers,
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
            .where((r) => r.contains('Match'))
            .toList();
            
        if (warnings.isEmpty && positives.isEmpty) {
          positives.add('✅ Crop evaluated successfully.');
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
      }
    } catch (e) {
      if (kDebugMode) print('Regional suitability request failed: $e. Falling back to local scoring.');
    }

    final List<RecommendationModel> allCrops = _getExtendedCropList();
    final String season = weather.season;
    final double temp = weather.temperature;
    final String farmState = farm.state.toLowerCase();

    // Try to find the crop in our database
    final crop = allCrops.firstWhere(
      (c) => c.cropName.toLowerCase().contains(cropName.toLowerCase()),
      orElse: () => RecommendationModel(
        cropName: cropName,
        imageUrl: '',
        marketDemand: 'Unknown',
        demandScore: 0.5,
        expectedProfit: 'Variable',
        suitableSoil: ['Loamy', 'Alluvial'], // generic
        suitableRegions: [], // unknown
        growthPeriod: '90-120 Days',
        matchReason: '',
      ),
    );

    double score = 0.0;
    List<String> warnings = [];
    List<String> positives = [];

    // 1. Regional Suitability Match (40%)
    if (crop.suitableRegions.isEmpty) {
      warnings.add('⚠️ This crop is not typically cultivated in our database regions. Proceed with caution.');
    } else {
      bool regionMatch = crop.suitableRegions.any((r) => r.toLowerCase() == farmState);
      if (regionMatch) {
        score += 0.4;
        positives.add('✅ Highly cultivated in ${farm.state}.');
      } else {
        score -= 0.3;
        warnings.add('⚠️ Not typically cultivated in ${farm.state}. You might face supply chain or climate issues.');
      }
    }

    // 2. Soil Match (25%)
    bool soilMatch = crop.suitableSoil.any((s) => 
      farm.soilType.toLowerCase().contains(s.toLowerCase()) || 
      s.toLowerCase().contains(farm.soilType.toLowerCase()));
    if (soilMatch) {
      score += 0.25;
      positives.add('✅ Your ${farm.soilType} is an excellent match.');
    } else {
      warnings.add('⚠️ Soil mismatch. Needs ${crop.suitableSoil.join(", ")}, but you have ${farm.soilType}.');
    }

    // 3. Season Match (20%)
    bool seasonMatch = _isCropSuitableForSeason(cropName, season);
    if (seasonMatch) {
      score += 0.20;
      positives.add('✅ Perfect for the current $season season.');
    } else {
      warnings.add('⚠️ Not ideal for $season season. Yield might be affected.');
    }

    // 4. Temp Match (10%)
    double tempScore = _calculateTempScore(cropName, temp);
    score += tempScore * 0.10;
    if (tempScore > 0.8) {
      positives.add('✅ Thrives in current ${temp.toInt()}°C temperature.');
    } else {
      warnings.add('⚠️ Current ${temp.toInt()}°C temp is not optimal. Risk of heat/cold stress.');
    }

    // 5. Water Availability Match (5%)
    double waterScore = _calculateWaterScore(cropName, farm.waterAvailability);
    score += waterScore * 0.05;
    if (waterScore > 0.8) {
      positives.add('✅ Matches your ${farm.waterAvailability} water availability.');
    } else {
      warnings.add('⚠️ Your ${farm.waterAvailability} water availability might not be sufficient.');
    }

    // Determine Verdict
    String verdict;
    if (score >= 0.7) {
      verdict = 'Highly Recommended';
    } else if (score >= 0.4) {
      verdict = 'Feasible with Extra Care';
    } else {
      verdict = 'Not Recommended (High Risk)';
    }

    // Normalize score to 0-100%
    double finalScore = (score.clamp(0.0, 1.0)) * 100;

    return CustomCropAnalysisModel(
      cropName: crop.cropName,
      score: finalScore,
      warnings: warnings,
      positives: positives,
      verdict: verdict,
    );
  }

  static bool _isCropSuitableForSeason(String cropName, String season) {
    final Map<String, List<String>> seasonMap = {
      'Kharif': ['Rice', 'Paddy', 'Maize', 'Cotton', 'Soybean', 'Groundnut', 'Sugarcane', 'Turmeric', 'Chilli', 'Tomato', 'Banana'],
      'Rabi': ['Wheat', 'Mustard', 'Onion', 'Potato', 'Chilli', 'Mango', 'Tomato', 'Peas', 'Groundnut'],
      'Zaid': ['Watermelon', 'Cucumber', 'Maize', 'Sunflower', 'Mango', 'Tomato', 'Onion'],
    };
    
    final suitableCrops = seasonMap[season] ?? [];
    return suitableCrops.any((c) => cropName.toLowerCase().contains(c.toLowerCase()));
  }

  static double _calculateTempScore(String cropName, double temp) {
    final cn = cropName.toLowerCase();
    if (cn.contains('wheat')) return (temp > 10 && temp < 25) ? 1.0 : 0.5;
    if (cn.contains('rice') || cn.contains('paddy')) return (temp > 22 && temp < 35) ? 1.0 : 0.6;
    if (cn.contains('cotton')) return (temp > 25 && temp < 40) ? 1.0 : 0.4;
    if (cn.contains('tomato')) return (temp > 18 && temp < 35) ? 1.0 : 0.5;
    if (cn.contains('mango')) return (temp > 24 && temp < 38) ? 1.0 : 0.5;
    if (cn.contains('onion')) return (temp > 13 && temp < 30) ? 1.0 : 0.5;
    if (cn.contains('potato')) return (temp > 15 && temp < 25) ? 1.0 : 0.4;
    if (cn.contains('chilli')) return (temp > 20 && temp < 35) ? 1.0 : 0.5;
    if (cn.contains('maize')) return (temp > 21 && temp < 35) ? 1.0 : 0.5;
    if (cn.contains('sugarcane')) return (temp > 20 && temp < 38) ? 1.0 : 0.5;
    if (cn.contains('banana')) return (temp > 22 && temp < 35) ? 1.0 : 0.5;
    if (cn.contains('groundnut')) return (temp > 22 && temp < 35) ? 1.0 : 0.5;
    return 0.8;
  }

  static double _calculateWaterScore(String cropName, String availability) {
    bool isHigh = availability.contains('High');
    bool isLow = availability.contains('Low');
    final cn = cropName.toLowerCase();

    if (cn.contains('rice') || cn.contains('paddy') || cn.contains('sugarcane') || cn.contains('banana')) {
      return isHigh ? 1.0 : (isLow ? 0.2 : 0.6);
    }
    if (cn.contains('mustard') || cn.contains('cotton') || cn.contains('groundnut')) {
      return isLow ? 1.0 : 0.8;
    }
    if (cn.contains('tomato') || cn.contains('chilli') || cn.contains('onion') || cn.contains('potato')) {
      return isHigh ? 0.9 : (isLow ? 0.5 : 0.8);
    }
    if (cn.contains('mango')) {
      return isLow ? 0.9 : 0.8;
    }
    return 0.9;
  }

  static List<RecommendationModel> _getExtendedCropList() {
    return [
      // Crops commonly available in the Mandi API
      RecommendationModel(
        cropName: 'Paddy Rice',
        imageUrl: 'https://images.unsplash.com/photo-1536679545597-c2e5e1946495?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.92,
        expectedProfit: '₹60,000 - ₹75,000 / Acre',
        suitableSoil: ['Clayey', 'Alluvial', 'Peaty', 'Loamy'],
        suitableRegions: ['West Bengal', 'Uttar Pradesh', 'Punjab', 'Odisha', 'Andhra Pradesh', 'Telangana', 'Tamil Nadu', 'Bihar', 'Chhattisgarh', 'Karnataka'],
        growthPeriod: '130-145 Days',
        matchReason: 'High rainfall forecast aligns with irrigation needs.',
      ),
      RecommendationModel(
        cropName: 'Tomato',
        imageUrl: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.90,
        expectedProfit: '₹50,000 - ₹80,000 / Acre',
        suitableSoil: ['Loamy', 'Sandy Loam', 'Red', 'Black', 'Alluvial'],
        suitableRegions: ['Andhra Pradesh', 'Karnataka', 'Maharashtra', 'Madhya Pradesh', 'Tamil Nadu', 'Telangana', 'Gujarat', 'West Bengal', 'Odisha', 'Bihar'],
        growthPeriod: '60-90 Days',
        matchReason: 'Strong local market demand year-round.',
      ),
      RecommendationModel(
        cropName: 'Onion',
        imageUrl: 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.88,
        expectedProfit: '₹40,000 - ₹70,000 / Acre',
        suitableSoil: ['Loamy', 'Sandy Loam', 'Alluvial', 'Red'],
        suitableRegions: ['Maharashtra', 'Karnataka', 'Madhya Pradesh', 'Gujarat', 'Rajasthan', 'Andhra Pradesh', 'Tamil Nadu', 'Bihar', 'Haryana'],
        growthPeriod: '90-120 Days',
        matchReason: 'Consistent demand in domestic and export markets.',
      ),
      RecommendationModel(
        cropName: 'Mango',
        imageUrl: 'https://images.unsplash.com/photo-1553279768-865429fa0078?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.85,
        expectedProfit: '₹80,000 - ₹1,50,000 / Acre',
        suitableSoil: ['Alluvial', 'Laterite', 'Red', 'Loamy', 'Sandy Loam'],
        suitableRegions: ['Andhra Pradesh', 'Uttar Pradesh', 'Karnataka', 'Tamil Nadu', 'Telangana', 'Bihar', 'Gujarat', 'Maharashtra', 'West Bengal', 'Odisha'],
        growthPeriod: 'Perennial (Seasonal harvest)',
        matchReason: 'Premium seasonal fruit with high market value.',
      ),
      RecommendationModel(
        cropName: 'Green Chilli',
        imageUrl: 'https://images.unsplash.com/photo-1588252303782-cb80119abd6d?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.87,
        expectedProfit: '₹50,000 - ₹90,000 / Acre',
        suitableSoil: ['Loamy', 'Sandy Loam', 'Black', 'Red'],
        suitableRegions: ['Andhra Pradesh', 'Telangana', 'Karnataka', 'Maharashtra', 'Rajasthan', 'Tamil Nadu', 'Madhya Pradesh', 'Gujarat', 'West Bengal'],
        growthPeriod: '60-90 Days',
        matchReason: 'Evergreen demand in Indian cuisine.',
      ),
      RecommendationModel(
        cropName: 'Potato',
        imageUrl: 'https://images.unsplash.com/photo-1518977676601-b53f82ber83a?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.86,
        expectedProfit: '₹35,000 - ₹55,000 / Acre',
        suitableSoil: ['Sandy Loam', 'Loamy', 'Alluvial'],
        suitableRegions: ['Uttar Pradesh', 'West Bengal', 'Bihar', 'Gujarat', 'Madhya Pradesh', 'Punjab', 'Andhra Pradesh', 'Karnataka', 'Assam'],
        growthPeriod: '75-120 Days',
        matchReason: 'Staple crop with consistent year-round demand.',
      ),
      RecommendationModel(
        cropName: 'Maize',
        imageUrl: 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'Medium',
        demandScore: 0.80,
        expectedProfit: '₹30,000 - ₹45,000 / Acre',
        suitableSoil: ['Loamy', 'Sandy Loam', 'Alluvial', 'Red'],
        suitableRegions: ['Karnataka', 'Andhra Pradesh', 'Telangana', 'Rajasthan', 'Madhya Pradesh', 'Bihar', 'Maharashtra', 'Uttar Pradesh', 'Tamil Nadu'],
        growthPeriod: '80-110 Days',
        matchReason: 'Rising demand for poultry feed and starch industry.',
      ),
      RecommendationModel(
        cropName: 'Sugarcane',
        imageUrl: 'https://images.unsplash.com/photo-1612964936037-9f984c7e2b12?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.82,
        expectedProfit: '₹60,000 - ₹1,00,000 / Acre',
        suitableSoil: ['Alluvial', 'Loamy', 'Black', 'Clayey'],
        suitableRegions: ['Uttar Pradesh', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Andhra Pradesh', 'Gujarat', 'Bihar', 'Punjab', 'Haryana'],
        growthPeriod: '10-12 Months',
        matchReason: 'Government MSP support with jaggery demand.',
      ),
      RecommendationModel(
        cropName: 'Banana',
        imageUrl: 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.84,
        expectedProfit: '₹60,000 - ₹1,20,000 / Acre',
        suitableSoil: ['Loamy', 'Alluvial', 'Red', 'Sandy Loam'],
        suitableRegions: ['Tamil Nadu', 'Maharashtra', 'Gujarat', 'Andhra Pradesh', 'Karnataka', 'West Bengal', 'Bihar', 'Madhya Pradesh', 'Assam'],
        growthPeriod: '10-12 Months',
        matchReason: 'High calorie fruit with consistent domestic demand.',
      ),
      RecommendationModel(
        cropName: 'Groundnut',
        imageUrl: 'https://images.unsplash.com/photo-1567892320421-1c657571ea4a?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'Medium',
        demandScore: 0.78,
        expectedProfit: '₹35,000 - ₹50,000 / Acre',
        suitableSoil: ['Sandy Loam', 'Red', 'Loamy', 'Black'],
        suitableRegions: ['Gujarat', 'Andhra Pradesh', 'Tamil Nadu', 'Karnataka', 'Rajasthan', 'Maharashtra', 'Telangana', 'Madhya Pradesh'],
        growthPeriod: '100-130 Days',
        matchReason: 'Oil-seed crop with strong industrial demand.',
      ),
      RecommendationModel(
        cropName: 'Turmeric',
        imageUrl: 'https://images.unsplash.com/photo-1615485925600-97237c4fc1ec?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.89,
        expectedProfit: '₹80,000 - ₹1,30,000 / Acre',
        suitableSoil: ['Loamy', 'Alluvial', 'Red'],
        suitableRegions: ['Telangana', 'Andhra Pradesh', 'Tamil Nadu', 'Maharashtra', 'Karnataka', 'Odisha', 'West Bengal'],
        growthPeriod: '210-270 Days',
        matchReason: 'High commercial value and strong export demand.',
      ),
      // Traditional crops retained
      RecommendationModel(
        cropName: 'Organic Wheat',
        imageUrl: 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.95,
        expectedProfit: '₹45,000 - ₹55,000 / Acre',
        suitableSoil: ['Alluvial', 'Loamy', 'Black'],
        suitableRegions: ['Punjab', 'Haryana', 'Uttar Pradesh', 'Madhya Pradesh', 'Rajasthan', 'Bihar', 'Gujarat'],
        growthPeriod: '120-150 Days',
        matchReason: 'Perfect temperature and soil moisture levels for Rabi season.',
      ),
      RecommendationModel(
        cropName: 'Hybrid Cotton',
        imageUrl: 'https://images.unsplash.com/photo-1594900045543-3e110c2657e2?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.85,
        expectedProfit: '₹40,000 - ₹50,000 / Acre',
        suitableSoil: ['Black', 'Alluvial'],
        suitableRegions: ['Gujarat', 'Maharashtra', 'Telangana', 'Andhra Pradesh', 'Madhya Pradesh', 'Karnataka', 'Haryana', 'Rajasthan', 'Punjab'],
        growthPeriod: '160-180 Days',
        matchReason: 'Black soil is excellent for cotton retention.',
      ),
      RecommendationModel(
        cropName: 'Yellow Mustard',
        imageUrl: 'https://images.unsplash.com/photo-1599423956327-02422502697d?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'Medium',
        demandScore: 0.75,
        expectedProfit: '₹30,000 - ₹38,000 / Acre',
        suitableSoil: ['Loamy', 'Sandy', 'Alluvial'],
        suitableRegions: ['Rajasthan', 'Madhya Pradesh', 'Haryana', 'Uttar Pradesh', 'West Bengal', 'Gujarat', 'Assam'],
        growthPeriod: '110-120 Days',
        matchReason: 'Low water requirement makes it suitable for dry conditions.',
      ),
      RecommendationModel(
        cropName: 'Soybean',
        imageUrl: 'https://images.unsplash.com/photo-1550989460-0adf9ea622e2?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.88,
        expectedProfit: '₹35,000 - ₹45,000 / Acre',
        suitableSoil: ['Black', 'Loamy'],
        suitableRegions: ['Madhya Pradesh', 'Maharashtra', 'Rajasthan', 'Karnataka', 'Telangana', 'Chhattisgarh'],
        growthPeriod: '90-110 Days',
        matchReason: 'High market demand for oil extraction.',
      ),
    ];
  }
}
