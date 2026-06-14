import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class FertilizerRecommendation {
  final String fertilizerName;
  final String applicationTime;
  final String reason;
  
  FertilizerRecommendation({
    required this.fertilizerName,
    required this.applicationTime,
    required this.reason,
  });
}

class FarmTask {
  final String title;
  final String category; // Fertilizer, Pesticide, Irrigation, Harvest, General
  final bool isCompleted;
  final String time;
  final IconData icon;
  final Color color;

  FarmTask({
    required this.title,
    required this.category,
    this.isCompleted = false,
    required this.time,
    required this.icon,
    required this.color,
  });
}

class GuidanceDay {
  final DateTime date;
  final String dailyTip;
  final List<FarmTask> tasks;
  final int cropAgeDays;

  GuidanceDay({
    required this.date,
    required this.dailyTip,
    required this.tasks,
    required this.cropAgeDays,
  });
}

class AssistantData {
  static List<GuidanceDay> getGuidanceForCrop({
    required String cropName,
    required DateTime plantedDate,
  }) {
    final now = DateTime.now();
    final todayStart = DateTime(now.year, now.month, now.day);
    
    // We will generate a list of 5 days: today - 2 days to today + 2 days
    return List.generate(5, (index) {
      final targetDate = todayStart.add(Duration(days: index - 2));
      final ageDays = targetDate.difference(DateTime(plantedDate.year, plantedDate.month, plantedDate.day)).inDays;
      
      if (ageDays < 0) {
        // Pre-planting
        return GuidanceDay(
          date: targetDate,
          cropAgeDays: ageDays,
          dailyTip: "Pre-planting preparation stage. Check soil health and prepare beds for $cropName.",
          tasks: [
            FarmTask(
              title: "Soil Bed Preparation",
              category: "General",
              time: "08:00 AM",
              icon: Icons.layers_outlined,
              color: Colors.brown,
            ),
            FarmTask(
              title: "Basal Compost Application",
              category: "Fertilizer",
              time: "11:00 AM",
              icon: Icons.eco_outlined,
              color: Colors.green,
            ),
          ],
        );
      } else if (ageDays <= 3) {
        // Germination Stage
        return GuidanceDay(
          date: targetDate,
          cropAgeDays: ageDays,
          dailyTip: "Day $ageDays since planting $cropName. Germination phase. Ensure optimal moisture.",
          tasks: [
            FarmTask(
              title: "Light Irrigation Cycle",
              category: "Irrigation",
              time: "07:00 AM",
              icon: Icons.water_drop_rounded,
              color: Colors.cyan,
            ),
            FarmTask(
              title: "Check Soil Crust & Compaction",
              category: "General",
              time: "04:30 PM",
              icon: Icons.science_outlined,
              color: Colors.orange,
            ),
          ],
        );
      } else if (ageDays <= 14) {
        // Seedling / Early Vegetative Stage
        return GuidanceDay(
          date: targetDate,
          cropAgeDays: ageDays,
          dailyTip: "Day $ageDays since planting $cropName. Seedlings are establishing roots. Watch out for weeds.",
          tasks: [
            FarmTask(
              title: "Weed Control & Scouting",
              category: "General",
              time: "08:00 AM",
              icon: Icons.grass,
              color: Colors.green,
            ),
            FarmTask(
              title: "Apply Starter Fertilizer",
              category: "Fertilizer",
              time: "10:30 AM",
              icon: Icons.opacity_rounded,
              color: Colors.blue,
            ),
          ],
        );
      } else if (ageDays <= 45) {
        // Mid Vegetative / Growth Stage
        return GuidanceDay(
          date: targetDate,
          cropAgeDays: ageDays,
          dailyTip: "Day $ageDays since planting $cropName. Rapid growth phase. Crop needs high nitrogen and pest scouting.",
          tasks: [
            FarmTask(
              title: "Nitrogen (Urea) Top Dressing",
              category: "Fertilizer",
              time: "08:00 AM",
              icon: Icons.opacity_rounded,
              color: Colors.blue,
            ),
            FarmTask(
              title: "Pest Scouting & Spraying",
              category: "Pesticide",
              time: "10:30 AM",
              icon: Icons.bug_report_outlined,
              color: Colors.orange,
            ),
            FarmTask(
              title: "Deep Drip Irrigation",
              category: "Irrigation",
              time: "05:00 PM",
              icon: Icons.water_drop_rounded,
              color: Colors.cyan,
            ),
          ],
        );
      } else if (ageDays <= 75) {
        // Flowering / Fruiting Stage
        return GuidanceDay(
          date: targetDate,
          cropAgeDays: ageDays,
          dailyTip: "Day $ageDays since planting $cropName. Flowering & grain filling. Maintain consistent watering.",
          tasks: [
            FarmTask(
              title: "Potassium/Phosphorus Spray",
              category: "Fertilizer",
              time: "07:00 AM",
              icon: Icons.eco_outlined,
              color: Colors.brown,
            ),
            FarmTask(
              title: "Fungal Disease Prevention",
              category: "Pesticide",
              time: "09:30 AM",
              icon: Icons.bug_report_outlined,
              color: Colors.red,
            ),
          ],
        );
      } else {
        // Maturity & Harvest Stage
        return GuidanceDay(
          date: targetDate,
          cropAgeDays: ageDays,
          dailyTip: "Day $ageDays since planting $cropName. Crop has reached maturity. Prepare for harvesting.",
          tasks: [
            FarmTask(
              title: "Crop Moisture Assessment",
              category: "General",
              time: "09:00 AM",
              icon: Icons.shutter_speed_outlined,
              color: Colors.amber,
            ),
            FarmTask(
              title: "Harvest & Storage Prep",
              category: "Harvest",
              time: "02:00 PM",
              icon: Icons.settings_outlined,
              color: Colors.grey,
            ),
          ],
        );
      }
    });
  }

  static List<FertilizerRecommendation> getFertilizerSchedule(String cropName) {
    if (cropName.toLowerCase().contains('wheat')) {
      return [
        FertilizerRecommendation(fertilizerName: 'DAP (Diammonium Phosphate)', applicationTime: 'At Planting', reason: 'Essential for strong root development.'),
        FertilizerRecommendation(fertilizerName: 'Urea (Nitrogen)', applicationTime: 'Day 21 (Crown Root Initiation)', reason: 'Boosts early vegetative growth.'),
        FertilizerRecommendation(fertilizerName: 'Potash (MOP)', applicationTime: 'Day 45 (Pre-flowering)', reason: 'Improves grain weight and drought resistance.'),
      ];
    } else if (cropName.toLowerCase().contains('rice') || cropName.toLowerCase().contains('paddy')) {
      return [
        FertilizerRecommendation(fertilizerName: 'NPK (Complex)', applicationTime: 'Basal Dose (At Transplanting)', reason: 'Balanced early nutrient supply.'),
        FertilizerRecommendation(fertilizerName: 'Urea', applicationTime: 'Day 15 & Day 45', reason: 'Promotes tillering and panicle growth.'),
        FertilizerRecommendation(fertilizerName: 'Zinc Sulphate', applicationTime: 'Day 20', reason: 'Prevents Khaira disease and improves yield.'),
      ];
    } else if (cropName.toLowerCase().contains('cotton')) {
      return [
        FertilizerRecommendation(fertilizerName: 'DAP & Potash', applicationTime: 'Basal Dose (At Sowing)', reason: 'Provides initial boost for seedling vigour.'),
        FertilizerRecommendation(fertilizerName: 'Urea', applicationTime: 'Day 30, 60, & 90', reason: 'Maintains vegetative growth alongside boll formation.'),
        FertilizerRecommendation(fertilizerName: 'Magnesium Sulphate', applicationTime: 'Day 60 (Squaring stage)', reason: 'Prevents leaf reddening.'),
      ];
    } else {
      return [
        FertilizerRecommendation(fertilizerName: 'NPK 19:19:19', applicationTime: 'Day 15', reason: 'Balanced early growth.'),
        FertilizerRecommendation(fertilizerName: 'Urea', applicationTime: 'Day 30', reason: 'Foliar growth boost.'),
        FertilizerRecommendation(fertilizerName: 'Potassium', applicationTime: 'Pre-flowering', reason: 'Better fruit set and quality.'),
      ];
    }
  }

  static List<GuidanceDay> getMockGuidance() {
    return getGuidanceForCrop(cropName: 'Mock Crop', plantedDate: DateTime.now());
  }

  static IconData _getIconForCategory(String category) {
    switch (category.toLowerCase()) {
      case 'fertilizer': return Icons.opacity_rounded;
      case 'irrigation': return Icons.water_drop_rounded;
      case 'pesticide': return Icons.bug_report_outlined;
      case 'harvest': return Icons.settings_outlined;
      default: return Icons.grass;
    }
  }

  static Color _getColorForCategory(String category) {
    switch (category.toLowerCase()) {
      case 'fertilizer': return Colors.blue;
      case 'irrigation': return Colors.cyan;
      case 'pesticide': return Colors.orange;
      case 'harvest': return Colors.amber;
      default: return Colors.green;
    }
  }

  static List<GuidanceDay> parseLiveGuidance(String jsonStr, DateTime plantedDate) {
    try {
      final List<dynamic> parsed = json.decode(jsonStr);
      final now = DateTime.now();
      final todayStart = DateTime(now.year, now.month, now.day);
      final List<GuidanceDay> days = [];

      for (int i = 0; i < 5; i++) {
        final targetDate = todayStart.add(Duration(days: i - 2));
        final ageDays = targetDate.difference(DateTime(plantedDate.year, plantedDate.month, plantedDate.day)).inDays;
        
        if (i < parsed.length) {
          final dayData = parsed[i];
          final List<dynamic> tasksData = dayData['tasks'] ?? [];
          final tasks = tasksData.map((t) => FarmTask(
            title: t['title'] ?? 'Task',
            category: t['category'] ?? 'General',
            time: t['time'] ?? '08:00 AM',
            icon: _getIconForCategory(t['category'] ?? ''),
            color: _getColorForCategory(t['category'] ?? ''),
          )).toList();

          days.add(GuidanceDay(
            date: targetDate,
            dailyTip: dayData['dailyTip'] ?? 'Focus on general crop health today.',
            tasks: tasks,
            cropAgeDays: ageDays,
          ));
        }
      }
      if (days.length == 5) return days;
    } catch (e) {
      if (kDebugMode) print('Failed to parse dynamic guidance: $e');
    }
    // Fallback if parsing fails
    return getGuidanceForCrop(cropName: 'Fallback', plantedDate: plantedDate);
  }
}
