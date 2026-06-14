import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/profit_models.dart';

class ProfitService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseAuth _auth = FirebaseAuth.instance;

  String? get _uid => _auth.currentUser?.uid;

  Future<void> saveProfitRecord(CropProfit record) async {
    if (_uid == null) throw Exception('User not logged in');
    
    await _firestore
        .collection('users')
        .doc(_uid)
        .collection('profit_records')
        .add(record.toMap());
  }

  Stream<List<CropProfit>> streamProfitRecords() {
    if (_uid == null) return Stream.value([]);

    return _firestore
        .collection('users')
        .doc(_uid)
        .collection('profit_records')
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) {
        return CropProfit.fromMap(doc.id, doc.data());
      }).toList();
    });
  }

  Future<void> deleteRecord(String id) async {
    if (_uid == null) return;
    await _firestore
        .collection('users')
        .doc(_uid)
        .collection('profit_records')
        .doc(id)
        .delete();
  }
}
