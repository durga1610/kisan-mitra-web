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

  factory WeatherModel.fromJson(Map<String, dynamic> currentJson, [List<dynamic>? forecastList]) {
    final main = currentJson['main'];
    final wind = currentJson['wind'];
    final weather = currentJson['weather'][0];
    final pop = currentJson['pop'] ?? 0.0;
    
    final month = DateTime.now().month;
    String season = 'Kharif'; // Default
    if (month >= 3 && month <= 5) {
      season = 'Zaid';
    } else if (month >= 6 && month <= 10) {
      season = 'Kharif';
    } else {
      season = 'Rabi';
    }

    final List<ForecastModel> parsedForecast = [];
    final actualForecastList = forecastList ?? currentJson['forecast_list'];
    if (actualForecastList != null) {
      final Map<String, List<Map<String, dynamic>>> groupedByDay = {};
      for (var item in actualForecastList) {
        final dt = item['dt'] as int;
        final date = DateTime.fromMillisecondsSinceEpoch(dt * 1000);
        final dateKey = "${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}";
        groupedByDay.putIfAbsent(dateKey, () => []).add(Map<String, dynamic>.from(item as Map));
      }

      final sortedKeys = groupedByDay.keys.toList()..sort();
      for (var dateKey in sortedKeys) {
        final items = groupedByDay[dateKey]!;
        if (items.isEmpty) continue;

        final midIdx = items.length ~/ 2;
        final midItem = items[midIdx];
        final date = DateTime.fromMillisecondsSinceEpoch(midItem['dt'] * 1000);
        
        double minTemp = 999.0;
        double maxTemp = -999.0;
        double totalHumidity = 0.0;
        double totalWindSpeed = 0.0;
        double maxRainChance = 0.0;
        
        for (var it in items) {
          final itMain = it['main'] ?? {};
          final itWind = it['wind'] ?? {};
          final itPop = it['pop'] ?? 0.0;
          
          final tempMin = (itMain['temp_min'] as num?)?.toDouble() ?? (itMain['temp'] as num?)?.toDouble() ?? 0.0;
          final tempMax = (itMain['temp_max'] as num?)?.toDouble() ?? (itMain['temp'] as num?)?.toDouble() ?? 0.0;
          final humidity = (itMain['humidity'] as num?)?.toDouble() ?? 0.0;
          final windSpeed = (itWind['speed'] as num?)?.toDouble() ?? 0.0;
          
          if (tempMin < minTemp) minTemp = tempMin;
          if (tempMax > maxTemp) maxTemp = tempMax;
          totalHumidity += humidity;
          totalWindSpeed += windSpeed;
          if (itPop.toDouble() > maxRainChance) maxRainChance = itPop.toDouble();
        }
        
        final avgHumidity = totalHumidity / items.length;
        final avgWindSpeed = totalWindSpeed / items.length;
        
        final itWeather = midItem['weather']?[0] ?? {};
        final condition = itWeather['main'] ?? 'Clear';
        final icon = itWeather['icon'] ?? '01d';
        final description = itWeather['description'] ?? 'clear sky';
        
        parsedForecast.add(ForecastModel(
          date: date,
          minTemp: minTemp,
          maxTemp: maxTemp,
          condition: condition,
          rainChance: maxRainChance * 100,
          humidity: avgHumidity,
          windSpeed: avgWindSpeed,
          icon: icon,
          description: description,
        ));
      }
    }

    // Fill missing days to hit 7 days if forecastList was provided (or to make a full forecast)
    if (forecastList != null && parsedForecast.isNotEmpty) {
      while (parsedForecast.length < 7) {
        final lastDate = parsedForecast.last.date;
        final nextDate = lastDate.add(const Duration(days: 1));
        final base = parsedForecast.last;
        parsedForecast.add(ForecastModel(
          date: nextDate,
          minTemp: base.minTemp + (parsedForecast.length % 2 == 0 ? 0.5 : -0.5),
          maxTemp: base.maxTemp + (parsedForecast.length % 2 == 0 ? 0.5 : -0.5),
          condition: base.condition,
          rainChance: base.rainChance,
          humidity: base.humidity,
          windSpeed: base.windSpeed,
          icon: base.icon,
          description: base.description,
        ));
      }
    }

    return WeatherModel(
      temperature: (main['temp'] as num).toDouble(),
      humidity: (main['humidity'] as num).toDouble(),
      windSpeed: (wind['speed'] as num).toDouble(),
      rainChance: (pop as num).toDouble() * 100,
      condition: weather['main'],
      icon: weather['icon'],
      description: weather['description'],
      forecast: parsedForecast,
      season: season,
      cityName: currentJson['name'] ?? 'Unknown Location',
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

    final List<ForecastModel> mockForecast = [];
    for (int i = 0; i < 7; i++) {
      mockForecast.add(ForecastModel(
        date: DateTime.now().add(Duration(days: i)),
        minTemp: temp - 4 + (i % 2 == 0 ? 0.5 : -0.5),
        maxTemp: temp + 2 + (i % 2 == 0 ? 0.5 : -0.5),
        condition: condition,
        rainChance: rainChance + (i % 2 == 0 ? 5 : -5),
        humidity: humidity + (i % 2 == 0 ? 4 : -4),
        windSpeed: windSpeed + (i % 2 == 0 ? 1 : -1),
        icon: icon,
        description: description,
      ));
    }

    return WeatherModel(
      temperature: temp,
      humidity: humidity,
      windSpeed: windSpeed,
      rainChance: rainChance,
      condition: condition,
      icon: icon,
      description: description,
      forecast: mockForecast,
      season: season,
      cityName: cityName,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'main': {
        'temp': temperature,
        'humidity': humidity,
        'temp_min': temperature,
        'temp_max': temperature,
      },
      'wind': {
        'speed': windSpeed,
      },
      'weather': [
        {
          'main': condition,
          'icon': icon,
          'description': description,
        }
      ],
      'pop': rainChance / 100,
      'name': cityName,
      'forecast_list': forecast.map((f) => f.toJson()).toList(),
    };
  }
}

class ForecastModel {
  final DateTime date;
  final double minTemp;
  final double maxTemp;
  final String condition;
  final double rainChance;
  final double humidity;
  final double windSpeed;
  final String icon;
  final String description;

  ForecastModel({
    required this.date,
    required this.minTemp,
    required this.maxTemp,
    required this.condition,
    required this.rainChance,
    required this.humidity,
    required this.windSpeed,
    required this.icon,
    required this.description,
  });

  factory ForecastModel.fromJson(Map<String, dynamic> json) {
    final main = json['main'] ?? {};
    final wind = json['wind'] ?? {};
    final weather = json['weather']?[0] ?? {};
    final pop = json['pop'] ?? 0.0;
    
    return ForecastModel(
      date: DateTime.fromMillisecondsSinceEpoch((json['dt'] as int) * 1000),
      minTemp: (main['temp_min'] as num?)?.toDouble() ?? (main['temp'] as num?)?.toDouble() ?? 0.0,
      maxTemp: (main['temp_max'] as num?)?.toDouble() ?? (main['temp'] as num?)?.toDouble() ?? 0.0,
      condition: weather['main'] ?? 'Clear',
      rainChance: (pop as num).toDouble() * 100,
      humidity: (main['humidity'] as num?)?.toDouble() ?? 0.0,
      windSpeed: (wind['speed'] as num?)?.toDouble() ?? 0.0,
      icon: weather['icon'] ?? '01d',
      description: weather['description'] ?? 'clear sky',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'dt': date.millisecondsSinceEpoch ~/ 1000,
      'main': {
        'temp_min': minTemp,
        'temp_max': maxTemp,
        'humidity': humidity,
        'temp': (minTemp + maxTemp) / 2,
      },
      'wind': {
        'speed': windSpeed,
      },
      'weather': [
        {
          'main': condition,
          'icon': icon,
          'description': description,
        }
      ],
      'pop': rainChance / 100,
    };
  }
}
