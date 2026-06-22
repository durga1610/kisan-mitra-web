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
  
  bool get isLoading {
    try {
      if (Uri.base.queryParameters['demo'] == 'true') return false;
    } catch (_) {}
    return _isLoading;
  }
  
  bool get isAuthenticated {
    try {
      if (Uri.base.queryParameters['demo'] == 'true') return true;
    } catch (_) {}
    return _user != null;
  }

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
