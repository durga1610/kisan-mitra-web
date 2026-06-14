import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LanguageProvider extends ChangeNotifier {
  String _currentLanguage = 'en';

  String get currentLanguage => _currentLanguage;

  LanguageProvider() {
    _loadLanguage();
  }

  Future<void> _loadLanguage() async {
    final prefs = await SharedPreferences.getInstance();
    _currentLanguage = prefs.getString('app_language') ?? 'en';
    notifyListeners();
  }

  Future<void> setLanguage(String languageCode) async {
    if (_currentLanguage == languageCode) return;
    _currentLanguage = languageCode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('app_language', languageCode);
    notifyListeners();
  }
}
