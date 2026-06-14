import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/providers/farm_provider.dart';
import '../../../ai_assistant/data/assistant_data.dart';

class FertilizerScreen extends StatelessWidget {
  const FertilizerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final farmProvider = Provider.of<FarmProvider>(context);
    final farm = farmProvider.selectedFarm;

    if (farm == null || farm.plantedCrops.isEmpty) {
      return Scaffold(
        
        appBar: AppBar(
          title: Text(
            'Fertilizer Schedule',
            style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18),
          ),
        ),
        body: Center(
          child: Text(
            'No crops planted to show fertilizer schedule.',
            style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
          ),
        ),
      );
    }

    return Scaffold(
      
      appBar: AppBar(
        title: Text(
          'Fertilizer Schedule',
          style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18),
        ),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: farm.plantedCrops.length,
        itemBuilder: (context, index) {
          final crop = farm.plantedCrops[index];
          final schedule = AssistantData.getFertilizerSchedule(crop.cropName);

          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 16),
                child: Text(
                  'Crop: ${crop.cropName}',
                  style: GoogleFonts.poppins(
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                    color: Theme.of(context).colorScheme.onSurface,
                  ),
                ),
              ),
              ...schedule.map((rec) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Theme.of(context).cardColor,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppColors.divider),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.02),
                            blurRadius: 8,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.green.withValues(alpha: 0.1),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(Icons.eco_outlined, color: Colors.green),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  rec.fertilizerName,
                                  style: GoogleFonts.poppins(
                                      fontSize: 15,
                                      fontWeight: FontWeight.w600,
                                      color: Theme.of(context).colorScheme.onSurface),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'When: ${rec.applicationTime}',
                                  style: GoogleFonts.poppins(
                                      fontSize: 13,
                                      fontWeight: FontWeight.w500,
                                      color: Theme.of(context).colorScheme.onSurface),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  rec.reason,
                                  style: GoogleFonts.poppins(
                                      fontSize: 12, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  )).toList(),
            ],
          );
        },
      ),
    );
  }
}
