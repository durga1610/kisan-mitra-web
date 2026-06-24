import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../config/routes/app_router.dart';
import '../../../../core/providers/farm_provider.dart';
import '../../../../core/models/farm_model.dart';
import '../../../../core/services/gemini_service.dart';
import '../../../../core/providers/language_provider.dart';
import '../../data/assistant_data.dart';
import '../../../../core/repositories/weather_repository.dart';
import '../../../../features/weather/data/models/weather_model.dart';

class AIAssistantScreen extends StatefulWidget {
  const AIAssistantScreen({super.key});

  @override
  State<AIAssistantScreen> createState() => _AIAssistantScreenState();
}

class _AIAssistantScreenState extends State<AIAssistantScreen>
    with SingleTickerProviderStateMixin {
  int _selectedCropIndex = 0;
  late GeminiService _geminiService;
  bool _isInitialized = false;
  String? _lastFarmId;

  DailyAssistant? _assistant;
  bool _isLoading = false;
  WeatherModel? _weather;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final farmProvider = Provider.of<FarmProvider>(context);
    final farmId = farmProvider.selectedFarm?.id;
    if (!_isInitialized || _lastFarmId != farmId) {
      _isInitialized = true;
      _lastFarmId = farmId;
      final lang = Provider.of<LanguageProvider>(context, listen: false).currentLanguage;
      _geminiService = GeminiService(
          selectedFarm: farmProvider.selectedFarm, languageCode: lang);
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          _fetchAssistant();
        }
      });
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _fetchAssistant() async {
    final farmProvider = Provider.of<FarmProvider>(context, listen: false);
    final farm = farmProvider.selectedFarm;
    if (farm == null || farm.plantedCrops.isEmpty) return;

    if (_selectedCropIndex >= farm.plantedCrops.length) {
      _selectedCropIndex = 0;
    }
    final crop = farm.plantedCrops[_selectedCropIndex];
    final ageDays = DateTime.now()
        .difference(DateTime(crop.plantedDate.year, crop.plantedDate.month,
            crop.plantedDate.day))
        .inDays;

    setState(() {
      _isLoading = true;
      _assistant = null;
    });

    // Fetch weather
    WeatherModel? weather;
    try {
      final weatherRepository = WeatherRepository();
      final lang = Provider.of<LanguageProvider>(context, listen: false).currentLanguage;
      if (farm.latitude != null && farm.longitude != null) {
        weather = await weatherRepository.getWeather(
            farm.latitude!, farm.longitude!,
            lang: lang, farmName: farm.name);
      } else {
        weather = await weatherRepository.getWeatherForLocation(
            farm.village, farm.district, farm.state,
            lang: lang, farmName: farm.name);
      }
    } catch (e) {
      debugPrint('[AIAssistant] Weather fetch failed: $e');
    }

    if (weather == null) {
      weather = WeatherRepository.getLatestCachedWeather();
      if (weather != null) {
        debugPrint('[AIAssistant] Using latest cached weather as fallback: ${weather.cityName}');
      }
    }

    if (mounted) setState(() => _weather = weather);

    // Call backend
    final jsonStr = await _geminiService.generateDailyGuidance(
      cropName: crop.cropName,
      cropAgeDays: ageDays,
      state: farm.state,
      soilType: farm.soilType,
      plantingDate: crop.plantedDate.toIso8601String(),
      farmSize: farm.landArea,
      waterAvailability: farm.waterAvailability,
      weatherCondition: weather?.condition,
      temperature: weather?.temperature,
      humidity: weather?.humidity,
      rainfallForecast: weather?.rainChance,
      windSpeed: weather?.windSpeed,
    );

    if (mounted) {
      setState(() {
        try {
          final clean = jsonStr
              .replaceAll('```json', '')
              .replaceAll('```', '')
              .trim();
          if (clean.length > 5 && clean.startsWith('{')) {
            _assistant = AssistantData.parseDailyAssistant(clean);
          }
        } catch (_) {}
        _assistant ??= DailyAssistant.fallback(
            cropName: crop.cropName, ageDays: ageDays, weather: weather);
        _isLoading = false;
      });
    }
  }

  // ────────────────────────────────────────────────────────────────────────────
  // Build
  // ────────────────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    final farmProvider = Provider.of<FarmProvider>(context);
    final farm = farmProvider.selectedFarm;

    if (farm == null) {
      return _buildEmptyState(
        icon: Icons.grass_rounded,
        title: 'No field selected',
        subtitle: 'Please select or add a field to get AI guidance.',
      );
    }

    final plantedCrops = farm.plantedCrops;

    if (plantedCrops.isEmpty) {
      return _buildEmptyState(
        icon: Icons.eco_rounded,
        title: 'No crops planted yet',
        subtitle:
            'Plant a crop from recommendations to start getting AI guidance.',
        actionLabel: 'Go to Recommendations',
        onAction: () => context.push(AppRouter.cropRecommendation),
      );
    }

    if (_selectedCropIndex >= plantedCrops.length) {
      _selectedCropIndex = 0;
    }

    return Scaffold(
      appBar: AppBar(
        title: Text('AI Farming Assistant',
            style:
                GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Colors.white),
            onPressed: _fetchAssistant,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: Column(
        children: [
          _buildCropSelector(plantedCrops),
          if (_isLoading) _buildLoadingBar(),
          if (!_isLoading && _assistant != null) ...[
            _buildStatusBanner(_assistant!),
            _buildTabBar(),
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildScheduleTab(_assistant!),
                  _buildRecommendationsTab(_assistant!),
                  _buildAlertsTab(_assistant!),
                ],
              ),
            ),
          ],
          if (!_isLoading && _assistant == null)
            const Expanded(
              child: Center(
                child: Text('Loading assistant data...'),
              ),
            ),
        ],
      ),
    );
  }

  // ── Crop Selector ────────────────────────────────────────────────────────────

  Widget _buildCropSelector(List<PlantedCropModel> crops) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: AppColors.primary,
      child: Row(
        children: [
          const Icon(Icons.spa_outlined, color: Colors.white),
          const SizedBox(width: 12),
          Text('Active Crop:',
              style: GoogleFonts.poppins(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: Colors.white)),
          const SizedBox(width: 12),
          Expanded(
            child: DropdownButtonHideUnderline(
              child: DropdownButton<int>(
                value: _selectedCropIndex,
                icon: const Icon(Icons.arrow_drop_down, color: Colors.white),
                dropdownColor: AppColors.primaryDark,
                items: List.generate(crops.length, (index) {
                  return DropdownMenuItem<int>(
                    value: index,
                    child: Text(crops[index].cropName,
                        style: GoogleFonts.poppins(
                            fontWeight: FontWeight.w700,
                            fontSize: 15,
                            color: Colors.white)),
                  );
                }),
                onChanged: (val) {
                  if (val != null && val != _selectedCropIndex) {
                    setState(() => _selectedCropIndex = val);
                    _fetchAssistant();
                  }
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Loading Bar ──────────────────────────────────────────────────────────────

  Widget _buildLoadingBar() {
    return Expanded(
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(color: AppColors.primary),
            const SizedBox(height: 20),
            Text(
              'AI is analysing your crop & weather...',
              style: GoogleFonts.poppins(color: AppColors.textSecondary),
            ),
          ],
        ),
      ),
    );
  }

  // ── Status Banner ────────────────────────────────────────────────────────────

  Widget _buildStatusBanner(DailyAssistant a) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: const BoxDecoration(gradient: AppColors.primaryGradient),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      a.cropName,
                      style: GoogleFonts.poppins(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.white),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Day ${a.cropAgeDays}  •  ${a.currentStageName}',
                      style: GoogleFonts.poppins(
                          fontSize: 13,
                          color: Colors.white.withValues(alpha: 0.9)),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  DateFormat('d MMM').format(DateTime.now()),
                  style: GoogleFonts.poppins(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: Colors.white),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          // Weather pill
          Row(
            children: [
              const Icon(Icons.cloud_rounded, color: Colors.white70, size: 14),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  a.weatherSummary,
                  style: GoogleFonts.poppins(
                      fontSize: 12,
                      color: Colors.white.withValues(alpha: 0.85)),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              if (a.expectedHarvestDate.isNotEmpty) ...[
                const SizedBox(width: 12),
                const Icon(Icons.agriculture_rounded,
                    color: Colors.white70, size: 14),
                const SizedBox(width: 4),
                Text(
                  'Harvest: ${a.expectedHarvestDate}',
                  style: GoogleFonts.poppins(
                      fontSize: 11,
                      color: Colors.white.withValues(alpha: 0.85)),
                ),
              ],
            ],
          ),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms).slideY(begin: -0.05, end: 0);
  }

  // ── Tab Bar ──────────────────────────────────────────────────────────────────

  Widget _buildTabBar() {
    return Container(
      color: Colors.white,
      child: TabBar(
        controller: _tabController,
        indicatorColor: AppColors.primary,
        labelColor: AppColors.primary,
        unselectedLabelColor: AppColors.textSecondary,
        labelStyle:
            GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 13),
        unselectedLabelStyle:
            GoogleFonts.poppins(fontWeight: FontWeight.w500, fontSize: 13),
        tabs: const [
          Tab(text: 'Schedule', icon: Icon(Icons.schedule_rounded, size: 18)),
          Tab(text: 'AI Advice', icon: Icon(Icons.auto_awesome_rounded, size: 18)),
          Tab(text: 'Alerts', icon: Icon(Icons.notifications_active_rounded, size: 18)),
        ],
      ),
    );
  }

  // ── Schedule Tab ─────────────────────────────────────────────────────────────

  Widget _buildScheduleTab(DailyAssistant a) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppDimensions.paddingLG),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSlotCard(
            icon: Icons.wb_sunny_rounded,
            label: 'Morning',
            color: const Color(0xFFFF8F00),
            tasks: a.schedule.morning,
          ),
          const SizedBox(height: 16),
          _buildSlotCard(
            icon: Icons.wb_cloudy_rounded,
            label: 'Afternoon',
            color: const Color(0xFF0288D1),
            tasks: a.schedule.afternoon,
          ),
          const SizedBox(height: 16),
          _buildSlotCard(
            icon: Icons.nights_stay_rounded,
            label: 'Evening',
            color: const Color(0xFF5E35B1),
            tasks: a.schedule.evening,
          ),
        ],
      ),
    );
  }

  Widget _buildSlotCard({
    required IconData icon,
    required String label,
    required Color color,
    required List<String> tasks,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.25)),
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.08),
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(icon, color: color, size: 20),
                ),
                const SizedBox(width: 12),
                Text(
                  label,
                  style: GoogleFonts.poppins(
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      color: color),
                ),
              ],
            ),
          ),
          // Tasks
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: tasks.asMap().entries.map((entry) {
                final i = entry.key;
                final task = entry.value;
                return Padding(
                  padding: EdgeInsets.only(bottom: i < tasks.length - 1 ? 12 : 0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        margin: const EdgeInsets.only(top: 4, right: 12),
                        width: 20,
                        height: 20,
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: 0.1),
                          shape: BoxShape.circle,
                        ),
                        child: Center(
                          child: Text(
                            '${i + 1}',
                            style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: color),
                          ),
                        ),
                      ),
                      Expanded(
                        child: Text(
                          task,
                          style: GoogleFonts.poppins(
                              fontSize: 13,
                              height: 1.45,
                              color: AppColors.textSecondary),
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 350.ms).slideY(begin: 0.05, end: 0);
  }

  // ── Recommendations Tab ──────────────────────────────────────────────────────

  Widget _buildRecommendationsTab(DailyAssistant a) {
    return ListView.separated(
      padding: const EdgeInsets.all(AppDimensions.paddingLG),
      itemCount: a.recommendations.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        final rec = a.recommendations[index];
        return _buildRecommendationCard(rec, index);
      },
    );
  }

  Widget _buildRecommendationCard(AIRecommendation rec, int index) {
    final color = rec.typeColor;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: color.withValues(alpha: 0.25)),
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.06),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.10),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(rec.iconData, color: color, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        rec.title,
                        style: GoogleFonts.poppins(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: AppColors.textPrimary),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: color.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        rec.type.toUpperCase(),
                        style: TextStyle(
                            fontSize: 9,
                            fontWeight: FontWeight.w800,
                            color: color,
                            letterSpacing: 0.5),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  rec.detail,
                  style: GoogleFonts.poppins(
                      fontSize: 13,
                      height: 1.45,
                      color: AppColors.textSecondary),
                ),
              ],
            ),
          ),
        ],
      ),
    )
        .animate(delay: (index * 60).ms)
        .fadeIn(duration: 300.ms)
        .slideX(begin: 0.05, end: 0);
  }

  // ── Alerts Tab ───────────────────────────────────────────────────────────────

  Widget _buildAlertsTab(DailyAssistant a) {
    return ListView.separated(
      padding: const EdgeInsets.all(AppDimensions.paddingLG),
      itemCount: a.alerts.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        final alert = a.alerts[index];
        return _buildAlertCard(alert, index);
      },
    );
  }

  Widget _buildAlertCard(DailyAlert alert, int index) {
    final color = alert.levelColor;
    final bg = alert.levelBg;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: Icon(alert.iconData, color: color, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: color.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        alert.level.toUpperCase(),
                        style: TextStyle(
                            fontSize: 9,
                            fontWeight: FontWeight.w800,
                            color: color,
                            letterSpacing: 0.5),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  alert.message,
                  style: GoogleFonts.poppins(
                      fontSize: 13.5,
                      height: 1.45,
                      fontWeight: FontWeight.w500,
                      color: color.withValues(alpha: 0.85)),
                ),
              ],
            ),
          ),
        ],
      ),
    )
        .animate(delay: (index * 60).ms)
        .fadeIn(duration: 300.ms)
        .slideY(begin: 0.05, end: 0);
  }

  // ── Empty State ──────────────────────────────────────────────────────────────

  Widget _buildEmptyState({
    required IconData icon,
    required String title,
    required String subtitle,
    String? actionLabel,
    VoidCallback? onAction,
  }) {
    return Scaffold(
      appBar: AppBar(
        title: Text('AI Farming Assistant',
            style: GoogleFonts.poppins(
                fontWeight: FontWeight.w700, fontSize: 18)),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 64, color: AppColors.primary.withValues(alpha: 0.5)),
              const SizedBox(height: 16),
              Text(title,
                  style: GoogleFonts.poppins(
                      fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(subtitle,
                  style: GoogleFonts.poppins(
                      color: AppColors.textSecondary),
                  textAlign: TextAlign.center),
              if (actionLabel != null && onAction != null) ...[
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: onAction,
                  icon: const Icon(Icons.add_circle_outline_rounded),
                  label: Text(actionLabel.tr(context)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 24, vertical: 14),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16)),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
