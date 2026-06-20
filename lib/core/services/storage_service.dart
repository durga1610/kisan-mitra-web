import 'dart:io';
import 'package:firebase_storage/firebase_storage.dart';
import 'dart:developer' as dev;
import '../config/api_config.dart';

class StorageService {
  final FirebaseStorage _storage = FirebaseStorage.instance;

  // Upload File
  Future<String> uploadFile({
    required String path,
    required File file,
    String? contentType,
  }) async {
    if (!ApiConfig.enableFirebaseStorage) {
      dev.log('Storage Upload skipped: Storage is disabled.');
      return '';
    }
    try {
      final ref = _storage.ref().child(path);
      final metadata = SettableMetadata(contentType: contentType);
      
      final uploadTask = ref.putFile(file, metadata);
      final snapshot = await uploadTask;
      
      return await snapshot.ref.getDownloadURL();
    } catch (e) {
      dev.log('Storage Upload Error: $e');
      rethrow;
    }
  }

  // Delete File
  Future<void> deleteFile(String path) async {
    if (!ApiConfig.enableFirebaseStorage) {
      dev.log('Storage Delete skipped: Storage is disabled.');
      return;
    }
    try {
      await _storage.ref().child(path).delete();
    } catch (e) {
      dev.log('Storage Delete Error: $e');
      rethrow;
    }
  }

  // Get Download URL
  Future<String> getDownloadUrl(String path) async {
    if (!ApiConfig.enableFirebaseStorage) {
      dev.log('Storage URL fetch skipped: Storage is disabled.');
      return '';
    }
    try {
      return await _storage.ref().child(path).getDownloadURL();
    } catch (e) {
      dev.log('Storage URL Error: $e');
      rethrow;
    }
  }
}
