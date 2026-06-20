import '../config/api_config.dart';

import 'package:flutter/foundation.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../features/weather/data/models/weather_model.dart';
import 'firestore_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'location_service.dart';

class _CachedWeatherEntry {
  final WeatherModel weather;
  final DateTime timestamp;
  _CachedWeatherEntry(this.weather, this.timestamp);
}

class WeatherService {
  final String baseUrl = 'https://api.openweathermap.org/data/2.5';
  final _firestoreService = FirestoreService();

  static final Map<String, _CachedWeatherEntry> _inMemoryCache = {};

  Future<String> _getApiKey() async {
    try {
      // Alignment 1: Check build-time injected key from environment variables
      if (ApiConfig.openWeatherApiKey.isNotEmpty && ApiConfig.openWeatherApiKey != 'YOUR_OPENWEATHER_API_KEY') {
        return ApiConfig.openWeatherApiKey;
      }
      
      // Alignment 2: Check custom user settings key
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
    final String cacheKey = 'cached_weather_${lat.toStringAsFixed(2)}_${lon.toStringAsFixed(2)}';
    final String memKey = '${lat.toStringAsFixed(2)}_${lon.toStringAsFixed(2)}';

    // 1. Check in-memory cache first
    if (_inMemoryCache.containsKey(memKey)) {
      final entry = _inMemoryCache[memKey]!;
      final age = DateTime.now().difference(entry.timestamp);
      if (age.inMinutes < 30) {
        debugPrint('[Weather] In-memory cache HIT and valid. Returning cached weather.');
        return entry.weather;
      }
    }

    // 2. Check SharedPreferences cache
    SharedPreferences? prefs;
    String? cachedStr;
    try {
      prefs = await SharedPreferences.getInstance();
      cachedStr = prefs.getString(cacheKey);
      if (cachedStr != null) {
        final cachedObj = json.decode(cachedStr);
        final timestamp = cachedObj['timestamp'] as int;
        final data = cachedObj['data'] as Map<String, dynamic>;
        final age = DateTime.now().millisecondsSinceEpoch - timestamp;
        if (age < 30 * 60 * 1000) {
          debugPrint('[Weather] Cache HIT and valid. Returning cached weather.');
          final weather = WeatherModel.fromJson(data);
          _inMemoryCache[memKey] = _CachedWeatherEntry(weather, DateTime.fromMillisecondsSinceEpoch(timestamp));
          return weather;
        }
      }
    } catch (e) {
      debugPrint('[Weather] SharedPreferences cache read error: $e');
    }

    try {
      debugPrint('[Weather] API request started');
      final apiKey = await _getApiKey();
      if (apiKey == 'YOUR_OPENWEATHER_API_KEY' || apiKey.trim().isEmpty) {
        debugPrint('[Weather] Placeholder API Key detected. Returning mock weather data.');
        String cityName = farmName ?? 'Chembarambakam, Tiruvallur';
        if (farmName == null || farmName.isEmpty) {
          try {
            final url = Uri.parse('https://nominatim.openstreetmap.org/reverse?format=json&lat=$lat&lon=$lon&zoom=18&addressdetails=1');
            final response = await http.get(url, headers: {
              'User-Agent': 'KisanMitraApp/1.0',
            }).timeout(const Duration(seconds: 3));
            if (response.statusCode == 200) {
              final data = json.decode(response.body);
              final address = data['address'] as Map<String, dynamic>?;
              if (address != null) {
                final village = address['village'] ?? address['suburb'] ?? address['town'] ?? address['city'] ?? '';
                final district = address['state_district'] ?? address['county'] ?? address['city_district'] ?? '';
                if (village.isNotEmpty && district.isNotEmpty) {
                  cityName = '$village, $district';
                } else if (district.isNotEmpty) {
                  cityName = district;
                }
              }
            }
          } catch (e) {
            debugPrint('[Weather] Reverse geocoding failed: $e');
          }
        }
        final weather = WeatherModel.mock(cityName: cityName);
        _inMemoryCache[memKey] = _CachedWeatherEntry(weather, DateTime.now());
        return weather;
      }
      final urlWeather = '$baseUrl/weather?lat=$lat&lon=$lon&appid=$apiKey&units=metric&lang=$lang';
      final urlForecast = '$baseUrl/forecast?lat=$lat&lon=$lon&appid=$apiKey&units=metric&lang=$lang';
      
      debugPrint('[Weather] Farm Name: ${farmName ?? 'N/A'}');
      debugPrint('[Weather] Latitude: $lat');
      debugPrint('[Weather] Longitude: $lon');
      debugPrint('[Weather] Loaded API Key Length: ${apiKey.length}');
      debugPrint('[Weather] Current Weather URL: $urlWeather');
      debugPrint('[Weather] Forecast URL: $urlForecast');
      
      final responses = await Future.wait([
        http.get(Uri.parse(urlWeather)).timeout(const Duration(seconds: 45)),
        http.get(Uri.parse(urlForecast)).timeout(const Duration(seconds: 45)),
      ]);
      
      final weatherResponse = responses[0];
      final forecastResponse = responses[1];
      
      debugPrint('[Weather] Weather Status Code: ${weatherResponse.statusCode}');
      debugPrint('[Weather] Forecast Status Code: ${forecastResponse.statusCode}');

      if (weatherResponse.statusCode == 200 && forecastResponse.statusCode == 200) {
        debugPrint('[Weather] Parsing started');
        final currentData = json.decode(weatherResponse.body);
        final forecastData = json.decode(forecastResponse.body);
        final forecastList = forecastData['list'] as List<dynamic>;
        
        final weather = WeatherModel.fromJson(currentData, forecastList);
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
            'current_data': currentData,
            'forecast_data': forecastData,
            'timestamp': DateTime.now().toIso8601String(),
          },
        ).then((_) => null, onError: (e) {
          debugPrint('[Weather] Firestore cache error: $e');
        });
        
        // Cache locally to SharedPreferences
        if (prefs != null) {
          try {
            final cacheData = {
              'timestamp': DateTime.now().millisecondsSinceEpoch,
              'data': weather.toJson(),
            };
            await prefs.setString(cacheKey, json.encode(cacheData));
            debugPrint('[Weather] Successfully saved to SharedPreferences cache.');
          } catch (e) {
            debugPrint('[Weather] SharedPreferences cache write error: $e');
          }
        }
        
        _inMemoryCache[memKey] = _CachedWeatherEntry(weather, DateTime.now());
        return weather;
      } else {
        throw Exception(jsonEncode({
          "status": "weather_unavailable",
          "message": "Live weather service unavailable"
        }));
      }
    } catch (e) {
      debugPrint('[Weather] Exception occurred: $e');
      if (cachedStr != null) {
        try {
          final cachedObj = json.decode(cachedStr);
          final data = cachedObj['data'] as Map<String, dynamic>;
          debugPrint('[Weather] API request failed, falling back to cached weather: $e');
          final weather = WeatherModel.fromJson(data);
          _inMemoryCache[memKey] = _CachedWeatherEntry(weather, DateTime.fromMillisecondsSinceEpoch(cachedObj['timestamp'] as int));
          return weather;
        } catch (ex) {
          debugPrint('[Weather] Failed to fall back to cache: $ex');
        }
      }
      if (_inMemoryCache.containsKey(memKey)) {
        debugPrint('[Weather] Failed, falling back to expired in-memory cache.');
        return _inMemoryCache[memKey]!.weather;
      }
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
    final String locationKey = '$village|$district|$state';

    // 1. Check in-memory cache
    if (_inMemoryCache.containsKey(locationKey)) {
      final entry = _inMemoryCache[locationKey]!;
      final age = DateTime.now().difference(entry.timestamp);
      if (age.inMinutes < 30) {
        debugPrint('[Weather] In-memory cache HIT for location: $locationKey. Returning cached weather.');
        return entry.weather;
      }
    }

    try {
      debugPrint('[Weather] Resolving coordinates for location: $village, $district, $state');
      final locationService = LocationService();
      final coords = await locationService.getLatLngFromAddress(village, district, state);
      
      if (coords != null) {
        final lat = coords['latitude']!;
        final lon = coords['longitude']!;
        debugPrint('[Weather] Location resolved to coordinates: $lat, $lon');
        final weather = await getWeather(lat, lon, lang: lang, farmName: farmName);
        _inMemoryCache[locationKey] = _CachedWeatherEntry(weather, DateTime.now());
        return weather;
      } else {
        if (_inMemoryCache.containsKey(locationKey)) {
          debugPrint('[Weather] Address resolution failed, using expired in-memory cache.');
          return _inMemoryCache[locationKey]!.weather;
        }
        throw Exception(jsonEncode({
          "status": "weather_unavailable",
          "message": "Live weather service unavailable"
        }));
      }
    } catch (e) {
      if (_inMemoryCache.containsKey(locationKey)) {
        debugPrint('[Weather] Exception occurred, using expired in-memory cache.');
        return _inMemoryCache[locationKey]!.weather;
      }
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
