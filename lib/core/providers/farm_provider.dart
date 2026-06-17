import 'dart:async';
import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/farm_model.dart';
import 'auth_provider.dart';
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
        // Restore selected farm index from SharedPreferences
        try {
          final prefs = await SharedPreferences.getInstance();
          final savedIndex = prefs.getInt('selected_farm_index') ?? 0;
          if (savedIndex >= 0 && savedIndex < _farms.length) {
            _selectedFarmIndex = savedIndex;
          } else {
            _selectedFarmIndex = 0;
          }
        } catch (e) {
          debugPrint('Error loading saved farm index: $e');
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
