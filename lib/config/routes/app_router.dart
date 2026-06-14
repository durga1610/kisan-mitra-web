import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../features/splash/presentation/screens/splash_screen.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/crops/presentation/screens/crops_screen.dart';
import '../../features/market/presentation/screens/market_screen.dart';
import '../../features/advisory/presentation/screens/advisory_screen.dart';
import '../../features/profile/presentation/screens/profile_screen.dart';
import '../../features/profile_setup/presentation/screens/profile_setup_screen.dart';
import '../../features/crop_recommendation/presentation/screens/crop_recommendation_screen.dart';
import '../../features/ai_assistant/presentation/screens/ai_assistant_screen.dart';
import '../../features/disease_detection/presentation/screens/disease_detection_screen.dart';
import '../../features/weather/presentation/screens/weather_screen.dart';
import '../../features/profit_analyzer/presentation/screens/profit_analyzer_screen.dart';

import '../../core/providers/auth_provider.dart';
import 'package:provider/provider.dart';

import '../../features/advisory/presentation/screens/ai_advisory_screen.dart';

import '../../features/disease_detection/presentation/screens/disease_history_screen.dart';
import '../../features/disease_detection/presentation/screens/disease_result_screen.dart';
import '../../features/disease_detection/data/models/disease_report.dart';
import '../../features/notifications/presentation/screens/notification_history_screen.dart';
import '../../features/advisory/presentation/screens/fertilizer_screen.dart';

class AppRouter {
  static const String splash = '/';
  static const String login = '/login';
  static const String home = '/home';
  static const String crops = '/crops';
  static const String market = '/market';
  static const String advisory = '/advisory';
  static const String aiAdvisory = '/ai-advisory';
  static const String profile = '/profile';
  static const String profileSetup = '/profile-setup';
  static const String cropRecommendation = '/crop-recommendation';
  static const String aiAssistant = '/ai-assistant';
  static const String diseaseDetection = '/disease-detection';
  static const String diseaseResult = '/disease-result';
  static const String diseaseHistory = '/disease-history';
  static const String weatherDashboard = '/weather-dashboard';
  static const String profitAnalyzer = '/profit-analyzer';
  static const String notifications = '/notifications';
  static const String fertilizer = '/fertilizer';

  static final GoRouter router = GoRouter(
    initialLocation: splash,
    redirect: (context, state) {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final isLoggingIn = state.matchedLocation == login;
      final isSplashing = state.matchedLocation == splash;

      if (authProvider.isLoading) return null;

      if (!authProvider.isAuthenticated) {
        if (!isLoggingIn && !isSplashing) return login;
        return null;
      }

      if (isLoggingIn || isSplashing) return home;

      return null;
    },
    debugLogDiagnostics: false,
    routes: [
      GoRoute(
        path: splash,
        name: 'splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: login,
        name: 'login',
        builder: (context, state) => const LoginScreen(),
        pageBuilder: (context, state) => CustomTransitionPage(
          key: state.pageKey,
          child: const LoginScreen(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(opacity: animation, child: child);
          },
        ),
      ),
      GoRoute(
        path: home,
        name: 'home',
        builder: (context, state) => const HomeScreen(),
        pageBuilder: (context, state) => CustomTransitionPage(
          key: state.pageKey,
          child: const HomeScreen(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return SlideTransition(
              position: Tween<Offset>(
                begin: const Offset(1, 0),
                end: Offset.zero,
              ).animate(CurvedAnimation(
                parent: animation,
                curve: Curves.easeOutCubic,
              )),
              child: child,
            );
          },
        ),
      ),
      GoRoute(
        path: crops,
        name: 'crops',
        builder: (context, state) => const CropsScreen(),
      ),
      GoRoute(
        path: market,
        name: 'market',
        builder: (context, state) => const MarketScreen(),
      ),
      GoRoute(
        path: advisory,
        name: 'advisory',
        builder: (context, state) => const AIAdvisoryScreen(),
      ),
      GoRoute(
        path: profile,
        name: 'profile',
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: profileSetup,
        name: 'profileSetup',
        builder: (context, state) => const ProfileSetupScreen(),
      ),
      GoRoute(
        path: cropRecommendation,
        name: 'cropRecommendation',
        builder: (context, state) => const CropRecommendationScreen(),
      ),
      GoRoute(
        path: aiAssistant,
        name: 'aiAssistant',
        builder: (context, state) => const AIAssistantScreen(),
      ),
      GoRoute(
        path: aiAdvisory,
        name: 'aiAdvisory',
        builder: (context, state) => const AIAdvisoryScreen(),
      ),
      GoRoute(
        path: diseaseDetection,
        name: 'diseaseDetection',
        builder: (context, state) => const DiseaseDetectionScreen(),
      ),
      GoRoute(
        path: diseaseResult,
        name: 'diseaseResult',
        builder: (context, state) {
          final report = state.extra as DiseaseReport;
          return DiseaseResultScreen(report: report);
        },
      ),
      GoRoute(
        path: diseaseHistory,
        name: 'diseaseHistory',
        builder: (context, state) => const DiseaseHistoryScreen(),
      ),
      GoRoute(
        path: weatherDashboard,
        name: 'weatherDashboard',
        builder: (context, state) => const WeatherScreen(),
      ),
      GoRoute(
        path: profitAnalyzer,
        name: 'profitAnalyzer',
        builder: (context, state) => const ProfitAnalyzerScreen(),
      ),
      GoRoute(
        path: notifications,
        name: 'notifications',
        builder: (context, state) => const NotificationHistoryScreen(),
      ),
      GoRoute(
        path: fertilizer,
        name: 'fertilizer',
        builder: (context, state) => const FertilizerScreen(),
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('Page not found: ${state.uri}'),
      ),
    ),
  );
}
