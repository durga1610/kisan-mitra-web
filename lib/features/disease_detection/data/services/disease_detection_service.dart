import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';
import '../../../../core/services/gemini_service.dart';
import '../models/disease_report.dart';

class DiseaseDetectionService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseStorage _storage = FirebaseStorage.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;

  Future<DiseaseReport?> detectAndSave(XFile imageFile, {String languageCode = 'en'}) async {
    try {
      final user = _auth.currentUser;
      if (user == null) throw Exception('User not authenticated');

      // 1. Get bytes for AI analysis and upload
      final imageBytes = await imageFile.readAsBytes();

      // 2. Call AI Analysis directly with local bytes first! (Much faster UX)
      final geminiService = GeminiService(languageCode: languageCode);
      final aiResponse = await geminiService.detectDisease(imageBytes);
      
      // 3. Parse AI Response
      final reportData = _parseAIResponse(aiResponse);

      // 4. Fire-and-forget Firebase Storage upload (Do not await!)
      final fileName = 'disease_${DateTime.now().millisecondsSinceEpoch}.jpg';
      final storageRef = _storage.ref().child('disease_scans/${user.uid}/$fileName');
      
      // We do not await this, so it won't block the UI
      storageRef.putData(
        imageBytes,
        SettableMetadata(contentType: 'image/jpeg'),
      ).then((uploadTask) async {
        final imageUrl = await uploadTask.ref.getDownloadURL();
        
        // Save to Firestore after upload succeeds
        final report = DiseaseReport(
          userId: user.uid,
          imageUrl: imageUrl,
          plantName: reportData['Plant'] ?? 'Unknown',
          diseaseName: reportData['Disease'] ?? 'Unknown',
          confidence: double.tryParse(reportData['Confidence'] ?? '0.0') ?? 0.0,
          severity: reportData['Severity'] ?? 'Unknown',
          symptoms: reportData['Symptoms'] ?? 'N/A',
          causes: reportData['Causes'] ?? 'N/A',
          treatment: reportData['Treatment'] ?? 'N/A',
          prevention: reportData['Prevention'] ?? 'N/A',
          suggestedProducts: reportData['Suggested Products'] ?? 'N/A',
          timestamp: DateTime.now(),
        );
        await _firestore.collection('disease_reports').add(report.toMap());
      }).catchError((e) {
        // Silently catch background upload failure
      });

      // 5. Return result to UI INSTANTLY without waiting for Firebase
      return DiseaseReport(
        userId: user.uid,
        imageUrl: imageFile.path, // Use the local file path to render instantly
        plantName: reportData['Plant'] ?? 'Unknown',
        diseaseName: reportData['Disease'] ?? 'Unknown',
        confidence: double.tryParse(reportData['Confidence'] ?? '0.0') ?? 0.0,
        severity: reportData['Severity'] ?? 'Unknown',
        symptoms: reportData['Symptoms'] ?? 'N/A',
        causes: reportData['Causes'] ?? 'N/A',
        treatment: reportData['Treatment'] ?? 'N/A',
        prevention: reportData['Prevention'] ?? 'N/A',
        suggestedProducts: reportData['Suggested Products'] ?? 'N/A',
        timestamp: DateTime.now(),
      );

    } catch (e) {
      debugPrint('Error in disease detection: $e');
      rethrow;
    }
  }

  Map<String, String> _parseAIResponse(String response) {
    final Map<String, String> data = {};
    final lines = response.split('\n');
    
    for (var line in lines) {
      if (line.contains(':')) {
        final parts = line.split(':');
        final key = parts[0].trim();
        final value = parts.sublist(1).join(':').trim();
        data[key] = value;
      }
    }
    return data;
  }

  Stream<List<DiseaseReport>> getHistory() {
    final user = _auth.currentUser;
    if (user == null) return Stream.value([]);

    return _firestore
        .collection('disease_reports')
        .where('uid', isEqualTo: user.uid)
        .orderBy('timestamp', descending: true)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) => DiseaseReport.fromMap(doc.data(), doc.id)).toList();
    });
  }
}
