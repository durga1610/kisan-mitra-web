import '../config/api_config.dart';
import '../../features/notifications/data/services/notification_service.dart';
import '../../features/notifications/data/models/km_notification_type.dart';
import 'package:flutter/foundation.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../features/weather/data/models/weather_model.dart';
import 'firestore_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

class WeatherService {
  final String baseUrl = 'https://api.openweathermap.org/data/2.5';
  final _firestoreService = FirestoreService();

  Future<String> _getApiKey() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      String key = prefs.getString('custom_openweather_api_key') ?? '';
      if (key.isEmpty || key == 'YOUR_OPENWEATHER_API_KEY') {
        return ApiConfig.openWeatherApiKey;
      }
      return key;
    } catch (e) {
      return ApiConfig.openWeatherApiKey;
    }
  }

  Future<WeatherModel> getWeather(double lat, double lon, {String lang = 'en'}) async {
    try {
      debugPrint('[Weather] API request started');
      final apiKey = await _getApiKey();
      final response = await http.get(
        Uri.parse('$baseUrl/weather?lat=$lat&lon=$lon&appid=$apiKey&units=metric&lang=$lang'),
      ).timeout(const Duration(seconds: 10));
      debugPrint('[Weather] API response received');

      if (response.statusCode == 200) {
        debugPrint('[Weather] Parsing started');
        final data = json.decode(response.body);
        final weather = WeatherModel.fromJson(data);
        debugPrint('[Weather] Parsing complete');
        
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
        

        // Trigger notification if weather is bad
        final condition = weather.condition.toLowerCase();
        if (condition.contains('rain') || condition.contains('storm') || condition.contains('thunder')) {
          // simple deduplication (only notify once per session for the same weather)
          final history = NotificationService().history;
          final alreadyNotified = history.any((n) => n.type == KmNotificationType.rain && DateTime.now().difference(n.timestamp).inHours < 4);
          if (!alreadyNotified) {
             NotificationService().triggerCustomNotification(
               title: 'Weather Alert',
               body: 'Drastic weather change detected: ${weather.condition}. Please take precautions for your crops.',
               type: KmNotificationType.rain,
               priority: 'High'
             );
          }
        }
        return weather;
      } else {
        throw Exception('Failed to load weather data (status: ${response.statusCode})');
      }
    } catch (e) {
      throw Exception('Failed to load weather data: $e');
    }
  }

  Future<WeatherModel> getWeatherForLocation(String district, String state, {String lang = 'en'}) async {
    try {
      final apiKey = await _getApiKey();
      final query = district.isNotEmpty ? '$district,IN' : '$state,IN';
      final encodedQuery = Uri.encodeComponent(query);
      
      final response = await http.get(
        Uri.parse('$baseUrl/weather?q=$encodedQuery&appid=$apiKey&units=metric&lang=$lang'),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return WeatherModel.fromJson(data);
      } else {
        // Fallback to state if district fails
        final encodedState = Uri.encodeComponent('$state,IN');
        final fallbackResponse = await http.get(
          Uri.parse('$baseUrl/weather?q=$encodedState&appid=$apiKey&units=metric&lang=$lang'),
        ).timeout(const Duration(seconds: 10));
        
        if (fallbackResponse.statusCode == 200) {
          final data = json.decode(fallbackResponse.body);
          return WeatherModel.fromJson(data);
        }
        throw Exception('Failed to load weather data (status: ${fallbackResponse.statusCode})');
      }
    } catch (e) {
      throw Exception('Failed to load weather data: $e');
    }
  }
}
