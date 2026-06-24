import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/providers/farm_provider.dart';
import '../../../../core/config/api_config.dart';

class FertilizerScreen extends StatefulWidget {
  const FertilizerScreen({super.key});

  @override
  State<FertilizerScreen> createState() => _FertilizerScreenState();
}

class _FertilizerScreenState extends State<FertilizerScreen> {
  Map<String, Map<String, dynamic>> _recommendations = {};
  bool _isLoading = true;

  bool _isInitialized = false;
  String? _lastFarmId;

  @override
  void initState() {
    super.initState();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final farmProvider = Provider.of<FarmProvider>(context);
    final farmId = farmProvider.selectedFarm?.id;
    if (!_isInitialized || _lastFarmId != farmId) {
      _isInitialized = true;
      _lastFarmId = farmId;
      setState(() {
        _isLoading = true;
      });
      _loadRecommendations();
    }
  }

  Future<void> _loadRecommendations() async {
    final farmProvider = Provider.of<FarmProvider>(context, listen: false);
    final farm = farmProvider.selectedFarm;
    if (farm == null || farm.plantedCrops.isEmpty) {
      setState(() {
        _isLoading = false;
      });
      return;
    }

    try {
      final String farmId = farm.id ?? 'default';
      final Map<String, Map<String, dynamic>> loadedRecs = {};
      final token = await FirebaseAuth.instance.currentUser?.getIdToken();
      
      for (final crop in farm.plantedCrops) {
        final response = await http.post(
          Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/fertilizer/recommend'),
          headers: {
            'Content-Type': 'application/json',
            if (token != null) 'Authorization': 'Bearer $token',
          },
          body: jsonEncode({
            'farmId': farmId,
            'cropId': crop.cropName,
            'plantedDate': crop.plantedDate.toIso8601String(),
          }),
        ).timeout(const Duration(seconds: 45));

        if (response.statusCode == 200) {
          loadedRecs[crop.cropName] = jsonDecode(response.body) as Map<String, dynamic>;
        }
      }

      setState(() {
        _recommendations = loadedRecs;
        _isLoading = false;
      });
    } catch (e) {
      if (kDebugMode) print('Error loading fertilizer recommendations: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final farmProvider = Provider.of<FarmProvider>(context);
    final farm = farmProvider.selectedFarm;

    if (farm == null || farm.plantedCrops.isEmpty) {
      return Scaffold(
        appBar: AppBar(
          title: Text(
            'Fertilizer Advice',
            style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18),
          ),
        ),
        body: Center(
          child: Text(
            'No crops planted to show fertilizer advice.',
            style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
          ),
        ),
      );
    }

    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(
          title: Text(
            'Fertilizer Advice',
            style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18),
          ),
        ),
        body: const Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Fertilizer Advice',
          style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          setState(() {
            _isLoading = true;
          });
          await _loadRecommendations();
        },
        notificationPredicate: (notification) => kIsWeb ? defaultScrollNotificationPredicate(notification) : false,
        child: ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: farm.plantedCrops.length,
          itemBuilder: (context, index) {
            final crop = farm.plantedCrops[index];
            final rec = _recommendations[crop.cropName];

            if (rec == null) {
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 8.0),
                child: Card(
                  elevation: 1,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          crop.cropName,
                          style: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 15),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Apply balanced NPK fertilizer (19:19:19) at 2.5 kg/acre. '
                          'Supplement with organic farmyard manure for soil health.',
                          style: GoogleFonts.poppins(fontSize: 13, color: Colors.grey[700]),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          'Tap refresh to load personalized advice.',
                          style: GoogleFonts.poppins(
                            fontSize: 12,
                            color: Theme.of(context).colorScheme.primary,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }

            final stage = rec['stage'] ?? 'Vegetative';
            final age = rec['age'] ?? 0;
            final recommendation = rec['recommendation'] ?? 'Urea';
            final dosage = rec['dosage'] ?? '25 kg/acre';
            final scheduleRaw = rec['schedule'] as List?;
            final schedule = scheduleRaw?.map((item) {
              if (item is Map) {
                return Map<String, dynamic>.from(item);
              }
              return <String, dynamic>{};
            }).toList() ?? [];

            if (schedule.isEmpty) {
              schedule.add({
                'day': 'Day 1',
                'fertilizer': recommendation,
                'dosage': dosage,
              });
            }

            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Crop Header with custom colors
                Container(
                  width: double.infinity,
                  margin: const EdgeInsets.symmetric(vertical: 12),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF2E7D32), Color(0xFF4CAF50)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.green.withValues(alpha: 0.15),
                        blurRadius: 8,
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
                          Row(
                            children: [
                              const Icon(Icons.eco, color: Colors.white, size: 28),
                              const SizedBox(width: 12),
                              Text(
                                crop.cropName,
                                style: GoogleFonts.poppins(
                                  fontSize: 20,
                                  fontWeight: FontWeight.w700,
                                  color: Colors.white,
                                ),
                              ),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: Colors.white.withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              stage.toUpperCase(),
                              style: GoogleFonts.poppins(
                                fontSize: 12,
                                fontWeight: FontWeight.w800,
                                color: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          const Icon(Icons.calendar_today_outlined, color: Colors.white70, size: 16),
                          const SizedBox(width: 6),
                          Text(
                            'Current Age: $age Days',
                            style: GoogleFonts.poppins(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: Colors.white.withValues(alpha: 0.9),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                
                // Complete Schedule Title
                Padding(
                  padding: const EdgeInsets.only(left: 4, bottom: 8, top: 8),
                  child: Text(
                    'Complete Fertilizer Schedule',
                    style: GoogleFonts.poppins(
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.8),
                    ),
                  ),
                ),
                
                // List of schedules
                ...schedule.map<Widget>((entry) {
                  final entryDay = entry['day'] ?? 'Day 1';
                  final entryFertilizer = entry['fertilizer'] ?? 'Urea';
                  final entryDosage = entry['dosage'] ?? '25 kg/acre';
                  final entryStage = entry['stage'] ?? '';
                  final isCurrentStage = entryStage.toString().toLowerCase() == stage.toString().toLowerCase();
                  
                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Theme.of(context).cardColor,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: isCurrentStage ? const Color(0xFF4CAF50).withValues(alpha: 0.5) : AppColors.divider,
                        width: isCurrentStage ? 1.5 : 1.0,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: isCurrentStage 
                            ? const Color(0xFF2E7D32).withValues(alpha: 0.04)
                            : Colors.black.withValues(alpha: 0.02),
                          blurRadius: 6,
                          offset: const Offset(0, 3),
                        ),
                      ],
                    ),
                    child: Row(
                      children: [
                        // Day indicator badge
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                          decoration: BoxDecoration(
                            color: isCurrentStage ? const Color(0xFFE8F5E9) : const Color(0xFFF5F5F5),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: isCurrentStage ? const Color(0xFFC8E6C9) : const Color(0xFFE0E0E0),
                            ),
                          ),
                          child: Text(
                            entryDay,
                            style: GoogleFonts.poppins(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: isCurrentStage ? const Color(0xFF2E7D32) : Colors.grey[700],
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        
                        // Fertilizer & dosage info
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                entryFertilizer,
                                style: GoogleFonts.poppins(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w700,
                                  color: Theme.of(context).colorScheme.onSurface,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Dosage: $entryDosage',
                                style: GoogleFonts.poppins(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500,
                                  color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                                ),
                              ),
                            ],
                          ),
                        ),
                        
                        // Icon / Current Stage Badge
                        if (isCurrentStage)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0xFFE8F5E9),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              'CURRENT',
                              style: GoogleFonts.poppins(
                                fontSize: 9,
                                fontWeight: FontWeight.w800,
                                color: const Color(0xFF2E7D32),
                              ),
                            ),
                          )
                        else
                          const Icon(
                            Icons.check_circle_outline,
                            color: Colors.grey,
                            size: 20,
                          ),
                      ],
                    ),
                  );
                }),
                const SizedBox(height: 16),
              ],
            );
          },
        ),
      ),
    );
  }
}
