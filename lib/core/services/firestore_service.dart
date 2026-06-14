import 'package:cloud_firestore/cloud_firestore.dart';
import 'dart:developer' as dev;

class FirestoreService {
  final FirebaseFirestore _db = FirebaseFirestore.instance;

  // Generic Create/Update
  Future<void> setData({
    required String path,
    required Map<String, dynamic> data,
    bool merge = true,
  }) async {
    try {
      final reference = _db.doc(path);
      await reference.set(data, SetOptions(merge: merge));
    } catch (e) {
      dev.log('Firestore Set Error: $e');
      rethrow;
    }
  }

  // Generic Add (with auto-generated ID)
  Future<DocumentReference> addData({
    required String collectionPath,
    required Map<String, dynamic> data,
  }) async {
    try {
      return await _db.collection(collectionPath).add(data);
    } catch (e) {
      dev.log('Firestore Add Error: $e');
      rethrow;
    }
  }

  // Generic Get Single Document
  Future<DocumentSnapshot> getDocument(String path) async {
    try {
      return await _db.doc(path).get();
    } catch (e) {
      dev.log('Firestore Get Error: $e');
      rethrow;
    }
  }

  // Generic Stream of Collection
  Stream<QuerySnapshot> streamCollection(String path) {
    return _db.collection(path).snapshots();
  }

  // Generic Stream of Single Document
  Stream<DocumentSnapshot> streamDocument(String path) {
    return _db.doc(path).snapshots();
  }

  // Generic Delete
  Future<void> deleteDocument(String path) async {
    try {
      await _db.doc(path).delete();
    } catch (e) {
      dev.log('Firestore Delete Error: $e');
      rethrow;
    }
  }

  // Batch write (example)
  Future<void> performBatchOperation(List<Map<String, dynamic>> operations) async {
    final batch = _db.batch();
    // Logic here
    await batch.commit();
  }
}
