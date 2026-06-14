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
  final String prevention;
  final String suggestedProducts;
  final DateTime timestamp;

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
    required this.prevention,
    required this.suggestedProducts,
    required this.timestamp,
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
      'prevention': prevention,
      'suggestedProducts': suggestedProducts,
      'timestamp': Timestamp.fromDate(timestamp),
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
      prevention: map['prevention'] ?? 'No prevention data',
      suggestedProducts: map['suggestedProducts'] ?? 'No product suggestions',
      timestamp: (map['timestamp'] as Timestamp).toDate(),
    );
  }
}
