import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

// ── Schedule ──────────────────────────────────────────────────────────────────

class DailySchedule {
  final List<String> morning;
  final List<String> afternoon;
  final List<String> evening;

  const DailySchedule({
    required this.morning,
    required this.afternoon,
    required this.evening,
  });

  factory DailySchedule.fromMap(Map<String, dynamic> map) {
    return DailySchedule(
      morning:  List<String>.from(map['morning']   ?? []),
      afternoon: List<String>.from(map['afternoon'] ?? []),
      evening:  List<String>.from(map['evening']   ?? []),
    );
  }
}

// ── Recommendation ────────────────────────────────────────────────────────────

class AIRecommendation {
  final String type;   // weather | fertilizer | disease | irrigation | harvest | general
  final String icon;
  final String title;
  final String detail;

  const AIRecommendation({
    required this.type,
    required this.icon,
    required this.title,
    required this.detail,
  });

  factory AIRecommendation.fromMap(Map<String, dynamic> map) {
    return AIRecommendation(
      type:   map['type']   ?? 'general',
      icon:   map['icon']   ?? 'info',
      title:  map['title']  ?? '',
      detail: map['detail'] ?? '',
    );
  }

  Color get typeColor {
    switch (type) {
      case 'weather':     return const Color(0xFF0288D1);
      case 'fertilizer':  return const Color(0xFF43A047);
      case 'disease':     return const Color(0xFFE53935);
      case 'irrigation':  return const Color(0xFF00ACC1);
      case 'harvest':     return const Color(0xFFF9A825);
      default:            return const Color(0xFF7E57C2);
    }
  }

  IconData get iconData {
    switch (icon) {
      case 'water_drop':     return Icons.water_drop_rounded;
      case 'thermostat':     return Icons.thermostat_rounded;
      case 'ac_unit':        return Icons.ac_unit_rounded;
      case 'bug_report':     return Icons.bug_report_rounded;
      case 'grass':          return Icons.grass_rounded;
      case 'eco':            return Icons.eco_rounded;
      case 'science':        return Icons.science_rounded;
      case 'opacity':        return Icons.opacity_rounded;
      case 'local_florist':  return Icons.local_florist_rounded;
      case 'water':          return Icons.water_rounded;
      case 'agriculture':    return Icons.agriculture_rounded;
      case 'wb_sunny':       return Icons.wb_sunny_rounded;
      case 'search':         return Icons.search_rounded;
      default:               return Icons.lightbulb_outline_rounded;
    }
  }
}

// ── Alert ─────────────────────────────────────────────────────────────────────

class DailyAlert {
  final String level;    // info | warning | danger
  final String icon;
  final String message;

  const DailyAlert({
    required this.level,
    required this.icon,
    required this.message,
  });

  factory DailyAlert.fromMap(Map<String, dynamic> map) {
    return DailyAlert(
      level:   map['level']   ?? 'info',
      icon:    map['icon']    ?? 'info',
      message: map['message'] ?? '',
    );
  }

  Color get levelColor {
    switch (level) {
      case 'danger':  return const Color(0xFFE53935);
      case 'warning': return const Color(0xFFFB8C00);
      default:        return const Color(0xFF0288D1);
    }
  }

  Color get levelBg {
    switch (level) {
      case 'danger':  return const Color(0xFFFFEBEE);
      case 'warning': return const Color(0xFFFFF3E0);
      default:        return const Color(0xFFE1F5FE);
    }
  }

  IconData get iconData {
    switch (icon) {
      case 'thermostat':           return Icons.thermostat_rounded;
      case 'ac_unit':              return Icons.ac_unit_rounded;
      case 'cloud_outlined':       return Icons.cloud_rounded;
      case 'coronavirus_outlined': return Icons.coronavirus_rounded;
      case 'agriculture':          return Icons.agriculture_rounded;
      case 'check_circle_outlined':return Icons.check_circle_rounded;
      default:                     return Icons.info_rounded;
    }
  }
}

// ── DailyAssistant ────────────────────────────────────────────────────────────

class DailyAssistant {
  final String cropName;
  final int cropAgeDays;
  final String currentStageName;
  final String expectedHarvestDate;
  final String weatherSummary;
  final DailySchedule schedule;
  final List<AIRecommendation> recommendations;
  final List<DailyAlert> alerts;

  const DailyAssistant({
    required this.cropName,
    required this.cropAgeDays,
    required this.currentStageName,
    required this.expectedHarvestDate,
    required this.weatherSummary,
    required this.schedule,
    required this.recommendations,
    required this.alerts,
  });

  factory DailyAssistant.fromMap(Map<String, dynamic> map) {
    return DailyAssistant(
      cropName:            map['cropName']            ?? '',
      cropAgeDays:         (map['cropAgeDays'] as num?)?.toInt() ?? 0,
      currentStageName:    map['currentStageName']    ?? '',
      expectedHarvestDate: map['expectedHarvestDate'] ?? '',
      weatherSummary:      map['weatherSummary']      ?? '',
      schedule:            DailySchedule.fromMap(Map<String, dynamic>.from(map['schedule'] ?? {})),
      recommendations: (map['recommendations'] as List? ?? [])
          .map((r) => AIRecommendation.fromMap(Map<String, dynamic>.from(r)))
          .toList(),
      alerts: (map['alerts'] as List? ?? [])
          .map((a) => DailyAlert.fromMap(Map<String, dynamic>.from(a)))
          .toList(),
    );
  }

  /// Fallback for when backend is unavailable
  static DailyAssistant fallback({required String cropName, required int ageDays}) {
    String stage = 'Early Growth';
    if (ageDays <= 7)        stage = 'Land Preparation';
    else if (ageDays <= 30)  stage = 'Early Growth';
    else if (ageDays <= 60)  stage = 'Vegetative Growth';
    else if (ageDays <= 90)  stage = 'Flowering Stage';
    else if (ageDays <= 120) stage = 'Fruit Development';
    else                     stage = 'Harvest Stage';

    return DailyAssistant(
      cropName:            cropName,
      cropAgeDays:         ageDays,
      currentStageName:    stage,
      expectedHarvestDate: '',
      weatherSummary:      'Weather data unavailable',
      schedule: const DailySchedule(
        morning:   ['Check soil moisture and irrigate if needed.', 'Inspect crop canopy for disease or pest signs.'],
        afternoon: ['Perform weeding and field maintenance.', 'Monitor for pest activity.'],
        evening:   ['Check irrigation system for tomorrow.', 'Record today\'s field observations.'],
      ),
      recommendations: [
        const AIRecommendation(
          type: 'general', icon: 'eco',
          title: 'Daily Scouting',
          detail: 'Walk through the field and check crop health, soil moisture, and any pest or disease signs.',
        ),
      ],
      alerts: [
        const DailyAlert(
          level: 'info', icon: 'info',
          message: 'Weather data unavailable. Proceed based on direct field observation.',
        ),
      ],
    );
  }
}

// ── Legacy models (kept for compatibility) ────────────────────────────────────

class FertilizerRecommendation {
  final String fertilizerName;
  final String applicationTime;
  final String reason;

  const FertilizerRecommendation({
    required this.fertilizerName,
    required this.applicationTime,
    required this.reason,
  });
}

class AssistantData {
  static List<FertilizerRecommendation> getFertilizerSchedule(String cropName) {
    if (cropName.toLowerCase().contains('wheat')) {
      return [
        const FertilizerRecommendation(fertilizerName: 'DAP', applicationTime: 'At Planting', reason: 'Root development.'),
        const FertilizerRecommendation(fertilizerName: 'Urea', applicationTime: 'Day 21', reason: 'Vegetative growth.'),
        const FertilizerRecommendation(fertilizerName: 'Potash', applicationTime: 'Day 45', reason: 'Grain weight.'),
      ];
    } else if (cropName.toLowerCase().contains('rice') || cropName.toLowerCase().contains('paddy')) {
      return [
        const FertilizerRecommendation(fertilizerName: 'NPK Complex', applicationTime: 'At Transplanting', reason: 'Balanced nutrients.'),
        const FertilizerRecommendation(fertilizerName: 'Urea', applicationTime: 'Day 15 & Day 45', reason: 'Tillering.'),
        const FertilizerRecommendation(fertilizerName: 'Zinc Sulphate', applicationTime: 'Day 20', reason: 'Prevents Khaira disease.'),
      ];
    } else if (cropName.toLowerCase().contains('cotton')) {
      return [
        const FertilizerRecommendation(fertilizerName: 'DAP + Potash', applicationTime: 'At Sowing', reason: 'Seedling vigour.'),
        const FertilizerRecommendation(fertilizerName: 'Urea', applicationTime: 'Day 30, 60 & 90', reason: 'Vegetative + boll growth.'),
        const FertilizerRecommendation(fertilizerName: 'Magnesium Sulphate', applicationTime: 'Day 60', reason: 'Prevent leaf reddening.'),
      ];
    }
    return [
      const FertilizerRecommendation(fertilizerName: 'NPK 19:19:19', applicationTime: 'Day 15', reason: 'Balanced early growth.'),
      const FertilizerRecommendation(fertilizerName: 'Urea', applicationTime: 'Day 30', reason: 'Foliar growth.'),
      const FertilizerRecommendation(fertilizerName: 'Potassium', applicationTime: 'Pre-flowering', reason: 'Better fruit set.'),
    ];
  }

  /// Parse a DailyAssistant from the backend JSON response
  static DailyAssistant? parseDailyAssistant(String jsonStr) {
    try {
      final Map<String, dynamic> data = json.decode(jsonStr);
      return DailyAssistant.fromMap(data);
    } catch (e) {
      if (kDebugMode) print('[AssistantData] Failed to parse daily assistant: $e');
      return null;
    }
  }
}
