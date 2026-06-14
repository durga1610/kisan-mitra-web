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
    if (month >= 3 && month <= 6) {
      season = 'Zaid';
    } else if (month >= 7 && month <= 10) {
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

  factory WeatherModel.mock() {
    return WeatherModel(
      temperature: 28.5,
      humidity: 65,
      windSpeed: 12.0,
      rainChance: 20.0,
      condition: 'Sunny',
      icon: '01d',
      description: 'clear sky',
      forecast: [],
      season: 'Rabi',
      cityName: 'Delhi',
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
