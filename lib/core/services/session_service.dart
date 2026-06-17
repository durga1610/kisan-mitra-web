import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:firebase_auth/firebase_auth.dart' hide AuthProvider;
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../../config/routes/app_router.dart';

class SessionService {
  static const String _keyLastActivity = 'last_activity_timestamp';
  static const int _timeoutSeconds = 3600; // 1 hour

  // Update last activity timestamp to now
  static Future<void> updateActivity() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt(_keyLastActivity, DateTime.now().millisecondsSinceEpoch);
    } catch (e) {
      debugPrint('Error updating session activity: $e');
    }
  }

  // Check if session has expired
  static Future<bool> isSessionExpired() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) return false;

      final prefs = await SharedPreferences.getInstance();
      final lastActivity = prefs.getInt(_keyLastActivity);
      if (lastActivity == null) {
        // If no timestamp, set it now and assume not expired
        await updateActivity();
        return false;
      }

      final diff = DateTime.now().millisecondsSinceEpoch - lastActivity;
      return diff > (_timeoutSeconds * 1000);
    } catch (e) {
      debugPrint('Error checking session expiry: $e');
      return false;
    }
  }

  // Check session and log out if expired
  static Future<void> checkSession(BuildContext context) async {
    if (await isSessionExpired()) {
      if (context.mounted) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.clear();
        
        final authProvider = Provider.of<AuthProvider>(context, listen: false);
        await authProvider.signOut();
        
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Your session has expired due to inactivity. Please log in again.'),
              backgroundColor: Colors.redAccent,
              behavior: SnackBarBehavior.floating,
              duration: Duration(seconds: 5),
            ),
          );
          context.go(AppRouter.login);
        }
      }
    } else {
      await updateActivity();
    }
  }
}
