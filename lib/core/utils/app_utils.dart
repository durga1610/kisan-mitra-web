import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../constants/app_strings.dart';

class AppUtils {
  AppUtils._();

  static String getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return AppStrings.goodMorning;
    if (hour < 17) return AppStrings.goodAfternoon;
    return AppStrings.goodEvening;
  }

  static String formatDate(DateTime date) {
    return DateFormat('dd MMM yyyy').format(date);
  }

  static String formatTime(DateTime time) {
    return DateFormat('hh:mm a').format(time);
  }

  static String formatCurrency(double amount) {
    return '₹${NumberFormat('#,##,###').format(amount)}';
  }

  static String formatPrice(double price) {
    return '₹${price.toStringAsFixed(2)}';
  }

  static bool isValidPhone(String phone) {
    final phoneRegex = RegExp(r'^[6-9]\d{9}$');
    return phoneRegex.hasMatch(phone);
  }

  static bool isValidPassword(String password) {
    return password.length >= 6;
  }

  static void showSnackBar(
    BuildContext context,
    String message, {
    bool isError = false,
    Duration duration = const Duration(seconds: 3),
  }) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red.shade700 : Colors.green.shade700,
        duration: duration,
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  static String getTodayDateFormatted() {
    return DateFormat('EEEE, dd MMMM yyyy').format(DateTime.now());
  }
}
