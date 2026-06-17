import 'package:cloud_firestore/cloud_firestore.dart';

class DiseaseReport {
  final String? id;
  final String userId;
  final String imageUrl;
  final String plantName;
  final String diseaseName;
  final double confidence;
  final String severity;
  final String symptoms;
  final String causes;
  final String treatment;
  final String organicTreatment;
  final String prevention;
  final String suggestedProducts;
  final String explanation;
  final String gradcamBase64;
  final List<Map<String, dynamic>> topPredictions;
  final DateTime timestamp;
  final String? warning;

  DiseaseReport({
    this.id,
    required this.userId,
    required this.imageUrl,
    required this.plantName,
    required this.diseaseName,
    required this.confidence,
    required this.severity,
    required this.symptoms,
    required this.causes,
    required this.treatment,
    required this.organicTreatment,
    required this.prevention,
    required this.suggestedProducts,
    required this.explanation,
    required this.gradcamBase64,
    this.topPredictions = const [],
    required this.timestamp,
    this.warning,
  });

  Map<String, dynamic> toMap() {
    return {
      'uid': userId,
      'imageUrl': imageUrl,
      'plantName': plantName,
      'diseaseName': diseaseName,
      'confidence': confidence,
      'severity': severity,
      'symptoms': symptoms,
      'causes': causes,
      'treatment': treatment,
      'organicTreatment': organicTreatment,
      'prevention': prevention,
      'suggestedProducts': suggestedProducts,
      'explanation': explanation,
      'gradcamBase64': gradcamBase64,
      'topPredictions': topPredictions,
      'timestamp': Timestamp.fromDate(timestamp),
      'warning': warning,
    };
  }

  factory DiseaseReport.fromMap(Map<String, dynamic> map, String id) {
    return DiseaseReport(
      id: id,
      userId: map['uid'] ?? '',
      imageUrl: map['imageUrl'] ?? '',
      plantName: map['plantName'] ?? 'Unknown',
      diseaseName: map['diseaseName'] ?? 'Unknown',
      confidence: (map['confidence'] ?? 0.0).toDouble(),
      severity: map['severity'] ?? 'Low',
      symptoms: map['symptoms'] ?? 'No symptoms data',
      causes: map['causes'] ?? 'No causes data',
      treatment: map['treatment'] ?? 'No treatment data',
      organicTreatment: map['organicTreatment'] ?? 'No organic treatment data',
      prevention: map['prevention'] ?? 'No prevention data',
      suggestedProducts: map['suggestedProducts'] ?? 'No product suggestions',
      explanation: map['explanation'] ?? 'No explanation data',
      gradcamBase64: map['gradcamBase64'] ?? '',
      topPredictions: List<Map<String, dynamic>>.from(
        (map['topPredictions'] ?? map['predictions'] ?? [])
            .map((item) => Map<String, dynamic>.from(item as Map)),
      ),
      timestamp: (map['timestamp'] as Timestamp).toDate(),
      warning: map['warning'],
    );
  }
}
