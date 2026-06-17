class WeatherModel {
  final double temperature;
  final double humidity;
  final double windSpeed;
  final double rainChance;
  final String condition;
  final String icon;
  final String description;
  final List<ForecastModel> forecast;
  final String season;
  final String cityName;

  WeatherModel({
    required this.temperature,
    required this.humidity,
    required this.windSpeed,
    required this.rainChance,
    required this.condition,
    required this.icon,
    required this.description,
    required this.forecast,
    required this.season,
    this.cityName = 'Unknown Location',
  });

  factory WeatherModel.fromJson(Map<String, dynamic> json) {
    // OpenWeather 2.5 API structure might vary slightly if it's 'current' or 'weather'
    // Usually it has 'main', 'wind', 'clouds', 'weather'
    final main = json['main'];
    final wind = json['wind'];
    final weather = json['weather'][0];
    final pop = json['pop'] ?? 0.0; // Probability of precipitation (usually in forecast)
    
    // Simple season detection based on month
    final month = DateTime.now().month;
    String season = 'Kharif'; // Default
    if (month >= 3 && month <= 5) {
      season = 'Zaid';
    } else if (month >= 6 && month <= 10) {
      season = 'Kharif';
    } else {
      season = 'Rabi';
    }

    return WeatherModel(
      temperature: (main['temp'] as num).toDouble(),
      humidity: (main['humidity'] as num).toDouble(),
      windSpeed: (wind['speed'] as num).toDouble(),
      rainChance: (pop as num).toDouble() * 100, // Convert to percentage
      condition: weather['main'],
      icon: weather['icon'],
      description: weather['description'],
      forecast: [], 
      season: season,
      cityName: json['name'] ?? 'Unknown Location',
    );
  }

  factory WeatherModel.mock({String cityName = 'Delhi'}) {
    final month = DateTime.now().month;
    String season = 'Kharif';
    double temp = 28.5;
    double humidity = 70.0;
    double windSpeed = 10.0;
    double rainChance = 30.0;
    String condition = 'Cloudy';
    String icon = '03d';
    String description = 'scattered clouds';

    if (month >= 3 && month <= 5) {
      season = 'Zaid';
      temp = 36.5;
      humidity = 40.0;
      windSpeed = 14.0;
      rainChance = 10.0;
      condition = 'Sunny';
      icon = '01d';
      description = 'clear sky';
    } else if (month >= 6 && month <= 10) {
      season = 'Kharif';
      temp = 29.0;
      humidity = 82.0;
      windSpeed = 16.0;
      rainChance = 75.0;
      condition = 'Rain';
      icon = '10d';
      description = 'moderate rain';
    } else {
      season = 'Rabi';
      temp = 18.0;
      humidity = 60.0;
      windSpeed = 8.0;
      rainChance = 5.0;
      condition = 'Partly Cloudy';
      icon = '02d';
      description = 'few clouds';
    }

    return WeatherModel(
      temperature: temp,
      humidity: humidity,
      windSpeed: windSpeed,
      rainChance: rainChance,
      condition: condition,
      icon: icon,
      description: description,
      forecast: [],
      season: season,
      cityName: cityName,
    );
  }
}

class ForecastModel {
  final DateTime date;
  final double temp;
  final String condition;

  ForecastModel({
    required this.date,
    required this.temp,
    required this.condition,
  });
}
