import 'dart:async';
import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/farm_model.dart';
import 'auth_provider.dart';

class FarmProvider extends ChangeNotifier {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  
  List<FarmModel> _farms = [];
  FarmModel? _selectedFarm;
  int _selectedFarmIndex = 0;
  bool _isLoading = true;
  StreamSubscription<QuerySnapshot>? _farmsSubscription;

  List<FarmModel> get farms => _farms;
  FarmModel? get selectedFarm => _selectedFarm;
  int get selectedFarmIndex => _selectedFarmIndex;
  bool get isLoading => _isLoading;

  void update(AuthProvider authProvider) {
    final user = authProvider.user;
    if (user != null) {
      _listenToFarms(user.uid);
    } else {
      _clear();
    }
  }

  void _listenToFarms(String uid) {
    _farmsSubscription?.cancel();
    _isLoading = true;
    notifyListeners();

    _farmsSubscription = _firestore
        .collection('farms')
        .where('ownerId', isEqualTo: uid)
        .snapshots()
        .listen((snapshot) {
      _farms = snapshot.docs.map((doc) => FarmModel.fromMap(doc.data(), docId: doc.id)).toList();
      
      if (_farms.isNotEmpty) {
        // Ensure index is valid
        if (_selectedFarmIndex >= _farms.length) {
          _selectedFarmIndex = 0;
        }
        _selectedFarm = _farms[_selectedFarmIndex];
      } else {
        _selectedFarm = null;
        _selectedFarmIndex = 0;
      }
      
      _isLoading = false;
      notifyListeners();
    }, onError: (error) {
      debugPrint('Error listening to farms: $error');
      _isLoading = false;
      notifyListeners();
    });
  }

  void selectFarmIndex(int index) {
    if (index >= 0 && index < _farms.length) {
      _selectedFarmIndex = index;
      _selectedFarm = _farms[index];
      notifyListeners();
    }
  }

  void _clear() {
    _farmsSubscription?.cancel();
    _farms = [];
    _selectedFarm = null;
    _selectedFarmIndex = 0;
    _isLoading = false;
    notifyListeners();
  }

  @override
  void dispose() {
    _farmsSubscription?.cancel();
    super.dispose();
  }
}
