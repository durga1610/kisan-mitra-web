import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';
import '../../../../core/services/gemini_service.dart';
import '../../../../core/config/api_config.dart';
import '../models/disease_report.dart';

class DiseaseDetectionService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseStorage _storage = FirebaseStorage.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;

  Future<DiseaseReport?> detectAndSave(XFile imageFile, {String languageCode = 'en'}) async {
    try {
      final user = _auth.currentUser;
      final userId = user?.uid ?? 'guest_user';
      String? savedDocId;

      // 1. Get bytes for AI analysis and upload
      final imageBytes = await imageFile.readAsBytes();

      // 2. Call AI Analysis directly with local bytes first! (Much faster UX)
      final geminiService = GeminiService(languageCode: languageCode);
      final aiResponse = await geminiService.detectDisease(imageBytes, filename: imageFile.name);
      
      // 3. Handle errors
      if (aiResponse['status'] == 'quality_failed') {
        throw Exception(aiResponse['reason'] ?? 'Poor image quality. Please retake the photo.');
      }
      if (aiResponse['status'] == 'confidence_failed') {
        throw Exception(aiResponse['reason'] ?? 'Unable to identify disease accurately. Please upload a clearer image.');
      }

      String parseListOrString(dynamic val) {
        if (val is List) {
          return val.join(', ');
        }
        return val?.toString() ?? 'N/A';
      }

      final symptoms = parseListOrString(aiResponse['symptoms']);
      final treatment = parseListOrString(aiResponse['treatment']);
      final prevention = parseListOrString(aiResponse['prevention']);
      final plantName = aiResponse['plantName'] ?? aiResponse['crop'] ?? 'Unknown';
      final diseaseName = aiResponse['diseaseName'] ?? aiResponse['disease'] ?? 'Unknown';
      final topPredictions = List<Map<String, dynamic>>.from(
        (aiResponse['predictions'] ?? []).map((item) => Map<String, dynamic>.from(item as Map)),
      );

      // 4. Save to Firestore immediately so history works even if storage fails
      if (user != null) {
        try {
          final docRef = _firestore.collection('disease_reports').doc();
          savedDocId = docRef.id;
          
          final report = DiseaseReport(
            id: savedDocId,
            userId: userId,
            imageUrl: imageFile.path, // Save local path or fallback
            plantName: plantName,
            diseaseName: diseaseName,
            confidence: (aiResponse['confidence'] ?? 0.0).toDouble(),
            severity: aiResponse['severity'] ?? 'Unknown',
            symptoms: symptoms,
            causes: aiResponse['causes'] ?? 'N/A',
            treatment: treatment,
            organicTreatment: aiResponse['organicTreatment'] ?? 'N/A',
            prevention: prevention,
            suggestedProducts: aiResponse['suggestedProducts'] ?? 'N/A',
            explanation: aiResponse['explanation'] ?? 'N/A',
            gradcamBase64: aiResponse['gradcamBase64'] ?? '',
            topPredictions: topPredictions,
            timestamp: DateTime.now(),
            warning: aiResponse['warning']?.toString(),
            confidenceBand: aiResponse['confidenceBand']?.toString() ?? 'high',
            source: aiResponse['source'],
            imageBytes: imageBytes,
          );
          
          await docRef.set(report.toMap());

          // 5. Fire-and-forget Firebase Storage upload (background)
          if (ApiConfig.enableFirebaseStorage) {
            final fileName = 'disease_${DateTime.now().millisecondsSinceEpoch}.jpg';
            final storageRef = _storage.ref().child('disease_scans/$userId/$fileName');

            storageRef.putData(
              imageBytes,
              SettableMetadata(contentType: 'image/jpeg'),
            ).then((uploadTask) async {
              final imageUrl = await uploadTask.ref.getDownloadURL();
              // Update the report in Firestore with the remote image URL
              await docRef.update({'imageUrl': imageUrl});
            }).catchError((e) {
              debugPrint('Firebase Storage background upload failed: $e');
            });
          } else {
            debugPrint('Firebase Storage background upload skipped (disabled in config).');
          }
        } catch (e) {
          debugPrint('Firestore history saving failed: $e');
        }
      }

      // 6. Return result to UI INSTANTLY
      return DiseaseReport(
        id: savedDocId,
        userId: userId,
        imageUrl: imageFile.path,
        plantName: plantName,
        diseaseName: diseaseName,
        confidence: (aiResponse['confidence'] ?? 0.0).toDouble(),
        severity: aiResponse['severity'] ?? 'Unknown',
        symptoms: symptoms,
        causes: aiResponse['causes'] ?? 'N/A',
        treatment: treatment,
        organicTreatment: aiResponse['organicTreatment'] ?? 'N/A',
        prevention: prevention,
        suggestedProducts: aiResponse['suggestedProducts'] ?? 'N/A',
        explanation: aiResponse['explanation'] ?? 'N/A',
        gradcamBase64: aiResponse['gradcamBase64'] ?? '',
        topPredictions: topPredictions,
        timestamp: DateTime.now(),
        warning: aiResponse['warning']?.toString(),
        confidenceBand: aiResponse['confidenceBand']?.toString() ?? 'high',
        source: aiResponse['source'],
        imageBytes: imageBytes,  // V2: carry bytes for feedback dataset collection
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

    try {
      return _firestore
          .collection('disease_reports')
          .where('uid', isEqualTo: user.uid)
          .orderBy('timestamp', descending: true)
          .snapshots()
          .map((snapshot) {
        return snapshot.docs.map((doc) => DiseaseReport.fromMap(doc.data(), doc.id)).toList();
      }).handleError((e) {
        debugPrint('Error getting disease history: $e');
        return <DiseaseReport>[];
      });
    } catch (e) {
      debugPrint('Firestore history catch: $e');
      return Stream.value([]);
    }
  }

  Future<void> deleteReport(String reportId) async {
    try {
      await _firestore.collection('disease_reports').doc(reportId).delete();
    } catch (e) {
      debugPrint('Error deleting disease report: $e');
      rethrow;
    }
  }
}
