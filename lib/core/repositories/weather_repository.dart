import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../config/api_config.dart';
import '../../features/weather/data/models/weather_model.dart';
import '../services/location_service.dart';
import '../services/firestore_service.dart';

class _CachedWeatherEntry {
  final WeatherModel weather;
  final DateTime timestamp;
  _CachedWeatherEntry(this.weather, this.timestamp);
}

class WeatherRepository {
  static final WeatherRepository _instance = WeatherRepository._internal();
  factory WeatherRepository() => _instance;
  WeatherRepository._internal();

  final _firestoreService = FirestoreService();
  static final Map<String, _CachedWeatherEntry> _inMemoryCache = {};

  static WeatherModel? getLatestCachedWeather() {
    if (_inMemoryCache.isEmpty) return null;
    _CachedWeatherEntry? freshest;
    for (final entry in _inMemoryCache.values) {
      if (freshest == null || entry.timestamp.isAfter(freshest.timestamp)) {
        freshest = entry;
      }
    }
    return freshest?.weather;
  }

  Future<WeatherModel> getWeather(double lat, double lon, {String lang = 'en', String? farmName}) async {
    final String cacheKey = 'cached_weather_${lat.toStringAsFixed(2)}_${lon.toStringAsFixed(2)}';
    final String memKey = '${lat.toStringAsFixed(2)}_${lon.toStringAsFixed(2)}';

    // 1. Check in-memory cache
    if (_inMemoryCache.containsKey(memKey)) {
      final entry = _inMemoryCache[memKey]!;
      final age = DateTime.now().difference(entry.timestamp);
      if (age.inMinutes < 30) {
        debugPrint('[WeatherRepository] In-memory cache HIT. Returning cached weather.');
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
          debugPrint('[WeatherRepository] SharedPreferences cache HIT. Returning cached weather.');
          final weather = WeatherModel.fromJson(data);
          _inMemoryCache[memKey] = _CachedWeatherEntry(weather, DateTime.fromMillisecondsSinceEpoch(timestamp));
          return weather;
        }
      }
    } catch (e) {
      debugPrint('[WeatherRepository] SharedPreferences cache read error: $e');
    }

    // 3. Query Backend API
    try {
      debugPrint('[WeatherRepository] API request started via Backend Proxy');
      final token = await FirebaseAuth.instance.currentUser?.getIdToken();
      final url = '${ApiConfig.customAiBackendUrl}/api/v1/weather?lat=$lat&lon=$lon&lang=$lang';

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
      ).timeout(const Duration(seconds: 45));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final weather = WeatherModel.fromJson(data);
        debugPrint('[WeatherRepository] Successfully fetched and parsed weather from backend.');

        // Cache to Firestore in background
        _firestoreService.addData(
          collectionPath: 'weather_reports',
          data: {
            'lat': lat,
            'lon': lon,
            'current_data': data,
            'timestamp': DateTime.now().toIso8601String(),
          },
        ).then((_) => null, onError: (e) {
          debugPrint('[WeatherRepository] Firestore audit cache error: $e');
        });

        // Cache locally to SharedPreferences
        if (prefs != null) {
          try {
            final cacheData = {
              'timestamp': DateTime.now().millisecondsSinceEpoch,
              'data': weather.toJson(),
            };
            await prefs.setString(cacheKey, json.encode(cacheData));
          } catch (e) {
            debugPrint('[WeatherRepository] SharedPreferences cache write error: $e');
          }
        }

        _inMemoryCache[memKey] = _CachedWeatherEntry(weather, DateTime.now());
        return weather;
      } else {
        throw Exception('Backend returned error status code: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('[WeatherRepository] Error querying backend weather: $e');
      if (cachedStr != null) {
        try {
          final cachedObj = json.decode(cachedStr);
          final data = cachedObj['data'] as Map<String, dynamic>;
          debugPrint('[WeatherRepository] API request failed, falling back to SharedPreferences cache.');
          final weather = WeatherModel.fromJson(data);
          _inMemoryCache[memKey] = _CachedWeatherEntry(weather, DateTime.fromMillisecondsSinceEpoch(cachedObj['timestamp'] as int));
          return weather;
        } catch (ex) {
          debugPrint('[WeatherRepository] Failed SharedPreferences cache fallback: $ex');
        }
      }
      if (_inMemoryCache.containsKey(memKey)) {
        debugPrint('[WeatherRepository] Failed, falling back to expired in-memory cache.');
        return _inMemoryCache[memKey]!.weather;
      }
      final latest = getLatestCachedWeather();
      if (latest != null) {
        debugPrint('[WeatherRepository] Failed completely, falling back to latest cached weather.');
        return latest;
      }
      throw Exception('Weather service unavailable');
    }
  }

  Future<WeatherModel> getWeatherForLocation(String village, String district, String state, {String lang = 'en', String? farmName}) async {
    final String locationKey = '$village|$district|$state';

    // 1. Check in-memory cache
    if (_inMemoryCache.containsKey(locationKey)) {
      final entry = _inMemoryCache[locationKey]!;
      final age = DateTime.now().difference(entry.timestamp);
      if (age.inMinutes < 30) {
        debugPrint('[WeatherRepository] In-memory cache HIT for location: $locationKey.');
        return entry.weather;
      }
    }

    try {
      debugPrint('[WeatherRepository] Resolving coordinates for location: $village, $district, $state');
      final locationService = LocationService();
      final coords = await locationService.getLatLngFromAddress(village, district, state);
      
      if (coords != null) {
        final lat = coords['latitude']!;
        final lon = coords['longitude']!;
        final weather = await getWeather(lat, lon, lang: lang, farmName: farmName);
        _inMemoryCache[locationKey] = _CachedWeatherEntry(weather, DateTime.now());
        return weather;
      } else {
        // Fallback to Delhi coordinates if geocoding fails completely
        final weather = await getWeather(28.61, 77.20, lang: lang, farmName: farmName);
        return weather;
      }
    } catch (e) {
      if (_inMemoryCache.containsKey(locationKey)) {
        debugPrint('[WeatherRepository] Exception occurred, using expired in-memory cache.');
        return _inMemoryCache[locationKey]!.weather;
      }
      rethrow;
    }
  }
}
