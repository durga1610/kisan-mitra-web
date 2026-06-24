import 'package:cloud_firestore/cloud_firestore.dart';
import '../../core/models/farm_model.dart';

class FarmRepository {
  static final FarmRepository _instance = FarmRepository._internal();
  factory FarmRepository() => _instance;
  FarmRepository._internal();

  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  Stream<List<FarmModel>> listenToFarms(String uid) {
    return _firestore
        .collection('farms')
        .where('ownerId', isEqualTo: uid)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) => FarmModel.fromMap(doc.data(), docId: doc.id)).toList();
    });
  }

  Future<void> updateFarmCoordinates(String farmId, double lat, double lon) async {
    await _firestore.collection('farms').doc(farmId).update({
      'latitude': lat,
      'longitude': lon,
    });
  }

  Future<void> updateSelectedFarmId(String uid, String farmId) async {
    await _firestore.collection('users').doc(uid).update({
      'selectedFarmId': farmId,
    });
  }
}
