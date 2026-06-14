import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
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

    try {
      final userDoc = await _firestoreService.getDocument('users/${firebaseUser.uid}');
      if (userDoc.exists) {
        _userModel = UserModel.fromMap(userDoc.data() as Map<String, dynamic>);
      } else {
        // Fallback for mock or missing data
        _userModel = UserModel(
          uid: firebaseUser.uid,
          name: firebaseUser.displayName ?? 'Kisan Farmer',
          phone: firebaseUser.phoneNumber ?? '+91 18001234567',
          email: firebaseUser.email ?? 'farmer@example.com',
          location: 'Local Farm',
          updatedAt: DateTime.now(),
        );
      }
    } catch (e) {
      debugPrint('Error loading user profile: $e');
      _userModel = UserModel(
        uid: firebaseUser.uid,
        name: firebaseUser.displayName ?? 'Kisan Farmer',
        phone: firebaseUser.phoneNumber ?? '+91 18001234567',
        email: firebaseUser.email ?? 'farmer@example.com',
        location: 'Local Farm',
        updatedAt: DateTime.now(),
      );
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void updateUserProfile(UserModel updatedUser) {
    _userModel = updatedUser;
    notifyListeners();
  }

  void clearUser() {
    _userModel = null;
    notifyListeners();
  }
}
