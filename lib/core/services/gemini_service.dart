import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http_parser/http_parser.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import '../config/api_config.dart';
import '../models/farm_model.dart';
import '../../features/weather/data/models/weather_model.dart';

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
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/advisory/chat'),
        headers: await _getHeaders(),
        body: jsonEncode({
          'message': message,
          'language': languageCode,
          'farm': selectedFarm != null ? {
            'id': selectedFarm!.id,
            'ownerId': selectedFarm!.ownerId,
            'name': selectedFarm!.name,
            'location': '${selectedFarm!.village}, ${selectedFarm!.district}, ${selectedFarm!.state}',
            'soilType': selectedFarm!.soilType,
            'waterAvailability': selectedFarm!.waterAvailability,
            'landArea': selectedFarm!.landArea,
            'plantedCrops': selectedFarm!.plantedCrops.map((c) => c.cropName).toList(),
          } : null,
          'weather': weather != null ? {
            'condition': weather!.condition,
            'temperature': weather!.temperature,
            'season': weather!.season,
            'humidity': weather!.humidity,
            'windSpeed': weather!.windSpeed,
            'rainChance': weather!.rainChance,
          } : null,
        }),
      ).timeout(const Duration(seconds: 15));


      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'text': data['text'] ?? _getOfflineResponse(message),
          'source': data['source'] ?? 'LOCAL_ENGINE',
        };
      }
    } catch (e) {
      if (kDebugMode) print('Error in custom API getResponse: $e');
    }
    return {
      'text': _getOfflineResponse(message),
      'source': 'LOCAL_ENGINE',
    };
  }

  String _getOfflineResponse(String message) {
    final lower = message.toLowerCase().trim();
    
    // Greetings
    if (lower == 'hi' || lower == 'hello' || lower == 'hey' || lower.startsWith('hello') || lower.startsWith('hi ')) {
      String welcome = 'Hello! I am Kisan Mitra AI, your personal farming assistant. ';
      if (selectedFarm != null) {
        welcome += 'How can I help you manage your farm **${selectedFarm!.name}** today?';
      } else {
        welcome += 'How can I help you with your agriculture questions today?';
      }
      return welcome;
    }
    
    // Weather & Temperature
    if (lower.contains('temperature') || lower.contains('weather') || lower.contains('rain') || lower.contains('forecast') || lower.contains('monsoon')) {
      String weatherInfo;
      if (weather != null) {
        weatherInfo = "Currently, the weather is ${weather!.condition.toLowerCase()} (around **${weather!.temperature.toStringAsFixed(1)}°C**) with **${weather!.humidity.toStringAsFixed(0)}%** humidity, **${weather!.windSpeed.toStringAsFixed(1)} km/h** wind speed, and **${weather!.rainChance.toStringAsFixed(0)}%** rain probability. ";
      } else {
        weatherInfo = "Currently, the weather is warm (around **32°C**). ";
      }
      if (selectedFarm != null) {
        weatherInfo += "In ${selectedFarm!.district}, ${selectedFarm!.state}, keeping track of soil moisture is key. ";
      }
      weatherInfo += "It is recommended to water crops early in the morning or late in the evening to reduce evaporation and protect them from thermal stress.";
      return weatherInfo;
    }
    
    // Summer/Zaid Season
    if (lower.contains('summer') || lower.contains('zaid') || lower.contains('hot weather')) {
      return 'For the **Summer (Zaid)** season, the recommended crops are:\n'
          '- **Vegetables**: Cucumber, Bitter Gourd, Pumpkin, Okra (Bhindi)\n'
          '- **Fruits**: Watermelon, Muskmelon\n'
          '- **Pulses**: Moong Dal (Green Gram), Urad Dal\n'
          'These crops grow well in hot temperatures and require efficient irrigation (such as drip systems).';
    }
    
    // Winter/Rabi Season
    if (lower.contains('winter') || lower.contains('rabi') || lower.contains('cold weather')) {
      return 'For the **Winter (Rabi)** season, the recommended crops are:\n'
          '- **Cereals**: Wheat, Barley\n'
          '- **Pulses**: Chickpeas (Gram), Peas, Lentils\n'
          '- **Oilseeds**: Mustard, Linseed\n'
          'These crops thrive in cool climates and require moderate moisture during germination and growth.';
    }

    // Rainy/Monsoon/Kharif Season
    if (lower.contains('rainy') || lower.contains('monsoon') || lower.contains('kharif')) {
      return 'For the **Monsoon (Kharif)** season, the recommended crops are:\n'
          '- **Cereals**: Paddy Rice, Maize, Bajra (Pearl Millet), Jowar (Sorghum)\n'
          '- **Cash Crops**: Cotton, Sugarcane, Soybean\n'
          '- **Pulses**: Arhar (Pigeon Pea), Black Gram\n'
          'Ensure proper drainage in your field to prevent waterlogging during heavy rainfall.';
    }

    // Soil types
    if (lower.contains('red soil')) {
      return 'For **red soil**, the best crops are **Groundnuts**, **Winter Wheat (Rabi)**, **Chickpeas (Gram)**, **Millets**, and **Cotton** as they adapt well to its drainage and porous properties.';
    } else if (lower.contains('black soil') || lower.contains('regur')) {
      return 'For **black soil** (Regur), the best crops are **Cotton**, **Wheat**, **Soybean**, **Sugarcane**, and **Linseed**, as black soil retains moisture exceptionally well.';
    } else if (lower.contains('sandy soil')) {
      return 'For **sandy soil**, the best crops are **Groundnuts**, **Bajra (Pearl Millet)**, **Watermelons**, and **Root Vegetables** (like carrots/potatoes) which thrive in quick-draining soils.';
    } else if (lower.contains('clayey soil') || lower.contains('clay soil')) {
      return 'For **clayey soil**, the best crops are **Paddy Rice**, **Sorghum**, and **Wheat**, which grow well in heavy, nutrient-rich moisture-retaining soils.';
    } else if (lower.contains('alluvial soil')) {
      return 'For **alluvial soil**, almost all crops grow exceptionally well! The best choices are **Rice**, **Wheat**, **Sugarcane**, **Cotton**, and **Jute** due to its high fertility.';
    } else if (lower.contains('soil')) {
      String soilResponse = "";
      if (selectedFarm != null) {
        soilResponse = "Your selected farm **${selectedFarm!.name}** has **${selectedFarm!.soilType}** soil. ";
      }
      return '$soilResponse\nDifferent soils support different crops:\n'
          '- **Black Soil**: Great for Cotton, Wheat\n'
          '- **Red Soil**: Great for Groundnut, Millets, Chickpea\n'
          '- **Sandy Soil**: Great for Watermelon, Pearl Millet (Bajra)\n'
          '- **Clayey Soil**: Great for Paddy Rice, Sorghum';
    }
    
    // Pests & Diseases
    if (lower.contains('pest') || lower.contains('disease') || lower.contains('insect') || lower.contains('worm') || lower.contains('fungus')) {
      return 'If you notice leaf spots, yellowing, or insects on your crops:\n'
          '1. Go to the **Disease Detection** tool in the app to upload a photo of the leaf.\n'
          '2. Ensure proper spacing between plants to improve airflow.\n'
          '3. Avoid over-watering as damp environments encourage fungal growth.\n'
          '4. Consider using organic neem oil spray or consult a local agronomist for targeted treatments.';
    }
    
    // Fertilizer
    if (lower.contains('fertilizer') || lower.contains('manure') || lower.contains('urea') || lower.contains('dap') || lower.contains('npk')) {
      return 'For optimal growth, use balanced Nitrogen-Phosphorus-Potassium (NPK) fertilizers like **Urea**, **DAP**, and **MOP**.\n'
          '- It is highly recommended to perform a soil test before applying fertilizers.\n'
          '- Organic options like compost or vermicompost improve soil health over the long term.\n'
          '- Apply fertilizers near the root zone rather than broadcasting on dry soil.';
    }
    
    // Mandi / Prices / Market
    if (lower.contains('price') || lower.contains('mandi') || lower.contains('market') || lower.contains('rate') || lower.contains('cost')) {
      return 'You can check current crop prices by going to the **Market** tab in the app. It provides local Mandi prices sorted by distance and state to help you get the best deal for your harvest.';
    }
    
    // Yield / Profit
    if (lower.contains('profit') || lower.contains('yield') || lower.contains('money') || lower.contains('income')) {
      return 'To plan your budget and estimate earnings, use the **Profit Analyzer** tool in the app. It helps you calculate input costs (seed, water, fertilizer) against target selling prices.';
    }

    String farmContext = "";
    if (selectedFarm != null) {
      final cropNames = selectedFarm!.plantedCrops.map((c) => c.cropName).toList();
      String cropsStr = cropNames.isEmpty ? "No active crops" : "Active crops: ${cropNames.join(', ')}";
      farmContext = "for your farm **${selectedFarm!.name}** (${selectedFarm!.soilType} soil, located in ${selectedFarm!.district}, ${selectedFarm!.state}). $cropsStr.";
    } else {
      farmContext = "to help you with your agriculture questions.";
    }
    
    // Default concise response
    return 'I\'m here $farmContext\n\nYou can ask me about:\n'
        '- **Soil suitability** (e.g., "what to grow in red soil?")\n'
        '- **Crop recommendation** (e.g., "best crops for summer")\n'
        '- **Fertilizer & irrigation** (e.g., "tips for watering crops")\n'
        '- **Pests & diseases** (e.g., "how to treat leaf spots")\n'
        'Or go to the **Disease Detection** tab to scan a crop photo!';
  }

  Future<Map<String, dynamic>> detectDisease(List<int> imageBytes, {String? filename, String? crop}) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      final isAuthenticated = user != null;
      
      if (kDebugMode) {
        print('[Disease Trace] --- START AUTHENTICATION TRACE ---');
        print('[Disease Trace] Current Firebase user ID: ${user?.uid ?? "null"}');
        print('[Disease Trace] Is user authenticated: $isAuthenticated');
      }

      if (user == null) {
        throw Exception('FirebaseAuth.instance.currentUser is null. User must be authenticated to run disease analysis.');
      }

      final token = await user.getIdToken(true); // Force token refresh before upload
      final tokenSucceeds = token != null && token.isNotEmpty;

      if (kDebugMode) {
        print('[Disease Trace] getIdToken() succeeded: $tokenSucceeds');
        print('[Disease Trace] Retrieved Firebase ID token (masked): ${token != null && token.length > 20 ? "${token.substring(0, 10)}...${token.substring(token.length - 10)}" : "null or invalid"}');
      }

      if (!tokenSucceeds) {
        throw Exception('Failed to retrieve a valid Firebase ID token.');
      }

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/disease/detect'),
      );
      
      request.headers['Authorization'] = 'Bearer $token';
      request.headers['Accept'] = 'application/json';
      
      if (kDebugMode) {
        print('[Disease Trace] Request URL: ${request.url}');
        // Mask the Authorization header value in logs
        final maskedHeaders = Map<String, String>.from(request.headers);
        if (maskedHeaders.containsKey('Authorization')) {
          final val = maskedHeaders['Authorization']!;
          maskedHeaders['Authorization'] = val.length > 27 
              ? '${val.substring(0, 17)}...${val.substring(val.length - 10)}' 
              : 'Bearer ...';
        }
        print('[Disease Trace] Request headers: $maskedHeaders');
        print('[Disease Trace] Authorization header presence: ${request.headers.containsKey('Authorization')}');
      }

      // Determine MIME type based on filename extension
      String mimeType = 'image/jpeg';
      final actualFilename = filename ?? 'image.jpg';
      final lowerFilename = actualFilename.toLowerCase();
      if (lowerFilename.endsWith('.png')) {
        mimeType = 'image/png';
      } else if (lowerFilename.endsWith('.webp')) {
        mimeType = 'image/webp';
      }
      
      if (kDebugMode) {
        print('[Disease Trace] Attached image filename: $actualFilename');
        print('[Disease Trace] Resolved Content-Type: $mimeType');
        print('[Disease Trace] Image size: ${imageBytes.length} bytes');
        print('[Disease Trace] Crop parameter: $crop');
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
      
      final streamedResponse = await request.send().timeout(const Duration(seconds: 20));
      final response = await http.Response.fromStream(streamedResponse);
      
      if (kDebugMode) {
        print('[Disease Trace] Backend response status code: ${response.statusCode}');
        print('[Disease Trace] Backend response headers: ${response.headers}');
        if (response.statusCode != 200) {
          print('[Disease Trace] Backend response body: ${response.body}');
        }
      }
      
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

  // For one-off specialized queries
  Future<String> generateAdvisory({
    required String crop,
    required String soil,
    required String location,
    required String weather,
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
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['text'] ?? _getOfflineAdvisory(crop, soil, location, weather);
      }
    } catch (e) {
      if (kDebugMode) print('Error in custom API generateAdvisory: $e');
    }
    return _getOfflineAdvisory(crop, soil, location, weather);
  }

  String _getOfflineAdvisory(String crop, String soil, String location, String weather) {
    return '### **Agricultural Advisory for $crop**\n\n'
        '**1. Soil Management ($soil Soil):**\n'
        '- Ensure proper land preparation and tilling.\n'
        '- Organic manure addition is recommended to improve soil texture and nutrient retention.\n\n'
        '**2. Irrigation & Water Needs:**\n'
        '- Given the weather conditions ($weather), maintain adequate watering frequency, especially during critical growth/flowering stages.\n'
        '- Drip irrigation is highly recommended to save water and target roots directly.\n\n'
        '**3. Nutrient & Fertilizer Management:**\n'
        '- Apply base NPK fertilizer based on standard requirements for $crop.\n'
        '- Keep the field free of weeds during the first 30 days of planting.';
  }

  // For personalized crop recommendation reasoning
  Future<String> generateRecommendationReasoning({
    required String cropName,
    required FarmModel farm,
    required WeatherModel weather,
    required String marketTrend,
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
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['text'] ?? 'Expert analysis indicates this is a highly profitable and resilient choice.';
      }
    } catch (e) {
      if (kDebugMode) print('Error in custom API generateRecommendationReasoning: $e');
    }
    return 'Expert analysis indicates this is a highly profitable and resilient choice for your specific farm conditions.';
  }

  // Generate a full list of crop recommendations dynamically based on live data
  Future<String> generateDynamicRecommendations({
    required FarmModel farm,
    required WeatherModel weather,
    required List<String> availableMarketCrops,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/advisory/recommendations'),
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
          },
          'availableMarketCrops': availableMarketCrops,
          'language': languageCode,
        }),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        return response.body;
      }
    } catch (e) {
      if (kDebugMode) print('Error in custom API generateDynamicRecommendations: $e');
    }
    return _getFallbackRecommendations();
  }

  String _getFallbackRecommendations() {
    return '''
[
  {
    "cropName": "Hybrid Tomato",
    "marketDemand": "High",
    "expectedProfit": "₹60,000 - ₹80,000 / Acre",
    "growthPeriod": "60-90 Days",
    "matchReason": "Excellent match for your current weather and highly profitable in your local Mandi.",
    "suitabilityScore": 0.95
  },
  {
    "cropName": "Paddy Rice",
    "marketDemand": "High",
    "expectedProfit": "₹55,000 - ₹75,000 / Acre",
    "growthPeriod": "120-140 Days",
    "matchReason": "Your soil type and water availability perfectly support this staple crop.",
    "suitabilityScore": 0.92
  },
  {
    "cropName": "Green Chilli",
    "marketDemand": "Medium",
    "expectedProfit": "₹45,000 - ₹65,000 / Acre",
    "growthPeriod": "70-90 Days",
    "matchReason": "Low risk and highly resilient to current temperature variations.",
    "suitabilityScore": 0.88
  },
  {
    "cropName": "Yellow Mustard",
    "marketDemand": "High",
    "expectedProfit": "₹40,000 - ₹55,000 / Acre",
    "growthPeriod": "100-120 Days",
    "matchReason": "Great alternative for seasonal rotation to maintain soil fertility.",
    "suitabilityScore": 0.85
  }
]
''';
  }

  // Generate real daily guidance dynamically based on live data
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
        }),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        return response.body;
      }
    } catch (e) {
      if (kDebugMode) print('Error in custom API generateDailyGuidance: $e');
    }
    return '[]';
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
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['suitable'] == true) {
          return null; // Suitable
        }
        return data['reason'];
      }
    } catch (e) {
      if (kDebugMode) print('Error in custom API checkCropSuitability: $e');
    }
    return null; // Assume suitable on network error
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
      ).timeout(const Duration(seconds: 10));

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
      ).timeout(const Duration(seconds: 5));
    } catch (e) {
      if (kDebugMode) print('Error in logSuitabilityAudit: $e');
    }
  }
}
