import 'dart:async';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_strings.dart';
import '../../../../core/utils/app_utils.dart';
import '../../../../core/localization/app_translations.dart';
import '../../../../config/routes/app_router.dart';
import '../widgets/dashboard_header.dart';
import '../widgets/weather_card.dart';
import '../widgets/quick_actions_grid.dart';
import '../widgets/market_prices_card.dart';
import '../widgets/alerts_card.dart';
import '../widgets/home_bottom_nav.dart';

import 'package:provider/provider.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/providers/farm_provider.dart';
import '../../../../core/providers/language_provider.dart';
import '../../../../core/services/firestore_service.dart';
import '../../../../core/services/location_service.dart';
import '../../../../core/services/weather_service.dart';
import '../../../weather/data/models/weather_model.dart';
import '../../../../core/models/farm_model.dart';
import '../../../../core/providers/user_provider.dart';


class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  final _firestoreService = FirestoreService();
  final _locationService = LocationService();
  final _weatherService = WeatherService();

  bool _isLoading = true;
  String? _error;
  WeatherModel? _weatherData;
  String _currentLocationName = 'Detecting location...';
  String? _lastFetchedFarmId;
  double? _lastFetchedLat;
  double? _lastFetchedLon;
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    _loadInitialData();
    _startAutoRefresh();
  }




  void _startAutoRefresh() {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(const Duration(minutes: 30), (timer) {
      _loadInitialData();
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadInitialData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final user = authProvider.user;

      if (user == null) {
        throw Exception('User not logged in');
      }
    } catch (e) {
      _error = 'Failed to load data: $e';
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _fetchWeatherForFarm(FarmModel? farm) async {
    if (farm == null) return;
    _lastFetchedFarmId = farm.id;
    _lastFetchedLat = farm.latitude;
    _lastFetchedLon = farm.longitude;
    
    try {
      final district = farm.district;
      final state = farm.state;
      final village = farm.village;
      
      setState(() {
        _currentLocationName = '$village, $district';
      });

      final lang = context.read<LanguageProvider>().currentLanguage;
      WeatherModel weather;
      if (farm.latitude != null && farm.longitude != null) {
        debugPrint('[Weather] Fetching by farm coordinates: ${farm.latitude}, ${farm.longitude}');
        weather = await _weatherService.getWeather(farm.latitude!, farm.longitude!, lang: lang, farmName: farm.name);
      } else {
        debugPrint('[Weather] Coordinates missing for ${farm.name}, using location query fallback');
        weather = await _weatherService.getWeatherForLocation(village, district, state, lang: lang, farmName: farm.name);
      }
      
      if (mounted) {
        setState(() {
          _weatherData = weather;
          _error = null;
        });
      }
    } catch (e) {
      debugPrint('Weather fetch error: $e');
      if (mounted) {
        setState(() {
          _weatherData = null;
          _error = 'Live weather service unavailable';
        });
      }
    }
  }

  void _onFarmSelected(BuildContext context, int index) {
    final farmProvider = Provider.of<FarmProvider>(context, listen: false);
    farmProvider.selectFarmIndex(index);
  }

  void _onNavTap(int index) {
    switch (index) {
      case 1:
        context.push(AppRouter.crops);
        break;
      case 2:
        context.push(AppRouter.market);
        break;
      case 3:
        context.push(AppRouter.advisory);
        break;
      case 4:
        context.push(AppRouter.profile);
        break;
    }
  }

  Future<void> _handleLogout() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Logout'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w700)),
        content: Text('Are you sure you want to sign out?'.tr(context), style: GoogleFonts.poppins()),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: Text('Cancel'.tr(context))),
          TextButton(onPressed: () => Navigator.pop(context, true), child: Text('Logout'.tr(context), style: TextStyle(color: Colors.red))),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      await Provider.of<AuthProvider>(context, listen: false).signOut();
      final prefs = await SharedPreferences.getInstance();
      await prefs.clear();
      if (mounted) {
        context.go(AppRouter.login);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final farmProvider = context.watch<FarmProvider>();
    final selectedFarm = farmProvider.selectedFarm;
    final userProvider = context.watch<UserProvider>();
    final userModel = userProvider.userModel;
    
    if (selectedFarm != null &&
        (_lastFetchedFarmId != selectedFarm.id ||
         _lastFetchedLat != selectedFarm.latitude ||
         _lastFetchedLon != selectedFarm.longitude ||
         _weatherData == null)) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _fetchWeatherForFarm(selectedFarm);
      });
    }

    final isPageLoading = _isLoading || farmProvider.isLoading || userProvider.isLoading;

    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadInitialData,
          color: Colors.white,
          child: CustomScrollView(
            physics: const BouncingScrollPhysics(),
            slivers: [
              // Header
              SliverToBoxAdapter(
                child: DashboardHeader(
                  greeting: AppUtils.getGreeting().tr(context),
                  farmerName: userModel?.name ?? 'Farmer'.tr(context),
                  profileImageUrl: userModel?.profileImageUrl,
                  date: AppUtils.getTodayDateFormatted(),
                  farmArea: selectedFarm?.landArea?.toString() ?? '0',
                  location: _currentLocationName,
                  fieldName: selectedFarm?.name ?? 'Field'.tr(context),
                  allFarmNames: farmProvider.farms.map((f) => f.name).toList(),
                  selectedFarmIndex: farmProvider.selectedFarmIndex,
                  onFarmSelected: (index) => _onFarmSelected(context, index),
                  onLogoutTap: _handleLogout,
                ),
              ),

              if (isPageLoading && userModel == null && farmProvider.farms.isEmpty)
                const SliverFillRemaining(
                  child: Center(child: CircularProgressIndicator(color: Colors.white)),
                )
              else if (_error != null && userModel == null && farmProvider.farms.isEmpty)
                SliverFillRemaining(
                  child: Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.error_outline_rounded, size: 48, color: AppColors.error),
                          const SizedBox(height: 16),
                          Text(_error!, textAlign: TextAlign.center, style: GoogleFonts.poppins()),
                          const SizedBox(height: 16),
                          ElevatedButton(onPressed: _loadInitialData, child: Text('Try Again'.tr(context))),
                        ],
                      ),
                    ),
                  ),
                )
              else
                SliverPadding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                  sliver: SliverList(
                    delegate: SliverChildListDelegate([
                      const SizedBox(height: 16),

                      // Weather Card
                      GestureDetector(
                        onTap: () => context.push(AppRouter.weatherDashboard),
                        child: WeatherCard(
                          temperature: _weatherData != null ? '${_weatherData!.temperature.toInt()}°C' : '--°C',
                          condition: _weatherData?.condition ?? '--',
                          humidity: _weatherData != null ? '${_weatherData!.humidity.toInt()}%' : '--%',
                          windSpeed: _weatherData != null ? '${_weatherData!.windSpeed.toInt()} km/h' : '-- km/h',
                          location: _currentLocationName,
                          rainChance: _weatherData != null ? '${_weatherData!.rainChance.toInt()}%' : '--%',
                        ),
                      ),
                      const SizedBox(height: 20),

                      // Farm Summary Row
                      Row(
                        children: [
                          _buildSummaryCard(
                            'Farm Area'.tr(context),
                            '${selectedFarm?.landArea ?? '0'} ${'Acres'.tr(context)}',
                            Icons.landscape_outlined,
                            Colors.orange,
                          ),
                          const SizedBox(width: 12),
                          _buildSummaryCard(
                            'Active Crop'.tr(context),
                            '${selectedFarm?.preferredCrops.length ?? 0}',
                            Icons.grass_rounded,
                            Colors.green,
                          ),
                        ],
                      ),
                      const SizedBox(height: 20),

                      // AI Recommendation Banner
                      _buildRecommendationBanner(context),
                      const SizedBox(height: 20),

                      // Section Title
                      _sectionTitle(AppStrings.quickActions.tr(context)),
                      const SizedBox(height: 12),

                      // Quick Actions
                      const QuickActionsGrid(),
                      const SizedBox(height: 20),

                      // Market Prices
                      _sectionTitle(AppStrings.marketPrice.tr(context), showViewAll: true,
                          onViewAll: () => context.go(AppRouter.market)),
                      const SizedBox(height: 12),

                      const MarketPricesCard(),
                      const SizedBox(height: 90),
                    ]),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSummaryCard(String title, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
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
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: color, size: 18),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: GoogleFonts.poppins(
                      fontSize: 11,
                      color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    value,
                    style: GoogleFonts.poppins(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      color: Theme.of(context).colorScheme.onSurface,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendationBanner(BuildContext context) {
    return GestureDetector(
      onTap: () => context.push(AppRouter.cropRecommendation),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: AppColors.cardGradient,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: Colors.white.withOpacity(0.3),
              blurRadius: 15,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.auto_awesome, color: Colors.white, size: 18),
                      const SizedBox(width: 8),
                      Text(
                        'AI Recommendation'.tr(context),
                        style: GoogleFonts.poppins(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Colors.white.withOpacity(0.9),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'What should you plant next?'.tr(context),
                    style: GoogleFonts.poppins(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: Theme.of(context).cardColor.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'Get Advice'.tr(context),
                      style: GoogleFonts.poppins(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios_rounded, color: Colors.white, size: 24),
          ],
        ),
      ),
    );
  }

  Widget _sectionTitle(String title,
      {bool showViewAll = false, VoidCallback? onViewAll}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          title,
          style: GoogleFonts.poppins(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: Theme.of(context).colorScheme.onSurface,
          ),
        ),
        if (showViewAll)
          GestureDetector(
            onTap: onViewAll,
            child: Text(
              AppStrings.viewAll,
              style: GoogleFonts.poppins(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: AppColors.primary,
              ),
            ),
          ),
      ],
    );
  }
}
