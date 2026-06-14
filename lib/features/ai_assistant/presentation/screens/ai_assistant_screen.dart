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

class AIAssistantScreen extends StatefulWidget {
  const AIAssistantScreen({super.key});

  @override
  State<AIAssistantScreen> createState() => _AIAssistantScreenState();
}

class _AIAssistantScreenState extends State<AIAssistantScreen> {
  int _selectedCropIndex = 0;
  int _selectedDayIndex = 2; // Default to 'Today' which is index 2 in our 5-day list
  late GeminiService _geminiService;
  
  List<GuidanceDay>? _liveGuidance;
  bool _isLoadingGuidance = false;

  @override
  void initState() {
    super.initState();
    final farmProvider = Provider.of<FarmProvider>(context, listen: false);
    final lang = Provider.of<LanguageProvider>(context, listen: false).currentLanguage;
    _geminiService = GeminiService(selectedFarm: farmProvider.selectedFarm, languageCode: lang);
    
    // Fetch live AI guidance after layout
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fetchLiveGuidanceForCurrentCrop();
    });
  }

  Future<void> _fetchLiveGuidanceForCurrentCrop() async {
    final farmProvider = Provider.of<FarmProvider>(context, listen: false);
    final farm = farmProvider.selectedFarm;
    if (farm == null || farm.plantedCrops.isEmpty) return;

    if (_selectedCropIndex >= farm.plantedCrops.length) {
       _selectedCropIndex = 0;
    }
    final crop = farm.plantedCrops[_selectedCropIndex];
    final ageDays = DateTime.now().difference(DateTime(crop.plantedDate.year, crop.plantedDate.month, crop.plantedDate.day)).inDays;

    setState(() {
      _isLoadingGuidance = true;
      _liveGuidance = null;
    });

    final jsonStr = await _geminiService.generateDailyGuidance(
      cropName: crop.cropName,
      cropAgeDays: ageDays,
      state: farm.state,
      soilType: farm.soilType,
    );

    if (mounted) {
      setState(() {
        // Clean markdown from json just in case
        final cleanJson = jsonStr.replaceAll('```json', '').replaceAll('```', '').trim();
        if (cleanJson.length > 5 && cleanJson.startsWith('[')) {
           _liveGuidance = AssistantData.parseLiveGuidance(cleanJson, crop.plantedDate);
        } else {
           // Fallback to local if AI fails or rate limited
           _liveGuidance = AssistantData.getGuidanceForCrop(cropName: crop.cropName, plantedDate: crop.plantedDate);
        }
        _isLoadingGuidance = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final farmProvider = Provider.of<FarmProvider>(context);
    final farm = farmProvider.selectedFarm;

    if (farm == null) {
      return Scaffold(
        
        appBar: AppBar(
          title: Text(
            'AI Farming Assistant',
            style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18),
          ),
        ),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.grass_rounded, size: 64, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                const SizedBox(height: 16),
                Text(
                  'No field selected',
                  style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  'Please select or add a field to get AI guidance.',
                  style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      );
    }

    final plantedCrops = farm.plantedCrops;

    if (plantedCrops.isEmpty) {
      return Scaffold(
        
        appBar: AppBar(
          title: Text(
            'AI Farming Assistant',
            style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18),
          ),
        ),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.eco_rounded, size: 64, color: Colors.green),
                const SizedBox(height: 16),
                Text(
                  'No crops planted yet',
                  style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  'Plant a crop from recommendations or analyze one to start getting AI guidance.',
                  style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () => context.push(AppRouter.cropRecommendation),
                  icon: const Icon(Icons.add_circle_outline_rounded),
                  label: Text('Go to Recommendations'.tr(context)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    if (_selectedCropIndex >= plantedCrops.length) {
      _selectedCropIndex = 0;
    }

    final selectedPlantedCrop = plantedCrops[_selectedCropIndex];
    final guidance = _liveGuidance ?? AssistantData.getGuidanceForCrop(
      cropName: selectedPlantedCrop.cropName,
      plantedDate: selectedPlantedCrop.plantedDate,
    );

    if (_selectedDayIndex >= guidance.length) {
      _selectedDayIndex = 2; // Reset to Today
    }
    final currentDay = guidance[_selectedDayIndex];

    return Scaffold(
      
      appBar: AppBar(
        title: Text(
          'AI Farming Assistant',
          style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline_rounded, color: Colors.white),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('AI Assistant provides real-time guidance based on your selected field and crops.'.tr(context))),
              );
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            padding: const EdgeInsets.only(bottom: 100),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildCropDropdown(plantedCrops),
                const Divider(height: 1, color: AppColors.divider),
                if (_isLoadingGuidance)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 80.0),
                    child: Center(
                      child: Column(
                        children: [
                          const CircularProgressIndicator(color: AppColors.primary),
                          const SizedBox(height: 16),
                          Text('AI is analyzing your crop stage...'.tr(context), style: const TextStyle(color: Colors.grey)),
                        ],
                      ),
                    ),
                  )
                else
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildDaySelector(guidance),
                      Padding(
                        padding: const EdgeInsets.all(AppDimensions.paddingLG),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _buildDailyGuidanceCard(currentDay.dailyTip),
                            const SizedBox(height: 24),
                            _buildSectionTitle('Today\'s Schedule'),
                            const SizedBox(height: 16),
                            _buildTaskTimeline(currentDay.tasks),
                            const SizedBox(height: 32),
                            _buildSpecializedRecommendations(),
                            const SizedBox(height: 24),
                            _buildHarvestTracker(selectedPlantedCrop.cropName, selectedPlantedCrop.plantedDate),
                          ],
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ),
          _buildChatFloatingButton(),
        ],
      ),
    );
  }

  Widget _buildCropDropdown(List<PlantedCropModel> crops) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: AppColors.primary,
      child: Row(
        children: [
          const Icon(Icons.spa_outlined, color: Colors.white),
          const SizedBox(width: 12),
          Text(
            'Active Crop:',
            style: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 14, color: Colors.white),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: DropdownButtonHideUnderline(
              child: DropdownButton<int>(
                value: _selectedCropIndex,
                icon: const Icon(Icons.arrow_drop_down, color: Colors.white),
                items: List.generate(crops.length, (index) {
                  return DropdownMenuItem<int>(
                    value: index,
                    child: Text(
                      crops[index].cropName,
                      style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 15),
                    ),
                  );
                }),
                onChanged: (val) {
                  if (val != null && val != _selectedCropIndex) {
                    setState(() {
                      _selectedCropIndex = val;
                      _selectedDayIndex = 2; // reset to today
                    });
                    _fetchLiveGuidanceForCurrentCrop();
                  }
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDaySelector(List<GuidanceDay> guidance) {
    return Container(
      height: 100,
      color: Colors.white,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        itemCount: guidance.length,
        itemBuilder: (context, index) {
          final isSelected = _selectedDayIndex == index;
          final date = guidance[index].date;
          final age = guidance[index].cropAgeDays;
          
          String ageText = age >= 0 ? 'Day $age' : 'Prep';
          if (age == 0) ageText = 'Planted';
          
          return GestureDetector(
            onTap: () => setState(() => _selectedDayIndex = index),
            child: AnimatedContainer(
              duration: 300.ms,
              width: 75,
              margin: const EdgeInsets.only(right: 12),
              decoration: BoxDecoration(
                color: isSelected ? AppColors.primary : AppColors.surfaceVariant,
                borderRadius: BorderRadius.circular(16),
                boxShadow: isSelected
                    ? [BoxShadow(color: Colors.white.withValues(alpha: 0.3), blurRadius: 8, offset: const Offset(0, 4))]
                    : [],
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    ageText,
                    style: GoogleFonts.poppins(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: isSelected ? Colors.white.withValues(alpha: 0.8) : AppColors.primary,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    DateFormat('E').format(date),
                    style: GoogleFonts.poppins(
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                      color: isSelected ? Colors.white.withValues(alpha: 0.8) : Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                    ),
                  ),
                  Text(
                    DateFormat('d').format(date),
                    style: GoogleFonts.poppins(
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      color: isSelected ? Colors.white : Theme.of(context).colorScheme.onSurface,
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildDailyGuidanceCard(String tip) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: AppColors.primaryGradient,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.white.withValues(alpha: 0.2),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Daily Guidance',
                  style: GoogleFonts.poppins(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Colors.white.withValues(alpha: 0.9),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  tip,
                  style: GoogleFonts.poppins(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                    color: Colors.white,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor.withValues(alpha: 0.2),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.lightbulb_outline_rounded, color: Colors.white, size: 28),
          ),
        ],
      ),
    ).animate().fadeIn().slideX(begin: -0.1, end: 0);
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: GoogleFonts.poppins(
        fontSize: 18,
        fontWeight: FontWeight.w700,
        color: Theme.of(context).colorScheme.onSurface,
      ),
    );
  }

  Widget _buildTaskTimeline(List<FarmTask> tasks) {
    return Column(
      children: tasks.map((task) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Column(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: task.color.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(task.icon, color: task.color, size: 24),
                  ),
                  const SizedBox(height: 4),
                  Container(width: 2, height: 30, color: AppColors.divider),
                ],
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardColor,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppColors.divider),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            task.title,
                            style: GoogleFonts.poppins(
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                              color: Theme.of(context).colorScheme.onSurface,
                            ),
                          ),
                          Text(
                            task.time,
                            style: GoogleFonts.poppins(
                              fontSize: 11,
                              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        task.category,
                        style: GoogleFonts.poppins(
                          fontSize: 12,
                          color: task.color,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildSpecializedRecommendations() {
    return Row(
      children: [
        Expanded(
          child: _buildSmallAdviceCard(
            'Fertilizer',
            'Check Fertilizer Screen',
            Icons.grass_rounded,
            Colors.green,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildSmallAdviceCard(
            'Irrigation',
            'Check Soil Moisture',
            Icons.water_drop_outlined,
            Colors.cyan,
          ),
        ),
      ],
    );
  }

  Widget _buildSmallAdviceCard(String title, String subtitle, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 12),
          Text(
            title,
            style: GoogleFonts.poppins(fontSize: 11, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
          ),
          Text(
            subtitle,
            style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.onSurface),
          ),
        ],
      ),
    );
  }

  Widget _buildHarvestTracker(String cropName, DateTime plantedDate) {
    final now = DateTime.now();
    final elapsedDays = now.difference(plantedDate).inDays;
    const totalDays = 90; // Standard growth cycle length
    final progress = (elapsedDays / totalDays).clamp(0.0, 1.0);
    final estHarvest = plantedDate.add(const Duration(days: totalDays));
    
    String stage = "Germination";
    if (elapsedDays > 75) {
      stage = "Maturity";
    } else if (elapsedDays > 45) {
      stage = "Flowering / Fruiting";
    } else if (elapsedDays > 14) {
      stage = "Vegetative Growth";
    } else if (elapsedDays > 3) {
      stage = "Seedling";
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildSectionTitle('Harvest Tracker'),
              const Icon(Icons.trending_up_rounded, color: AppColors.success, size: 20),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Icon(Icons.event_note_rounded, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7), size: 16),
              const SizedBox(width: 8),
              Text(
                'Est. Harvest: ${DateFormat('dd MMMM yyyy').format(estHarvest)}',
                style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w500),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 8,
              backgroundColor: AppColors.surfaceVariant,
              valueColor: const AlwaysStoppedAnimation<Color>(AppColors.success),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '${(progress * 100).toInt()}% Progress - Growth Stage: $stage',
            style: GoogleFonts.poppins(fontSize: 11, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
          ),
        ],
      ),
    );
  }

  Widget _buildChatFloatingButton() {
    return Positioned(
      bottom: 20,
      left: 20,
      right: 20,
      child: GestureDetector(
        onTap: () => context.push(AppRouter.aiAdvisory),
        child: Container(
          height: 65,
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(35),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.3),
                blurRadius: 15,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: Row(
            children: [
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: Theme.of(context).colorScheme.primary.withOpacity(0.1), shape: BoxShape.circle),
                child: Icon(Icons.auto_awesome, color: Theme.of(context).colorScheme.primary, size: 24),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Text(
                  'Ask AI Assistant...',
                  style: GoogleFonts.poppins(
                    fontSize: 15,
                    color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              IconButton(
                icon: Icon(Icons.mic_none_rounded, color: Theme.of(context).colorScheme.onSurface, size: 26),
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Voice assistant coming soon!'.tr(context))),
                  );
                },
              ),
              const SizedBox(width: 8),
            ],
          ),
        ),
      ).animate().slideY(begin: 1, end: 0, delay: 500.ms, curve: Curves.elasticOut),
    );
  }
}
