import 'dart:async';
import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/farm_model.dart';
import 'auth_provider.dart';
import 'user_provider.dart';
import '../services/location_service.dart';

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

  UserProvider? _userProvider;
  String? _currentUid;

  void update(AuthProvider authProvider, UserProvider userProvider) {
    _userProvider = userProvider;
    final user = authProvider.user;
    if (user != null) {
      if (_currentUid != user.uid) {
        _currentUid = user.uid;
        _listenToFarms(user.uid);
      } else {
        _syncSelectedFarmFromUserProvider();
      }
    } else {
      _clear();
      _currentUid = null;
    }
  }

  void _syncSelectedFarmFromUserProvider() {
    if (_farms.isEmpty || _userProvider == null) return;
    final selectedFarmId = _userProvider!.userModel?.selectedFarmId;
    if (selectedFarmId != null) {
      final index = _farms.indexWhere((f) => f.id == selectedFarmId);
      if (index != -1 && index != _selectedFarmIndex) {
        _selectedFarmIndex = index;
        _selectedFarm = _farms[index];
        notifyListeners();
      }
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
        .listen((snapshot) async {
      _farms = snapshot.docs.map((doc) => FarmModel.fromMap(doc.data(), docId: doc.id)).toList();
      
      bool updatedAny = false;
      for (int i = 0; i < _farms.length; i++) {
        final farm = _farms[i];
        if (farm.id != null && (farm.latitude == null || farm.longitude == null)) {
          debugPrint('[FarmProvider] Geocoding missing coordinates for farm: ${farm.name} (${farm.village}, ${farm.district}, ${farm.state})');
          final locationService = LocationService();
          final coords = await locationService.getLatLngFromAddress(farm.village, farm.district, farm.state);
          if (coords != null) {
            final lat = coords['latitude']!;
            final lon = coords['longitude']!;
            
            // Save coordinates permanently to Firestore
            await _firestore.collection('farms').doc(farm.id).update({
              'latitude': lat,
              'longitude': lon,
            }).catchError((e) => debugPrint('[FarmProvider] Error updating farm coordinates: $e'));
            
            // Update in-memory copy
            _farms[i] = FarmModel(
              id: farm.id,
              ownerId: farm.ownerId,
              name: farm.name,
              state: farm.state,
              district: farm.district,
              village: farm.village,
              soilType: farm.soilType,
              landArea: farm.landArea,
              waterAvailability: farm.waterAvailability,
              preferredCrops: farm.preferredCrops,
              plantedCrops: farm.plantedCrops,
              updatedAt: farm.updatedAt,
              latitude: lat,
              longitude: lon,
            );
            updatedAny = true;
          }
        }
      }
      
      if (_farms.isNotEmpty) {
        final selectedFarmId = _userProvider?.userModel?.selectedFarmId;
        if (selectedFarmId != null) {
          final index = _farms.indexWhere((f) => f.id == selectedFarmId);
          if (index != -1) {
            _selectedFarmIndex = index;
            _selectedFarm = _farms[index];
          } else {
            _selectedFarmIndex = 0;
            _selectedFarm = _farms[0];
          }
        } else {
          _selectedFarmIndex = 0;
          _selectedFarm = _farms[0];
          if (_selectedFarm != null && _selectedFarm!.id != null) {
            FirebaseFirestore.instance.collection('users').doc(uid).update({
              'selectedFarmId': _selectedFarm!.id,
            }).catchError((e) => debugPrint('Error saving initial selectedFarmId: $e'));
          }
        }
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

  void selectFarmIndex(int index) async {
    if (index >= 0 && index < _farms.length) {
      _selectedFarmIndex = index;
      _selectedFarm = _farms[index];
      notifyListeners();
      try {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setInt('selected_farm_index', index);
      } catch (e) {
        debugPrint('Error saving farm index: $e');
      }

      // Also update Firestore to sync with other devices
      final farmId = _farms[index].id;
      if (farmId != null) {
        try {
          await FirebaseFirestore.instance.collection('users').doc(_selectedFarm!.ownerId).update({
            'selectedFarmId': farmId,
          });
        } catch (e) {
          debugPrint('Error updating selectedFarmId in Firestore: $e');
        }
      }
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
