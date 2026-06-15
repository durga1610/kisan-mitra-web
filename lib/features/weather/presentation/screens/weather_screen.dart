import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:intl/intl.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/services/location_service.dart';
import '../../../../core/services/weather_service.dart';
import '../../../../core/providers/language_provider.dart';
import '../../../../core/providers/farm_provider.dart';
import 'package:provider/provider.dart';
import 'package:geolocator/geolocator.dart';
import '../../data/models/weather_model.dart';

class WeatherScreen extends StatefulWidget {
  const WeatherScreen({super.key});

  @override
  State<WeatherScreen> createState() => _WeatherScreenState();
}

class _WeatherScreenState extends State<WeatherScreen> {
  final _locationService = LocationService();
  final _weatherService = WeatherService();
  
  bool _isLoading = true;
  String? _error;
  WeatherModel? _weather;
  String _locationName = 'Detecting location...';

  @override
  void initState() {
    super.initState();
    debugPrint('[Weather] Screen opened');
    _fetchWeather();
  }

  Future<void> _fetchWeather() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      Position? position;
      try {
        position = await _locationService.getCurrentPosition();
      } catch (e) {
        debugPrint('[Weather] Location service failed: $e');
      }
      
      if (!mounted) return;
      final lang = context.read<LanguageProvider>().currentLanguage;
      
      if (position != null) {
        final address = await _locationService.getAddressFromLatLng(position);
        final district = address['district'] ?? '';
        final state = address['state'] ?? '';
        
        if (!mounted) return;
        setState(() {
          if (district.isNotEmpty && state.isNotEmpty) {
            _locationName = '$district, $state';
          } else if (district.isNotEmpty || state.isNotEmpty) {
            _locationName = district.isNotEmpty ? district : state;
          } else {
            _locationName = 'Unknown Location';
          }
        });
        
        try {
          final data = await _weatherService.getWeather(position.latitude, position.longitude, lang: lang);
          if (!mounted) return;
          setState(() {
            _weather = data;
            if (_locationName == 'Unknown Location' && data.cityName != 'Unknown Location') {
              _locationName = data.cityName;
            }
          });
        } catch (apiErr) {
          debugPrint('[Weather] GPS Weather API failed: $apiErr');
          _setMockWeather(_locationName);
        }
        debugPrint('[Weather] UI updated via GPS');
      } else {
        // Fallback to Farm Profile State
        final farmState = context.read<FarmProvider>().selectedFarm?.state ?? '';
        final farmDistrict = context.read<FarmProvider>().selectedFarm?.district ?? '';
        String fallbackLocationName = 'Thiruvallur, Tamil Nadu'; // Default
        if (farmState.isNotEmpty) {
          fallbackLocationName = farmDistrict.isNotEmpty ? '$farmDistrict, $farmState' : farmState;
        }
        
        setState(() {
          _locationName = fallbackLocationName;
        });

        try {
          final data = await _weatherService.getWeatherForLocation(farmDistrict, farmState, lang: lang);
          if (!mounted) return;
          setState(() {
            _weather = data;
          });
          debugPrint('[Weather] UI updated via Farm State');
        } catch (apiErr) {
          debugPrint('[Weather] Location Weather API failed: $apiErr');
          _setMockWeather(_locationName);
        }
      }
    } catch (e) {
      if (!mounted) return;
      debugPrint('[Weather] Error: $e');
      _setMockWeather(_locationName);
    } finally {
      debugPrint('[Weather] Loading finished');
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _setMockWeather(String locationName) {
    final month = DateTime.now().month;
    String season = 'Kharif';
    double temp = 28.5;
    double humidity = 70.0;
    double windSpeed = 10.0;
    double rainChance = 30.0;
    String condition = 'Cloudy';
    String icon = '03d';
    String description = 'scattered clouds';

    if (month >= 3 && month <= 6) {
      season = 'Zaid';
      temp = 36.5;
      humidity = 40.0;
      windSpeed = 14.0;
      rainChance = 10.0;
      condition = 'Sunny';
      icon = '01d';
      description = 'clear sky';
    } else if (month >= 7 && month <= 10) {
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

    _weather = WeatherModel(
      temperature: temp,
      humidity: humidity,
      windSpeed: windSpeed,
      rainChance: rainChance,
      condition: condition,
      icon: icon,
      description: description,
      forecast: [],
      season: season,
      cityName: locationName,
    );
    _error = 'Using simulated weather data. Configure OPENWEATHER_API_KEY for live updates.';
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(color: AppColors.primary),
              const SizedBox(height: 16),
              Text('Loading weather...'.tr(context), style: GoogleFonts.poppins()),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      
      body: RefreshIndicator(
        onRefresh: _fetchWeather,
        color: Colors.white,
        child: CustomScrollView(
          slivers: [
            _buildAppBar(context, _locationName),
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(AppDimensions.paddingLG),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (_error != null)
                      Container(
                        width: double.infinity,
                        margin: const EdgeInsets.only(bottom: 16),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppColors.error.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppColors.error.withOpacity(0.5)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.cloud_off_rounded, color: AppColors.error, size: 20),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                _error!,
                                style: GoogleFonts.poppins(color: AppColors.error, fontSize: 13, fontWeight: FontWeight.w500),
                              ),
                            ),
                          ],
                        ),
                      ),
                    if (_weather != null) ...[
                      _buildMainWeatherCard(_weather!),
                      const SizedBox(height: 24),
                      _buildMetricsGrid(_weather!),
                      const SizedBox(height: 32),
                      _buildSectionTitle('Agricultural Outlook'),
                      const SizedBox(height: 16),
                      _buildRecommendations(_weather!.season),
                      const SizedBox(height: 40),
                    ] else ...[
                      Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const SizedBox(height: 40),
                            Icon(Icons.cloud_off_rounded, size: 64, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5)),
                            const SizedBox(height: 16),
                            Text("Weather data not available".tr(context), style: GoogleFonts.poppins(fontSize: 16)),
                            const SizedBox(height: 24),
                            ElevatedButton.icon(
                              onPressed: _fetchWeather,
                              icon: const Icon(Icons.refresh_rounded),
                              label: Text('Retry'.tr(context)),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppColors.primary,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ]
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppBar(BuildContext context, String location) {
    return SliverAppBar(
      backgroundColor: AppColors.primary,
      iconTheme: const IconThemeData(color: Colors.white),
      expandedHeight: 200,
      elevation: 0,
      title: Row(
        children: [
          const Icon(Icons.location_on_rounded, size: 18, color: Colors.white),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              location,
              style: GoogleFonts.poppins(fontSize: 15, fontWeight: FontWeight.w600, color: Colors.white),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
      leading: IconButton(
        icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white, size: 20),
        onPressed: () => Navigator.pop(context),
      ),
    );
  }

  Widget _buildMainWeatherCard(WeatherModel weather) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: AppColors.primaryGradient,
        borderRadius: BorderRadius.circular(30),
        boxShadow: [
          BoxShadow(color: Colors.white.withValues(alpha: 0.3), blurRadius: 20, offset: const Offset(0, 10)),
        ],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${weather.temperature.toInt()}°',
                    style: GoogleFonts.poppins(fontSize: 64, fontWeight: FontWeight.w700, color: Colors.white),
                  ),
                  Text(
                    weather.condition,
                    style: GoogleFonts.poppins(fontSize: 20, fontWeight: FontWeight.w500, color: Colors.white.withValues(alpha: 0.9)),
                  ),
                ],
              ),
              const Icon(Icons.wb_sunny_rounded, size: 100, color: Colors.white).animate(onPlay: (c) => c.repeat(reverse: true)).moveY(begin: -10, end: 10, duration: 2.seconds),
            ],
          ),
          const SizedBox(height: 24),
          Divider(color: Colors.white.withValues(alpha: 0.2)),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildSimpleInfo(Icons.water_drop_rounded, '${weather.rainChance.toInt()}%', 'Rain'),
              _buildSimpleInfo(Icons.air_rounded, '${weather.windSpeed.toInt()} km/h', 'Wind'),
              _buildSimpleInfo(Icons.eco_rounded, weather.season, 'Season'),
            ],
          ),
        ],
      ),
    ).animate().fadeIn().scale(delay: 100.ms);
  }

  Widget _buildSimpleInfo(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, color: Colors.white, size: 20),
        const SizedBox(height: 8),
        Text(value, style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white)),
        Text(label, style: GoogleFonts.poppins(fontSize: 11, color: Colors.white.withValues(alpha: 0.7))),
      ],
    );
  }

  Widget _buildMetricsGrid(WeatherModel weather) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 16,
      crossAxisSpacing: 16,
      childAspectRatio: 2.2,
      children: [
        _buildMetricCard('Humidity', '${weather.humidity.toInt()}%', Icons.waves_rounded, Colors.blue),
        _buildMetricCard('Wind Speed', '${weather.windSpeed.toInt()} km/h', Icons.air_rounded, Colors.orange),
        _buildMetricCard('Rain Chance', '${weather.rainChance.toInt()}%', Icons.umbrella_rounded, Colors.purple),
        _buildMetricCard('Season', weather.season, Icons.eco_outlined, Colors.green),
      ],
    );
  }

  Widget _buildMetricCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.divider),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: color.withValues(alpha: 0.1), shape: BoxShape.circle),
            child: Icon(icon, color: color, size: 18),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title, 
                  style: GoogleFonts.poppins(fontSize: 11, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  value, 
                  style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface),
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface),
    );
  }

  Widget _buildRecommendations(String season) {
    final tips = season == 'Kharif' 
      ? ['Focus on rice and cotton cultivation.', 'Ensure proper drainage for heavy rains.', 'Monitor for monsoon-related pests.']
      : season == 'Rabi'
      ? ['Ideal for wheat and mustard.', 'Manage irrigation for dry winter weather.', 'Watch for morning frost.']
      : ['Fast growing crops like moong and vegetables.', 'Intense irrigation required due to heat.', 'Protect soil from direct sun.'];

    return Column(
      children: tips.map((tip) {
        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.divider),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.eco_rounded, color: AppColors.primary, size: 18),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  tip,
                  style: GoogleFonts.poppins(fontSize: 13, color: Theme.of(context).colorScheme.onSurface, height: 1.4),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    ).animate().fadeIn(delay: 300.ms);
  }
}
