import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/services/location_service.dart';
import '../../../../core/repositories/weather_repository.dart';
import '../../../../core/providers/language_provider.dart';
import '../../../../core/providers/farm_provider.dart';
import '../../data/models/weather_model.dart';

class WeeklyForecastScreen extends StatefulWidget {
  final WeatherModel weather;

  const WeeklyForecastScreen({super.key, required this.weather});

  @override
  State<WeeklyForecastScreen> createState() => _WeeklyForecastScreenState();
}

class _WeeklyForecastScreenState extends State<WeeklyForecastScreen> {
  late WeatherModel _weather;
  bool _isLoading = false;
  String? _error;
  final _weatherService = WeatherRepository();

  @override
  void initState() {
    super.initState();
    _weather = widget.weather;
  }

  Future<void> _refreshForecast() async {
    if (_isLoading) return;
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final farmProvider = context.read<FarmProvider>();
      final farm = farmProvider.selectedFarm;
      final lang = context.read<LanguageProvider>().currentLanguage;
      
      WeatherModel updatedWeather;
      if (farm != null) {
        if (farm.latitude != null && farm.longitude != null) {
          updatedWeather = await _weatherService.getWeather(
            farm.latitude!,
            farm.longitude!,
            lang: lang,
            farmName: farm.name,
          );
        } else {
          updatedWeather = await _weatherService.getWeatherForLocation(
            farm.village,
            farm.district,
            farm.state,
            lang: lang,
            farmName: farm.name,
          );
        }
      } else {
        final locationService = LocationService();
        final position = await locationService.getCurrentPosition();
        if (position != null) {
          updatedWeather = await _weatherService.getWeather(
            position.latitude,
            position.longitude,
            lang: lang,
          );
        } else {
          throw Exception('Location unavailable');
        }
      }

      if (!mounted) return;
      setState(() {
        _weather = updatedWeather;
        _error = null;
      });
    } catch (e) {
      debugPrint('[WeeklyForecast] Refresh failed: $e');
      if (!mounted) return;
      setState(() {
        _error = 'Live weather service unavailable. Displaying offline cache.';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Live weather service unavailable. Displaying offline cache.'.tr(context)),
          backgroundColor: AppColors.error,
          behavior: SnackBarBehavior.floating,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final forecast = _weather.forecast;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: AppColors.primary,
        iconTheme: const IconThemeData(color: Colors.white),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'Weekly Forecast'.tr(context),
          style: GoogleFonts.poppins(
            color: Colors.white,
            fontWeight: FontWeight.w600,
            fontSize: 18,
          ),
        ),
        actions: [
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  color: Colors.white,
                  strokeWidth: 2,
                ),
              ),
            )
          else
            IconButton(
              icon: const Icon(Icons.refresh_rounded, color: Colors.white),
              onPressed: _refreshForecast,
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refreshForecast,
        notificationPredicate: (notification) => kIsWeb ? defaultScrollNotificationPredicate(notification) : false,
        color: Colors.white,
        backgroundColor: AppColors.primary,
        child: forecast.isEmpty
            ? _buildEmptyState()
            : ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(AppDimensions.paddingLG),
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
                              _error!.tr(context),
                              style: GoogleFonts.poppins(
                                color: AppColors.error,
                                fontSize: 13,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ],
                      ),
                    )
                  else
                    Container(
                      width: double.infinity,
                      margin: const EdgeInsets.only(bottom: 16),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppColors.success.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: AppColors.success.withOpacity(0.5)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.check_circle_outline_rounded, color: AppColors.success, size: 20),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              '${'Location'.tr(context)}: ${_weather.cityName}'.tr(context),
                              style: GoogleFonts.poppins(
                                color: AppColors.success,
                                fontSize: 13,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  
                  Text(
                    '7-Day Agricultural Forecast'.tr(context),
                    style: GoogleFonts.poppins(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: theme.colorScheme.onSurface,
                    ),
                  ),
                  const SizedBox(height: 12),
                  
                  ...forecast.asMap().entries.map((entry) {
                    final index = entry.key;
                    final dayForecast = entry.value;
                    return ForecastDayCard(forecast: dayForecast)
                        .animate()
                        .fadeIn(delay: (index * 50).ms)
                        .moveY(begin: 10, end: 0, delay: (index * 50).ms);
                  }),
                  
                  const SizedBox(height: 24),
                  
                  // Agro-advisory note for weather conditions
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.primaryContainer,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.primary.withOpacity(0.2)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.info_rounded, color: AppColors.primaryDark),
                            const SizedBox(width: 8),
                            Text(
                              'Agricultural Notice'.tr(context),
                              style: GoogleFonts.poppins(
                                fontWeight: FontWeight.w700,
                                fontSize: 14,
                                color: AppColors.primaryDark,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Weather conditions directly impact pesticide application and irrigation schedules. Check rain probabilities before spraying.'.tr(context),
                          style: GoogleFonts.poppins(
                            fontSize: 12,
                            color: AppColors.primaryDark,
                            height: 1.4,
                          ),
                        ),
                      ],
                    ),
                  ).animate().fadeIn(delay: 400.ms),
                  
                  const SizedBox(height: 40),
                ],
              ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.cloud_off_rounded,
            size: 64,
            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.3),
          ),
          const SizedBox(height: 16),
          Text(
            'No forecast data available'.tr(context),
            style: GoogleFonts.poppins(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _refreshForecast,
            icon: const Icon(Icons.refresh_rounded),
            label: Text('Retry'.tr(context)),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class ForecastDayCard extends StatefulWidget {
  final ForecastModel forecast;

  const ForecastDayCard({super.key, required this.forecast});

  @override
  State<ForecastDayCard> createState() => _ForecastDayCardState();
}

class _ForecastDayCardState extends State<ForecastDayCard> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dateFormat = DateFormat('EEEE, MMM d');
    final dayName = dateFormat.format(widget.forecast.date);

    return GestureDetector(
      onTap: () {
        setState(() {
          _isExpanded = !_isExpanded;
        });
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: theme.cardColor,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: AppColors.divider),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.02),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          children: [
            Row(
              children: [
                // Left: Day name and Date
                Expanded(
                  flex: 3,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        dayName.tr(context),
                        style: GoogleFonts.poppins(
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                          color: theme.colorScheme.onSurface,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Text(
                        DateFormat('d MMMM').format(widget.forecast.date).tr(context),
                        style: GoogleFonts.poppins(
                          fontSize: 11,
                          color: theme.colorScheme.onSurface.withOpacity(0.6),
                        ),
                      ),
                    ],
                  ),
                ),
                // Center: Weather Icon and Label
                Expanded(
                  flex: 3,
                  child: Row(
                    children: [
                      _getWeatherIcon(widget.forecast.icon),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          widget.forecast.condition.tr(context),
                          style: GoogleFonts.poppins(
                            fontWeight: FontWeight.w500,
                            fontSize: 13,
                            color: theme.colorScheme.onSurface,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
                // Right: Min/Max temp & Expand chevron
                Expanded(
                  flex: 3,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      Text(
                        '${widget.forecast.maxTemp.toInt()}° / ${widget.forecast.minTemp.toInt()}°',
                        style: GoogleFonts.poppins(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                          color: theme.colorScheme.onSurface,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Icon(
                        _isExpanded ? Icons.keyboard_arrow_up_rounded : Icons.keyboard_arrow_down_rounded,
                        color: theme.colorScheme.onSurface.withOpacity(0.6),
                        size: 20,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            
            // Expandable details section
            AnimatedSize(
              duration: const Duration(milliseconds: 200),
              curve: Curves.easeInOut,
              child: _isExpanded
                  ? Padding(
                      padding: const EdgeInsets.only(top: 16.0),
                      child: Column(
                        children: [
                          const Divider(color: AppColors.divider),
                          const SizedBox(height: 8),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceAround,
                            children: [
                              _buildDetailMetric(
                                Icons.umbrella_rounded,
                                '${widget.forecast.rainChance.toInt()}%',
                                'Rain Prob.'.tr(context),
                                Colors.blue,
                              ),
                              _buildDetailMetric(
                                Icons.waves_rounded,
                                '${widget.forecast.humidity.toInt()}%',
                                'Humidity'.tr(context),
                                Colors.green,
                              ),
                              _buildDetailMetric(
                                Icons.air_rounded,
                                '${widget.forecast.windSpeed.toInt()} km/h',
                                'Wind Speed'.tr(context),
                                Colors.orange,
                              ),
                            ],
                          ),
                          if (widget.forecast.description.isNotEmpty) ...[
                            const SizedBox(height: 12),
                            Text(
                              '${'Description'.tr(context)}: ${widget.forecast.description}'.tr(context),
                              style: GoogleFonts.poppins(
                                fontSize: 11,
                                fontStyle: FontStyle.italic,
                                color: theme.colorScheme.onSurface.withOpacity(0.7),
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ],
                      ),
                    )
                  : const SizedBox.shrink(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailMetric(IconData icon, String value, String label, Color color) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color, size: 18),
        ),
        const SizedBox(height: 6),
        Text(
          value,
          style: GoogleFonts.poppins(
            fontWeight: FontWeight.w700,
            fontSize: 13,
            color: Theme.of(context).colorScheme.onSurface,
          ),
        ),
        Text(
          label,
          style: GoogleFonts.poppins(
            fontSize: 10,
            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
          ),
        ),
      ],
    );
  }

  Widget _getWeatherIcon(String iconCode) {
    IconData iconData = Icons.wb_sunny_rounded;
    Color iconColor = Colors.orange;

    if (iconCode.contains('01')) {
      iconData = Icons.wb_sunny_rounded;
      iconColor = Colors.orange;
    } else if (iconCode.contains('02') || iconCode.contains('03') || iconCode.contains('04')) {
      iconData = Icons.wb_cloudy_rounded;
      iconColor = Colors.blueGrey;
    } else if (iconCode.contains('09') || iconCode.contains('10')) {
      iconData = Icons.umbrella_rounded;
      iconColor = Colors.blue;
    } else if (iconCode.contains('11')) {
      iconData = Icons.thunderstorm_rounded;
      iconColor = Colors.deepPurple;
    } else if (iconCode.contains('13')) {
      iconData = Icons.ac_unit_rounded;
      iconColor = Colors.lightBlueAccent;
    } else if (iconCode.contains('50')) {
      iconData = Icons.cloud_queue_rounded;
      iconColor = Colors.grey;
    }

    return Icon(iconData, color: iconColor, size: 24);
  }
}
