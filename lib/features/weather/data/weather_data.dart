import 'package:flutter/material.dart';

class DailyForecast {
  final DateTime date;
  final double minTemp;
  final double maxTemp;
  final String condition;
  final IconData icon;

  DailyForecast({
    required this.date,
    required this.minTemp,
    required this.maxTemp,
    required this.condition,
    required this.icon,
  });
}

class WeatherData {
  final String location;
  final double temperature;
  final String condition;
  final int humidity;
  final double windSpeed;
  final double rainChance;
  final String uvIndex;
  final List<DailyForecast> weeklyForecast;
  final List<String> recommendations;

  WeatherData({
    required this.location,
    required this.temperature,
    required this.condition,
    required this.humidity,
    required this.windSpeed,
    required this.rainChance,
    required this.uvIndex,
    required this.weeklyForecast,
    required this.recommendations,
  });

  static WeatherData getMockData() {
    return WeatherData(
      location: 'Pune, Maharashtra',
      temperature: 28.5,
      condition: 'Partly Cloudy',
      humidity: 72,
      windSpeed: 14.5,
      rainChance: 15.0,
      uvIndex: 'Moderate',
      recommendations: [
        'Ideal time for harvesting wheat as dry weather is expected.',
        'Avoid pesticide spraying for the next 24 hours due to moderate winds.',
        'Slight humidity increase might attract fungal growth; inspect leaves.',
        'Good day for soil moisture testing.'
      ],
      weeklyForecast: [
        DailyForecast(date: DateTime.now(), minTemp: 22, maxTemp: 30, condition: 'Sunny', icon: Icons.wb_sunny_rounded),
        DailyForecast(date: DateTime.now().add(const Duration(days: 1)), minTemp: 23, maxTemp: 31, condition: 'Cloudy', icon: Icons.cloud_rounded),
        DailyForecast(date: DateTime.now().add(const Duration(days: 2)), minTemp: 21, maxTemp: 29, condition: 'Rain', icon: Icons.umbrella_rounded),
        DailyForecast(date: DateTime.now().add(const Duration(days: 3)), minTemp: 20, maxTemp: 28, condition: 'Storm', icon: Icons.thunderstorm_rounded),
        DailyForecast(date: DateTime.now().add(const Duration(days: 4)), minTemp: 22, maxTemp: 30, condition: 'Sunny', icon: Icons.wb_sunny_rounded),
        DailyForecast(date: DateTime.now().add(const Duration(days: 5)), minTemp: 24, maxTemp: 32, condition: 'Hot', icon: Icons.wb_sunny_rounded),
        DailyForecast(date: DateTime.now().add(const Duration(days: 6)), minTemp: 23, maxTemp: 31, condition: 'Cloudy', icon: Icons.cloud_rounded),
      ],
    );
  }
}
