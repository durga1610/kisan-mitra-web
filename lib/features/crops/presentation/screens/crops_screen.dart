import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:intl/intl.dart';
import 'package:percent_indicator/linear_percent_indicator.dart';
import 'package:provider/provider.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/providers/farm_provider.dart';
import '../../../../core/models/farm_model.dart';
import '../../../../core/localization/app_translations.dart';
import '../../../../core/services/firestore_service.dart';
import '../../../../core/services/gemini_service.dart';
import '../../../../features/profile_setup/presentation/screens/profile_setup_screen.dart';

class CropsScreen extends StatelessWidget {
  const CropsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final farmProvider = context.watch<FarmProvider>();
    final farm = farmProvider.selectedFarm;

    if (farm == null) {
      return Scaffold(
        
        appBar: AppBar(
          title: Text(
            'Farm Management'.tr(context),
            style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18),
          ),
        ),
        body: Center(
          child: Text('No farm selected'.tr(context), style: GoogleFonts.poppins()),
        ),
      );
    }

    final totalLand = farm.landArea;
    final cropsCount = farm.plantedCrops.length;
    double usedLand = 0.0;
    for (var c in farm.plantedCrops) {
      usedLand += (c.landArea ?? 0.0);
    }

    return Scaffold(
      
      appBar: AppBar(
        title: Text(
          'Farm Management'.tr(context),
          style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_box_rounded, color: Colors.white),
            tooltip: 'Add Custom Crop',
            onPressed: () => _addCustomCrop(context, farm),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppDimensions.paddingLG),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildLandSummary(context, totalLand, usedLand),
            const SizedBox(height: 32),
            _buildSectionTitle(context, 'Active Cultivations'.tr(context)),
            const SizedBox(height: 16),
            if (farm.plantedCrops.isEmpty)
               Text('No active cultivations'.tr(context), style: GoogleFonts.poppins()),
            ...farm.plantedCrops.map((crop) => _buildCropProgressCard(context, crop, totalLand, cropsCount, farm)),
            const SizedBox(height: 32),
            if (farm.plantedCrops.isNotEmpty) ...[
              _buildSectionTitle(context, 'Land Analytics'.tr(context)),
              const SizedBox(height: 16),
              _buildLandDistributionChart(context, farm),
            ],
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildLandSummary(BuildContext context, double totalLand, double usedLand) {
    return Row(
      children: [
        Expanded(
          child: _buildSummaryItem(context,
            'Total Land'.tr(context),
            '$totalLand ${'Acres'.tr(context)}',
            Icons.landscape_rounded,
            AppColors.earth,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildSummaryItem(context,
            'Used Land'.tr(context),
            '$usedLand ${'Acres'.tr(context)}',
            Icons.pie_chart_rounded,
            AppColors.primary,
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryItem(BuildContext context, String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10, offset: const Offset(0, 4)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: color.withValues(alpha: 0.1), shape: BoxShape.circle),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(height: 16),
          Text(label, style: GoogleFonts.poppins(fontSize: 12, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
          Text(value, style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface)),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(BuildContext context, String title) {
    return Text(
      title,
      style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface),
    );
  }

  Widget _buildCropProgressCard(BuildContext context, PlantedCropModel crop, double totalLand, int cropsCount, FarmModel farm) {
    final landArea = crop.landArea ?? (cropsCount > 0 ? totalLand / cropsCount : 0.0);

    final now = DateTime.now();
    final daysSincePlanted = now.difference(crop.plantedDate).inDays;
    
    // Calculate simple mock progress assuming 120 days cycle
    final cycleDays = 120;
    double progress = daysSincePlanted / cycleDays;
    if (progress > 1.0) progress = 1.0;
    if (progress < 0.0) progress = 0.0;

    String stage = 'Seedling'.tr(context);
    if (progress > 0.8) stage = 'Harvesting'.tr(context);
    else if (progress > 0.5) stage = 'Fruiting'.tr(context);
    else if (progress > 0.2) stage = 'Vegetative'.tr(context);

    final estHarvest = crop.plantedDate.add(Duration(days: cycleDays));

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
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
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(color: AppColors.surfaceVariant, borderRadius: BorderRadius.circular(12)),
                child: Text('🌱'.tr(context), style: TextStyle(fontSize: 20)),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      crop.cropName,
                      style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface),
                    ),
                    Text(
                      '${landArea.toStringAsFixed(1)} ${'Acres'.tr(context)} • $stage',
                      style: GoogleFonts.poppins(fontSize: 12, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                    ),
                  ],
                ),
              ),

              _buildHealthBadge(context, 'Good'.tr(context)),
              IconButton(
                icon: const Icon(Icons.edit, size: 18),
                onPressed: () => _editLandArea(context, crop, farm),
              ),
              IconButton(
                icon: const Icon(Icons.delete_outline, size: 18, color: Colors.red),
                onPressed: () => _deleteCrop(context, crop, farm),
              ),

            ],
          ),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Progress'.tr(context),
                style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w500),
              ),
              Text(
                '${(progress * 100).toInt()}%',
                style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface),
              ),
            ],
          ),
          const SizedBox(height: 8),
          LinearPercentIndicator(
            lineHeight: 10.0,
            percent: progress,
            backgroundColor: AppColors.surfaceVariant,
            progressColor: AppColors.primary,
            barRadius: const Radius.circular(10),
            padding: EdgeInsets.zero,
            animation: true,
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildDateInfo(context, 'Sown'.tr(context), crop.plantedDate),
              _buildDateInfo(context, 'Est. Harvest'.tr(context), estHarvest),
            ],
          ),
        ],
      ),
    ).animate().fadeIn().slideX(begin: 0.1, end: 0);
  }

  Widget _buildHealthBadge(BuildContext context, String status) {
    final isGood = status == 'Good' || status == 'Good'.tr(context);
    final color = isGood ? AppColors.success : Colors.orange;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(12)),
      child: Text(
        status,
        style: GoogleFonts.poppins(fontSize: 10, fontWeight: FontWeight.w700, color: color),
      ),
    );
  }

  Widget _buildDateInfo(BuildContext context, String label, DateTime date) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: GoogleFonts.poppins(fontSize: 10, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
        Text(
          DateFormat('dd MMM yyyy').format(date),
          style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.onSurface),
        ),
      ],
    );
  }

  Widget _buildLandDistributionChart(BuildContext context, FarmModel farm) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Land Utilization'.tr(context),
            style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 20),
          ...farm.plantedCrops.map((crop) {
            final landArea = crop.landArea ?? (farm.plantedCrops.isNotEmpty ? farm.landArea / farm.plantedCrops.length : 0.0);
            final percentage = farm.landArea > 0 ? landArea / farm.landArea : 0.0;
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(crop.cropName, style: GoogleFonts.poppins(fontSize: 12)),
                      Text('${landArea.toStringAsFixed(1)} Ac (${(percentage * 100).toInt()}%)',
                          style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w600)),
                    ],
                  ),
                  const SizedBox(height: 6),
                  LinearPercentIndicator(
                    lineHeight: 6,
                    percent: percentage,
                    backgroundColor: AppColors.surfaceVariant,
                    progressColor: AppColors.earth,
                    barRadius: const Radius.circular(3),
                    padding: EdgeInsets.zero,
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Future<void> _editLandArea(BuildContext context, PlantedCropModel crop, FarmModel farm) async {
    final TextEditingController _controller = TextEditingController(text: crop.landArea?.toString() ?? '');
    
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Edit Land Area'.tr(context)),
        content: TextField(
          controller: _controller,
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            labelText: 'Land Area (Acres)'.tr(context),
            border: const OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'.tr(context)),
          ),
          ElevatedButton(
            onPressed: () async {
              final val = double.tryParse(_controller.text);
              if (val != null && val > 0 && farm.id != null) {
                double currentUsedLand = 0;
                for (var c in farm.plantedCrops) {
                  if (c.cropName.toLowerCase() != crop.cropName.toLowerCase()) {
                    currentUsedLand += (c.landArea ?? 0.0);
                  }
                }
                if (currentUsedLand + val > farm.landArea) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Not enough land! Available: ${(farm.landArea - currentUsedLand).toStringAsFixed(1)} Acres'),
                      backgroundColor: AppColors.error,
                    ),
                  );
                  return;
                }
                
                // Update in Firestore
                final index = farm.plantedCrops.indexOf(crop);
                if (index != -1) {
                  final newCrops = List<PlantedCropModel>.from(farm.plantedCrops);
                  newCrops[index] = PlantedCropModel(
                    cropName: crop.cropName,
                    plantedDate: crop.plantedDate,
                    landArea: val,
                  );
                  await FirestoreService().setData(
                    path: 'farms/${farm.id}',
                    data: {'plantedCrops': newCrops.map((c) => c.toMap()).toList()},
                    merge: true,
                  );
                }
              }
              if (context.mounted) Navigator.pop(context);
            },
            child: Text('Save'.tr(context)),
          ),
        ],
      ),
    );
  }
  Future<void> _deleteCrop(BuildContext context, PlantedCropModel crop, FarmModel farm) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Delete Crop'.tr(context)),
        content: Text('Are you sure you want to delete ${crop.cropName} from your farm?'.tr(context)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel'.tr(context)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
            onPressed: () => Navigator.pop(context, true),
            child: Text('Delete'.tr(context), style: const TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );

    if (confirm == true && farm.id != null) {
      final newCrops = List<PlantedCropModel>.from(farm.plantedCrops)
        ..removeWhere((c) => c.cropName.toLowerCase() == crop.cropName.toLowerCase());
      final newPreferred = List<String>.from(farm.preferredCrops)
        ..removeWhere((p) => p.toLowerCase() == crop.cropName.toLowerCase());
        
      await FirestoreService().setData(
        path: 'farms/${farm.id}',
        data: {
          'plantedCrops': newCrops.map((c) => c.toMap()).toList(),
          'preferredCrops': newPreferred,
        },
        merge: true,
      );
    }
  }

  Future<void> _addCustomCrop(BuildContext context, FarmModel farm) async {
    final TextEditingController _nameController = TextEditingController();
    final TextEditingController _areaController = TextEditingController();
    bool _isChecking = false;
    
    await showDialog(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setState) {
          return AlertDialog(
            title: Text('Add Custom Crop'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.bold)),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: _nameController,
                  enabled: !_isChecking,
                  decoration: InputDecoration(
                    labelText: 'Crop Name'.tr(context),
                    hintText: 'e.g. Tomato, Mango'.tr(context),
                    border: const OutlineInputBorder(),
                    prefixIcon: const Icon(Icons.eco_rounded),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _areaController,
                  keyboardType: TextInputType.number,
                  enabled: !_isChecking,
                  decoration: InputDecoration(
                    labelText: 'Land Area (Acres)'.tr(context),
                    border: const OutlineInputBorder(),
                    prefixIcon: const Icon(Icons.landscape_rounded),
                  ),
                ),
                if (_isChecking) ...[
                  const SizedBox(height: 20),
                  const CircularProgressIndicator(),
                  const SizedBox(height: 8),
                  Text('AI is analyzing crop suitability...', style: GoogleFonts.poppins(fontSize: 12, color: AppColors.primary)),
                ]
              ],
            ),
            actions: [
              if (!_isChecking)
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text('Cancel'.tr(context)),
                ),
              if (!_isChecking)
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                  ),
                  onPressed: () async {
                    final cropName = _nameController.text.trim();
                    final val = double.tryParse(_areaController.text);
                    if (cropName.isNotEmpty && farm.id != null) {
                      double currentUsedLand = 0;
                      for (var c in farm.plantedCrops) {
                        currentUsedLand += (c.landArea ?? 0.0);
                      }
                      final requiredLand = val ?? 0.0;
                      if (currentUsedLand + requiredLand > farm.landArea) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Not enough land! Available: ${(farm.landArea - currentUsedLand).toStringAsFixed(1)} Acres'),
                            backgroundColor: AppColors.error,
                          ),
                        );
                        return;
                      }

                      setState(() => _isChecking = true);
                      
                      final validationResult = await GeminiService.validateCropSuitability(cropName, farm.id!);
                      
                      setState(() => _isChecking = false);
                      
                      if (context.mounted) {
                        Navigator.pop(dialogContext); // Close Add Custom Crop dialog
                      }

                      if (validationResult != null && context.mounted) {
                        final bool isSuitable = validationResult['suitable'] ?? true;
                        final int score = validationResult['score'] ?? 100;
                        final List<dynamic> reasons = validationResult['reasons'] ?? [];
                        final List<dynamic> alternatives = validationResult['alternatives'] ?? [];

                        final proceed = await showDialog<bool>(
                          context: context,
                          barrierDismissible: false,
                          builder: (context) {
                            final Color scoreColor = isSuitable ? AppColors.success : Colors.orange;
                            return AlertDialog(
                              title: Row(
                                children: [
                                  Icon(
                                    isSuitable ? Icons.check_circle_outline_rounded : Icons.warning_amber_rounded,
                                    color: scoreColor,
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    isSuitable ? 'AI Crop Suitability: Suitable' : 'AI Crop Suitability Warning',
                                    style: GoogleFonts.poppins(fontWeight: FontWeight.bold, fontSize: 16),
                                  ),
                                ],
                              ),
                              content: SingleChildScrollView(
                                child: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                      decoration: BoxDecoration(
                                        color: scoreColor.withValues(alpha: 0.1),
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(
                                            isSuitable ? 'Suitable' : 'Not Recommended',
                                            style: GoogleFonts.poppins(
                                              fontWeight: FontWeight.bold,
                                              color: scoreColor,
                                            ),
                                          ),
                                          Text(
                                            'Score: $score%',
                                            style: GoogleFonts.poppins(
                                              fontWeight: FontWeight.bold,
                                              color: scoreColor,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    const SizedBox(height: 16),
                                    Text(
                                      'Suitability Factors:',
                                      style: GoogleFonts.poppins(fontWeight: FontWeight.bold, fontSize: 12),
                                    ),
                                    const SizedBox(height: 6),
                                    ...reasons.map((r) => Padding(
                                      padding: const EdgeInsets.only(bottom: 6),
                                      child: Row(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          const Text('• ', style: TextStyle(fontWeight: FontWeight.bold)),
                                          Expanded(
                                            child: Text(
                                              r.toString(),
                                              style: GoogleFonts.poppins(fontSize: 12),
                                            ),
                                          ),
                                        ],
                                      ),
                                    )),
                                    if (!isSuitable && alternatives.isNotEmpty) ...[
                                      const SizedBox(height: 16),
                                      Text(
                                        'Recommended Alternatives:',
                                        style: GoogleFonts.poppins(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 12,
                                          color: AppColors.primary,
                                        ),
                                      ),
                                      const SizedBox(height: 6),
                                      ...alternatives.map((alt) => Padding(
                                        padding: const EdgeInsets.only(bottom: 4),
                                        child: Row(
                                          children: [
                                            const Icon(Icons.eco_rounded, size: 14, color: Colors.green),
                                            const SizedBox(width: 6),
                                            Text(
                                              alt.toString(),
                                              style: GoogleFonts.poppins(
                                                fontSize: 12,
                                                fontWeight: FontWeight.w500,
                                              ),
                                            ),
                                          ],
                                        ),
                                      )),
                                    ]
                                  ],
                                ),
                              ),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.pop(context, false),
                                  child: Text('Cancel', style: GoogleFonts.poppins()),
                                ),
                                ElevatedButton(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: isSuitable ? AppColors.success : Colors.red,
                                    foregroundColor: Colors.white,
                                  ),
                                  onPressed: () => Navigator.pop(context, true),
                                  child: Text(
                                    isSuitable ? 'Plant Crop' : 'Plant Anyway',
                                    style: GoogleFonts.poppins(fontWeight: FontWeight.bold),
                                  ),
                                ),
                              ],
                            );
                          },
                        );

                        if (proceed == true) {
                          // Post Audit Log
                          final reasonsStr = reasons.join(', ');
                          await GeminiService.logSuitabilityAudit(
                            farm.id!,
                            cropName,
                            score.toDouble(),
                            reasonsStr,
                            !isSuitable,
                          );

                          // Plant the crop
                          final newCrops = List<PlantedCropModel>.from(farm.plantedCrops);
                          if (!newCrops.any((c) => c.cropName.toLowerCase() == cropName.toLowerCase())) {
                            newCrops.add(PlantedCropModel(
                              cropName: cropName,
                              plantedDate: DateTime.now(),
                              landArea: val ?? 0.0,
                            ));
                            
                            final newPreferred = List<String>.from(farm.preferredCrops);
                            if (!newPreferred.any((p) => p.toLowerCase() == cropName.toLowerCase())) {
                              newPreferred.add(cropName);
                            }

                            await FirestoreService().setData(
                              path: 'farms/${farm.id}',
                              data: {
                                'plantedCrops': newCrops.map((c) => c.toMap()).toList(),
                                'preferredCrops': newPreferred,
                              },
                              merge: true,
                            );
                          }
                        }
                      }
                    }
                  },
                  child: Text('Plant Crop'.tr(context)),
                ),
            ],
          );
        }
      ),
    );
  }
}
