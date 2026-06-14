import 'package:flutter/material.dart';

class AppColors {
  AppColors._();

  // Primary Green Palette
  static const Color primary = Color(0xFF2E7D32);
  static const Color primaryLight = Color(0xFF4CAF50);
  static const Color primaryDark = Color(0xFF1B5E20);
  static const Color primaryContainer = Color(0xFFE8F5E9);

  // Secondary / Accent
  static const Color secondary = Color(0xFFF9A825);
  static const Color secondaryLight = Color(0xFFFFD54F);
  static const Color secondaryDark = Color(0xFFF57F17);
  static const Color secondaryContainer = Color(0xFFFFF8E1);

  // Earth Tones
  static const Color earth = Color(0xFF795548);
  static const Color earthLight = Color(0xFFA1887F);
  static const Color earthContainer = Color(0xFFEFEBE9);

  // Sky Blue
  static const Color sky = Color(0xFF0288D1);
  static const Color skyLight = Color(0xFF4FC3F7);
  static const Color skyContainer = Color(0xFFE1F5FE);

  // Neutrals
  static const Color white = Color(0xFFFFFFFF);
  static const Color background = Color(0xFFF5F9F4);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFF5F5F5);

  // Text
  static const Color textPrimary = Color(0xFF212121);
  static const Color textSecondary = Color(0xFF616161);
  static const Color textHint = Color(0xFF9E9E9E);
  static const Color textOnPrimary = Color(0xFFFFFFFF);

  // Status Colors
  static const Color success = Color(0xFF43A047);
  static const Color warning = Color(0xFFFB8C00);
  static const Color error = Color(0xFFE53935);
  static const Color info = Color(0xFF039BE5);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primaryDark, primary, primaryLight],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient splashGradient = LinearGradient(
    colors: [Color(0xFF1B5E20), Color(0xFF2E7D32), Color(0xFF388E3C)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient cardGradient = LinearGradient(
    colors: [Color(0xFF43A047), Color(0xFF2E7D32)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient weatherGradient = LinearGradient(
    colors: [Color(0xFF0288D1), Color(0xFF4FC3F7)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient alertGradient = LinearGradient(
    colors: [Color(0xFFF57F17), Color(0xFFF9A825)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // Divider
  static const Color divider = Color(0xFFE0E0E0);
  static const Color shadow = Color(0x1A000000);
}
