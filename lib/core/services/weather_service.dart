import '../config/api_config.dart';

import 'package:flutter/foundation.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../features/weather/data/models/weather_model.dart';
import 'firestore_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'location_service.dart';

class WeatherService {
  final String baseUrl = 'https://api.openweathermap.org/data/2.5';
  final _firestoreService = FirestoreService();

  Future<String> _getApiKey() async {
    try {
      // Priority 1: Check build-time injected key from environment variables
      if (ApiConfig.openWeatherApiKey.isNotEmpty && ApiConfig.openWeatherApiKey != 'YOUR_OPENWEATHER_API_KEY') {
        return ApiConfig.openWeatherApiKey;
      }
      
      // Priority 2: Check custom user settings key
      final prefs = await SharedPreferences.getInstance();
      String key = prefs.getString('custom_openweather_api_key') ?? '';
      if (key.isNotEmpty && key != 'YOUR_OPENWEATHER_API_KEY') {
        return key;
      }
      
      return ApiConfig.openWeatherApiKey;
    } catch (e) {
      return ApiConfig.openWeatherApiKey;
    }
  }

  Future<WeatherModel> getWeather(double lat, double lon, {String lang = 'en', String? farmName}) async {
    try {
      debugPrint('[Weather] API request started');
      final apiKey = await _getApiKey();
      final url = '$baseUrl/weather?lat=$lat&lon=$lon&appid=$apiKey&units=metric&lang=$lang';
      
      debugPrint('[Weather] Farm Name: ${farmName ?? 'N/A'}');
      debugPrint('[Weather] Latitude: $lat');
      debugPrint('[Weather] Longitude: $lon');
      debugPrint('[Weather] Loaded API Key Length: ${apiKey.length}');
      debugPrint('[Weather] Request URL: $url');
      
      final response = await http.get(
        Uri.parse(url),
      ).timeout(const Duration(seconds: 10));
      
      debugPrint('[Weather] Response Status Code: ${response.statusCode}');
      debugPrint('[Weather] Response Body: ${response.body}');

      if (response.statusCode == 200) {
        debugPrint('[Weather] Parsing started');
        final data = json.decode(response.body);
        final weather = WeatherModel.fromJson(data);
        debugPrint('[Weather] Parsing complete');
        
        debugPrint('[Weather] Temperature: ${weather.temperature}');
        debugPrint('[Weather] Humidity: ${weather.humidity}');
        debugPrint('[Weather] Wind Speed: ${weather.windSpeed}');
        debugPrint('[Weather] Rainfall: ${weather.rainChance}%');
        
        // Cache to Firestore without awaiting to prevent infinite hanging
        _firestoreService.addData(
          collectionPath: 'weather_reports',
          data: {
            'lat': lat,
            'lon': lon,
            'data': data,
            'timestamp': DateTime.now().toIso8601String(),
          },
        ).catchError((e) => debugPrint('[Weather] Firestore cache error: $e'));
        
        return weather;
      } else {
        throw Exception(jsonEncode({
          "status": "weather_unavailable",
          "message": "Live weather service unavailable"
        }));
      }
    } catch (e) {
      if (e is! Exception || !e.toString().contains('weather_unavailable')) {
        throw Exception(jsonEncode({
          "status": "weather_unavailable",
          "message": "Live weather service unavailable"
        }));
      }
      rethrow;
    }
  }

  Future<WeatherModel> getWeatherForLocation(String village, String district, String state, {String lang = 'en', String? farmName}) async {
    try {
      debugPrint('[Weather] Resolving coordinates for location: $village, $district, $state');
      final locationService = LocationService();
      final coords = await locationService.getLatLngFromAddress(village, district, state);
      
      if (coords != null) {
        final lat = coords['latitude']!;
        final lon = coords['longitude']!;
        debugPrint('[Weather] Location resolved to coordinates: $lat, $lon');
        return getWeather(lat, lon, lang: lang, farmName: farmName);
      } else {
        throw Exception(jsonEncode({
          "status": "weather_unavailable",
          "message": "Live weather service unavailable"
        }));
      }
    } catch (e) {
      if (e is! Exception || !e.toString().contains('weather_unavailable')) {
        throw Exception(jsonEncode({
          "status": "weather_unavailable",
          "message": "Live weather service unavailable"
        }));
      }
      rethrow;
    }
  }
}
