import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';
import '../services/firestore_service.dart';

class UserProvider extends ChangeNotifier {
  final FirestoreService _firestoreService = FirestoreService();
  UserModel? _userModel;
  bool _isLoading = false;

  UserModel? get userModel => _userModel;
  bool get isLoading => _isLoading;

  Future<void> updateAuth(User? firebaseUser) async {
    if (firebaseUser == null) {
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

    String? firestoreName;

    try {
      final userDoc = await _firestoreService.getDocument('users/${firebaseUser.uid}');
      final prefs = await SharedPreferences.getInstance();
      if (userDoc.exists) {
        final data = userDoc.data() as Map<String, dynamic>;
        _userModel = UserModel.fromMap(data);
        firestoreName = _userModel!.name;

        await prefs.setString('cached_user_name', _userModel!.name);
        await prefs.setString('cached_user_phone', _userModel!.phone);
        await prefs.setString('cached_user_email', _userModel!.email ?? '');
        if (_userModel!.profileImageUrl != null) {
          await prefs.setString('cached_user_photo', _userModel!.profileImageUrl!);
        } else {
          await prefs.remove('cached_user_photo');
        }
      } else {
        firestoreName = firebaseUser.displayName ?? 'Kisan Farmer';
        if (_userModel == null) {
          _userModel = UserModel(
            uid: firebaseUser.uid,
            name: firestoreName,
            phone: firebaseUser.phoneNumber ?? '+91 18001234567',
            email: firebaseUser.email ?? 'farmer@example.com',
            location: 'Local Farm',
            updatedAt: DateTime.now(),
          );
        }
      }
    } catch (e) {
      debugPrint('Error loading user profile: $e');
      if (_userModel == null) {
        _userModel = UserModel(
          uid: firebaseUser.uid,
          name: firebaseUser.displayName ?? 'Kisan Farmer',
          phone: firebaseUser.phoneNumber ?? '+91 18001234567',
          email: firebaseUser.email ?? 'farmer@example.com',
          location: 'Local Farm',
          updatedAt: DateTime.now(),
        );
      }
    } finally {
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
    }
  }

  void updateUserProfile(UserModel updatedUser) async {
    _userModel = updatedUser;
    notifyListeners();
    try {
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
      debugPrint('Error saving updated profile to cache: $e');
    }
  }

  void clearUser() async {
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
}
