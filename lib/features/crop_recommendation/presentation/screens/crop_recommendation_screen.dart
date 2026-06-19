import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:percent_indicator/linear_percent_indicator.dart';
import 'package:provider/provider.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/services/firestore_service.dart';
import '../../../../core/services/weather_service.dart';
import '../../../../core/services/recommendation_service.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/providers/farm_provider.dart';
import '../../../../core/providers/language_provider.dart';
import '../../../../features/weather/data/models/weather_model.dart';
import '../../data/recommendation_data.dart';
import '../../../../core/models/user_model.dart';
import '../../../../core/models/farm_model.dart';

class CropRecommendationScreen extends StatefulWidget {
  const CropRecommendationScreen({super.key});

  @override
  State<CropRecommendationScreen> createState() => _CropRecommendationScreenState();
}

class _CropRecommendationScreenState extends State<CropRecommendationScreen> {
  final _firestoreService = FirestoreService();
  final _weatherService = WeatherService();
  
  bool _isLoadingUser = true;
  bool _isLoadingRecommendations = false;
  String? _error;
  
  UserModel? _user;
  WeatherModel? _weather;
  List<RecommendationModel> _recommendations = [];
  String? _lastFetchedFarmId;

  @override
  void initState() {
    super.initState();
    _fetchUser();
  }

  Future<void> _fetchUser() async {
    setState(() {
      _isLoadingUser = true;
      _error = null;
    });

    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final user = authProvider.user;
      
      if (user == null) {
        throw Exception('User not authenticated');
      }

      final userDoc = await _firestoreService.getDocument('users/${user.uid}');
      if (!userDoc.exists) {
        throw Exception('Profile not found. Please complete setup.');
      }
      
      if (mounted) {
        setState(() {
          _user = UserModel.fromMap(userDoc.data() as Map<String, dynamic>);
        });
      }
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoadingUser = false);
    }
  }

  Future<void> _fetchRecommendationsForFarm(FarmModel farm) async {
    if (_lastFetchedFarmId == farm.id) return;
    
    _lastFetchedFarmId = farm.id;
    setState(() => _isLoadingRecommendations = true);

    try {
      final lang = Provider.of<LanguageProvider>(context, listen: false).currentLanguage;
      _weather = await _weatherService.getWeatherForLocation(farm.village, farm.district, farm.state, lang: lang);
      _recommendations = await RecommendationService.getRecommendations(farm: farm, weather: _weather!, languageCode: lang);

      if (_recommendations.isEmpty) {
        _recommendations = CropRecommendationData.getMockRecommendations();
      }
    } catch (e) {
      debugPrint('Recommendation error: $e');
      _recommendations = CropRecommendationData.getMockRecommendations();
    } finally {
      if (mounted) setState(() => _isLoadingRecommendations = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final farmProvider = context.watch<FarmProvider>();
    final farm = farmProvider.selectedFarm;

    if (farm != null && _lastFetchedFarmId != farm.id && !_isLoadingRecommendations) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _fetchRecommendationsForFarm(farm);
      });
    }

    final isPageLoading = _isLoadingUser || farmProvider.isLoading || _isLoadingRecommendations;

    if (isPageLoading) {
      return Scaffold(
        body: Center(child: CircularProgressIndicator(color: Theme.of(context).colorScheme.onSurface)),
      );
    }

    if (_error != null || farm == null) {
      return Scaffold(
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error_outline_rounded, size: 64, color: AppColors.error),
                const SizedBox(height: 16),
                Text(
                  'Something went wrong',
                  style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  _error ?? 'No fields found. Please add a field in your Profile.',
                  textAlign: TextAlign.center,
                  style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () {
                    _lastFetchedFarmId = null;
                    _fetchUser();
                  },
                  style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
                  child: Text('Retry'.tr(context)),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return Scaffold(
      
      body: CustomScrollView(
        slivers: [
          _buildSliverAppBar(context),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(AppDimensions.paddingLG),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildConditionsHeader(farm),
                  const SizedBox(height: 32),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'AI Recommendations',
                        style: GoogleFonts.poppins(
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                          color: Theme.of(context).colorScheme.onSurface,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: Theme.of(context).cardColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.auto_awesome, size: 14, color: Theme.of(context).colorScheme.onSurface),
                            const SizedBox(width: 4),
                            Text(
                              'Live AI',
                              style: GoogleFonts.poppins(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: Theme.of(context).colorScheme.onSurface,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: _recommendations.length,
                    separatorBuilder: (context, index) => const SizedBox(height: 16),
                    itemBuilder: (context, index) {
                      return _CropRecommendationCard(
                        recommendation: _recommendations[index],
                        farm: farm,
                      ).animate().fadeIn(delay: (100 * index).ms).slideY(begin: 0.1, end: 0);
                    },
                  ),
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSliverAppBar(BuildContext context) {
    return SliverAppBar(
      expandedHeight: 120,
      floating: false,
      pinned: true,
      backgroundColor: AppColors.primary,
      elevation: 0,
      flexibleSpace: FlexibleSpaceBar(
        title: Text(
          'Crop Recommendations',
          style: GoogleFonts.poppins(
            fontWeight: FontWeight.w600,
            color: Theme.of(context).colorScheme.onSurface,
            fontSize: 18,
          ),
        ),
        background: Stack(
          children: [
            Container(decoration: const BoxDecoration(gradient: AppColors.primaryGradient)),
            Positioned(
              right: -20,
              top: -20,
              child: Icon(Icons.eco, size: 140, color: Theme.of(context).colorScheme.onSurface.withOpacity(0.1)),
            ),
          ],
        ),
      ),
      leading: IconButton(
        icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white, size: 20),
        onPressed: () => Navigator.pop(context),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.search_rounded, color: Colors.white),
          onPressed: () {
            final farm = Provider.of<FarmProvider>(context, listen: false).selectedFarm;
            if (farm != null && _weather != null) {
              showModalBottomSheet(
                context: context,
                isScrollControlled: true,
                backgroundColor: Colors.transparent,
                builder: (context) => _CustomCropAnalyzerSheet(farm: farm, weather: _weather!),
              );
            }
          },
        ),
      ],
    );
  }

  Widget _buildConditionsHeader(FarmModel farm) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Your Farm Conditions',
            style: GoogleFonts.poppins(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: Theme.of(context).colorScheme.onSurface,
            ),
          ),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildConditionItem(
                Icons.wb_sunny_outlined, 
                _weather != null ? '${_weather!.temperature.toStringAsFixed(1)}°C' : '--°C', 
                _weather?.condition ?? 'Loading...', 
                AppColors.secondary
              ),
              _buildConditionItem(
                Icons.calendar_month_outlined, 
                _weather?.season ?? '--', 
                'Season', 
                AppColors.primary
              ),
              _buildConditionItem(
                Icons.layers_outlined, 
                farm.soilType.split(' ')[0], 
                'Soil Type', 
                AppColors.earth
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildConditionItem(IconData icon, String value, String label, Color color) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color, size: 22),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: GoogleFonts.poppins(
            fontSize: 14,
            fontWeight: FontWeight.w700,
            color: Theme.of(context).colorScheme.onSurface,
          ),
        ),
        Text(
          label,
          style: GoogleFonts.poppins(
            fontSize: 11,
            color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
          ),
        ),
      ],
    );
  }
}

class _CropRecommendationCard extends StatelessWidget {
  final RecommendationModel recommendation;
  final FarmModel farm;

  const _CropRecommendationCard({required this.recommendation, required this.farm});

  Future<void> _plantCrop(BuildContext context) async {
    final cropName = recommendation.cropName;
    if (farm.preferredCrops.contains(cropName)) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$cropName is already planted in your field!'), backgroundColor: Colors.orange),
      );
      return;
    }

    try {
      final newCrops = List<String>.from(farm.preferredCrops)..add(cropName);
      final newPlantedCrops = List<PlantedCropModel>.from(farm.plantedCrops)
        ..add(PlantedCropModel(cropName: cropName, plantedDate: DateTime.now()));
      await FirebaseFirestore.instance.collection('farms').doc(farm.id).update({
        'preferredCrops': newCrops,
        'plantedCrops': newPlantedCrops.map((c) => c.toMap()).toList(),
      });
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('✅ $cropName added to your field!'), backgroundColor: AppColors.success),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to add crop.'.tr(context)), backgroundColor: AppColors.error),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
            child: SizedBox(
              height: 140,
              width: double.infinity,
              child: CachedNetworkImage(
                imageUrl: recommendation.imageUrl,
                fit: BoxFit.cover,
                placeholder: (context, url) => Container(color: AppColors.surfaceVariant),
                errorWidget: (context, url, error) => const Icon(Icons.error),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  recommendation.cropName,
                                  style: GoogleFonts.poppins(
                                    fontSize: 18,
                                    fontWeight: FontWeight.w700,
                                    color: Theme.of(context).colorScheme.onSurface,
                                  ),
                                ),
                              ),
                              if (recommendation.source != null && recommendation.source != 'LOCAL_ENGINE') ...[
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: recommendation.source == 'GEMINI_FALLBACK'
                                        ? Colors.blue.withValues(alpha: 0.15)
                                        : Colors.orange.withValues(alpha: 0.15),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(
                                        recommendation.source == 'GEMINI_FALLBACK'
                                            ? Icons.auto_awesome_rounded
                                            : Icons.alt_route_rounded,
                                        size: 10,
                                        color: recommendation.source == 'GEMINI_FALLBACK'
                                            ? Colors.blue[700]
                                            : Colors.orange[700],
                                      ),
                                      const SizedBox(width: 4),
                                      Text(
                                        recommendation.source == 'GEMINI_FALLBACK'
                                            ? 'Gemini'
                                            : 'Enhanced',
                                        style: GoogleFonts.poppins(
                                          fontSize: 9,
                                          fontWeight: FontWeight.bold,
                                          color: recommendation.source == 'GEMINI_FALLBACK'
                                              ? Colors.blue[700]
                                              : Colors.orange[700],
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ],
                          ),
                          if (recommendation.isLocallyCultivated) ...[
                            const SizedBox(height: 4),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: Theme.of(context).cardColor.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.location_on, size: 12, color: Theme.of(context).colorScheme.onSurface),
                                  const SizedBox(width: 4),
                                  Text(
                                    'Popular in your Region',
                                    style: GoogleFonts.poppins(fontSize: 10, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.onSurface),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        _buildDemandBadge(),
                        const SizedBox(height: 4),
                        Text(
                          '${(recommendation.suitabilityScore * 100).toInt()}% Match',
                          style: GoogleFonts.poppins(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: Theme.of(context).colorScheme.onSurface,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    const Icon(Icons.payments_outlined, size: 16, color: AppColors.success),
                    const SizedBox(width: 8),
                    Text(
                      recommendation.expectedProfit,
                      style: GoogleFonts.poppins(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.success,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                _buildMarketDemandIndicator(context),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.background,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.info_outline_rounded, size: 18, color: Theme.of(context).colorScheme.onSurface),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          recommendation.matchReason,
                          style: GoogleFonts.poppins(
                            fontSize: 12,
                            color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () => _plantCrop(context),
                    icon: const Icon(Icons.add_circle_outline, size: 18),
                    label: Text(
                      'Plant this Crop',
                      style: GoogleFonts.poppins(fontWeight: FontWeight.w600),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      elevation: 0,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDemandBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.success.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        '${recommendation.marketDemand} Demand',
        style: GoogleFonts.poppins(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: AppColors.success,
        ),
      ),
    );
  }

  Widget _buildMarketDemandIndicator(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Market Demand',
              style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w500),
            ),
            Text(
              '${(recommendation.demandScore * 100).toInt()}%',
              style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface),
            ),
          ],
        ),
        const SizedBox(height: 8),
        LinearPercentIndicator(
          lineHeight: 8.0,
          percent: recommendation.demandScore,
          backgroundColor: AppColors.surfaceVariant,
          progressColor: AppColors.primary,
          barRadius: const Radius.circular(10),
          padding: EdgeInsets.zero,
          animation: true,
          animationDuration: 1000,
        ),
      ],
    );
  }
}

class _CustomCropAnalyzerSheet extends StatefulWidget {
  final FarmModel farm;
  final WeatherModel weather;

  const _CustomCropAnalyzerSheet({required this.farm, required this.weather});

  @override
  State<_CustomCropAnalyzerSheet> createState() => _CustomCropAnalyzerSheetState();
}

class _CustomCropAnalyzerSheetState extends State<_CustomCropAnalyzerSheet> {
  final TextEditingController _controller = TextEditingController();
  CustomCropAnalysisModel? _analysis;

  Future<void> _analyze() async {
    if (_controller.text.trim().isEmpty) return;
    FocusScope.of(context).unfocus();
    
    final lang = Provider.of<LanguageProvider>(context, listen: false).currentLanguage;
    final result = await RecommendationService.analyzeCustomCrop(
      cropName: _controller.text.trim(),
      farm: widget.farm,
      weather: widget.weather,
      languageCode: lang,
    );

    setState(() {
      _analysis = result;
    });
  }

  Future<void> _plantCustomCrop() async {
    if (_analysis == null) return;
    
    final cropName = _analysis!.cropName;
    if (widget.farm.preferredCrops.contains(cropName)) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$cropName is already planted in your field!'), backgroundColor: Colors.orange),
      );
      return;
    }

    try {
      final newCrops = List<String>.from(widget.farm.preferredCrops)..add(cropName);
      final newPlantedCrops = List<PlantedCropModel>.from(widget.farm.plantedCrops)
        ..add(PlantedCropModel(cropName: cropName, plantedDate: DateTime.now()));
      await FirebaseFirestore.instance.collection('farms').doc(widget.farm.id).update({
        'preferredCrops': newCrops,
        'plantedCrops': newPlantedCrops.map((c) => c.toMap()).toList(),
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('✅ $cropName added to your field!'), backgroundColor: AppColors.success),
        );
        Navigator.pop(context); // close bottom sheet
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to add crop.'.tr(context)), backgroundColor: AppColors.error),
        );
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      decoration: const BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          Container(
            margin: const EdgeInsets.only(top: 12),
            height: 4,
            width: 40,
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(24),
            child: Row(
              children: [
                Icon(Icons.analytics_outlined, color: Theme.of(context).colorScheme.onSurface, size: 28),
                const SizedBox(width: 12),
                Text(
                  'Custom Crop Analyzer',
                  style: GoogleFonts.poppins(fontSize: 20, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: 'e.g. Tomatoes, Chilli, Wheat',
                      hintStyle: GoogleFonts.poppins(color: AppColors.textHint),
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: BorderSide.none,
                      ),
                      prefixIcon: const Icon(Icons.search, color: AppColors.textHint),
                    ),
                    onSubmitted: (_) => _analyze(),
                  ),
                ),
                const SizedBox(width: 12),
                GestureDetector(
                  onTap: _analyze,
                  child: Container(
                    height: 52,
                    width: 52,
                    decoration: BoxDecoration(
                      color: Theme.of(context).cardColor,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Icon(Icons.arrow_forward_rounded, color: Theme.of(context).colorScheme.onSurface),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: _analysis == null
                ? Center(
                    child: Text(
                      'Search for a crop to analyze its suitability\nfor your specific farm conditions.',
                      textAlign: TextAlign.center,
                      style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                    ),
                  )
                : ListView(
                    padding: const EdgeInsets.symmetric(horizontal: 24),
                    children: [
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: Theme.of(context).cardColor,
                          borderRadius: BorderRadius.circular(20),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.05),
                              blurRadius: 10,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  _analysis!.cropName.toUpperCase(),
                                  style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.w700),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: _getVerdictColor(_analysis!.score).withOpacity(0.1),
                                    borderRadius: BorderRadius.circular(20),
                                  ),
                                  child: Text(
                                    _analysis!.verdict,
                                    style: GoogleFonts.poppins(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w600,
                                      color: _getVerdictColor(_analysis!.score),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 24),
                            Text(
                              'Suitability Score',
                              style: GoogleFonts.poppins(fontSize: 14, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                Expanded(
                                  child: LinearPercentIndicator(
                                    lineHeight: 10.0,
                                    percent: _analysis!.score / 100,
                                    backgroundColor: AppColors.surfaceVariant,
                                    progressColor: _getVerdictColor(_analysis!.score),
                                    barRadius: const Radius.circular(10),
                                    padding: EdgeInsets.zero,
                                    animation: true,
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Text(
                                  '${_analysis!.score.toInt()}%',
                                  style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                      if (_analysis!.positives.isNotEmpty) ...[
                        Text(
                          'Positives',
                          style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.success),
                        ),
                        const SizedBox(height: 12),
                        ..._analysis!.positives.map((p) => Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: Text(p, style: GoogleFonts.poppins(fontSize: 14, color: Theme.of(context).colorScheme.onSurface)),
                        )),
                        const SizedBox(height: 24),
                      ],
                      if (_analysis!.warnings.isNotEmpty) ...[
                        Text(
                          'Risk Warnings',
                          style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.error),
                        ),
                        const SizedBox(height: 12),
                        ..._analysis!.warnings.map((w) => Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: Text(w, style: GoogleFonts.poppins(fontSize: 14, color: AppColors.error)),
                        )),
                      ],
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: _plantCustomCrop,
                          icon: const Icon(Icons.add_circle_outline, size: 18),
                          label: Text(
                            'Plant this Crop Anyway',
                            style: GoogleFonts.poppins(fontWeight: FontWeight.w600),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.primary,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            elevation: 0,
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  Color _getVerdictColor(double score) {
    if (score >= 70) return AppColors.success;
    if (score >= 40) return Colors.orange;
    return AppColors.error;
  }
}

