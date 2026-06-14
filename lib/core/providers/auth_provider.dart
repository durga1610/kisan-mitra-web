import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  User? _user;
  bool _isLoading = true;

  AuthProvider() {
    _init();
  }

  User? get user => _user;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _user != null;

  void _init() {
    _authService.user.listen((User? user) {
      _user = user;
      _isLoading = false;
      notifyListeners();
    });
  }

  // Helper method for sign out
  Future<void> signOut() async {
    await _authService.signOut();
  }
}
