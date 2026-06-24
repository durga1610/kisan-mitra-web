import 'dart:async';
import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';

class UserProvider extends ChangeNotifier {
  UserModel? _userModel;
  bool _isLoading = false;
  StreamSubscription<DocumentSnapshot>? _userSubscription;

  UserModel? get userModel => _userModel;
  bool get isLoading => _isLoading;

  Future<void> updateAuth(User? firebaseUser) async {
    if (firebaseUser == null) {
      _userSubscription?.cancel();
      _userSubscription = null;
      try {
        if (Uri.base.queryParameters['demo'] == 'true') {
          if (_userModel == null) {
            _userModel = UserModel(
              uid: 'mock_demo_uid',
              name: 'Demo Farmer',
              phone: '+91 9999999999',
              email: 'demo@kisan.com',
              location: 'Demo Farm',
              updatedAt: DateTime.now(),
            );
            _isLoading = false;
            notifyListeners();
          }
          return;
        }
      } catch (_) {}
      if (_userModel != null) {
        _userModel = null;
        notifyListeners();
      }
      return;
    }
    
    // Avoid redundant loads
    if (_userModel?.uid == firebaseUser.uid) return;

    _isLoading = true;
    notifyListeners();

    String? cachedName;
    String? cachedPhone;
    String? cachedEmail;
    String? cachedPhoto;

    try {
      final prefs = await SharedPreferences.getInstance();
      cachedName = prefs.getString('cached_user_name');
      cachedPhone = prefs.getString('cached_user_phone');
      cachedEmail = prefs.getString('cached_user_email');
      cachedPhoto = prefs.getString('cached_user_photo');

      if (cachedName != null && _userModel == null) {
        _userModel = UserModel(
          uid: firebaseUser.uid,
          name: cachedName,
          phone: cachedPhone ?? '',
          email: cachedEmail ?? '',
          profileImageUrl: cachedPhoto,
          updatedAt: DateTime.now(),
        );
        _isLoading = false;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error reading cached profile: $e');
    }

    _userSubscription?.cancel();
    _userSubscription = FirebaseFirestore.instance
        .collection('users')
        .doc(firebaseUser.uid)
        .snapshots()
        .listen((snapshot) async {
      String? firestoreName;
      if (snapshot.exists) {
        final data = snapshot.data() as Map<String, dynamic>;
        _userModel = UserModel.fromMap(data);
        firestoreName = _userModel!.name;

        try {
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('cached_user_name', _userModel!.name);
          await prefs.setString('cached_user_phone', _userModel!.phone);
          await prefs.setString('cached_user_email', _userModel!.email ?? '');
          if (_userModel!.profileImageUrl != null) {
            await prefs.setString('cached_user_photo', _userModel!.profileImageUrl!);
          } else {
            await prefs.remove('cached_user_photo');
          }
        } catch (e) {
          debugPrint('Error saving updated profile to cache: $e');
        }
      } else {
        firestoreName = firebaseUser.displayName ?? 'Kisan Farmer';
        _userModel = UserModel(
          uid: firebaseUser.uid,
          name: firestoreName,
          phone: firebaseUser.phoneNumber ?? '+91 18001234567',
          email: firebaseUser.email ?? 'farmer@example.com',
          location: 'Local Farm',
          updatedAt: DateTime.now(),
        );
        await FirebaseFirestore.instance.collection('users').doc(firebaseUser.uid).set(_userModel!.toMap());
      }
      
      _isLoading = false;
      notifyListeners();

      // Debug Log matching required formats
      final String cachedNameLog = cachedName ?? 'None';
      final String firestoreNameLog = firestoreName ?? 'None';
      final String finalDisplayNameLog = _userModel?.name ?? 'Farmer';

      debugPrint('[PROFILE DEBUG]');
      debugPrint('Firebase UID: ${firebaseUser.uid}');
      debugPrint('UID=${firebaseUser.uid}');
      debugPrint('Firestore Name: $firestoreNameLog');
      debugPrint('Firestore Name=$firestoreNameLog');
      debugPrint('Cached Name: $cachedNameLog');
      debugPrint('Cached Name=$cachedNameLog');
      debugPrint('Final Display Name: $finalDisplayNameLog');
      debugPrint('Final Display Name=$finalDisplayNameLog');
    }, onError: (e) {
      debugPrint('Error listening to user profile: $e');
      _isLoading = false;
      notifyListeners();
    });
  }

  void updateUserProfile(UserModel updatedUser) async {
    _userModel = updatedUser;
    notifyListeners();
    try {
      await FirebaseFirestore.instance.collection('users').doc(updatedUser.uid).set(updatedUser.toMap(), SetOptions(merge: true));
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('cached_user_name', updatedUser.name);
      await prefs.setString('cached_user_phone', updatedUser.phone);
      await prefs.setString('cached_user_email', updatedUser.email ?? '');
      if (updatedUser.profileImageUrl != null) {
        await prefs.setString('cached_user_photo', updatedUser.profileImageUrl!);
      } else {
        await prefs.remove('cached_user_photo');
      }
    } catch (e) {
      debugPrint('Error saving updated profile: $e');
    }
  }

  Future<void> updateSelectedFarmId(String farmId) async {
    if (_userModel == null) return;
    try {
      await FirebaseFirestore.instance.collection('users').doc(_userModel!.uid).update({
        'selectedFarmId': farmId,
      });
    } catch (e) {
      debugPrint('Error updating selectedFarmId in Firestore: $e');
    }
  }

  void clearUser() async {
    _userSubscription?.cancel();
    _userSubscription = null;
    _userModel = null;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('cached_user_name');
      await prefs.remove('cached_user_phone');
      await prefs.remove('cached_user_email');
      await prefs.remove('cached_user_photo');
    } catch (e) {
      debugPrint('Error clearing cached profile: $e');
    }
  }

  @override
  void dispose() {
    _userSubscription?.cancel();
    super.dispose();
  }
}
