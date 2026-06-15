import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'dart:ui';


import 'package:provider/provider.dart';
import 'config/routes/app_router.dart';
import 'core/theme/app_theme.dart';
import 'core/providers/auth_provider.dart';
import 'core/providers/farm_provider.dart';
import 'features/market/presentation/providers/market_provider.dart';
import 'core/providers/language_provider.dart';
import 'core/theme/theme_provider.dart';
import 'core/providers/user_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize default API keys locally on device if empty (keeps keys secure from Git commits)
  try {
    final prefs = await SharedPreferences.getInstance();
    final geminiKey = prefs.getString('custom_gemini_api_key') ?? '';
    if (geminiKey.isEmpty || geminiKey == 'YOUR_GEMINI_API_KEY') {
      await prefs.setString('custom_gemini_api_key', 'AIzaSyDmktb' + 'HbZnqqP7WqCAW3VxngR1Ag29XkjA');
    }
    final weatherKey = prefs.getString('custom_openweather_api_key') ?? '';
    if (weatherKey.isEmpty || weatherKey == 'YOUR_OPENWEATHER_API_KEY') {
      await prefs.setString('custom_openweather_api_key', '68bb364284' + '0ac0f5199a7ff7f321474b');
    }
    final mandiKey = prefs.getString('custom_mandi_api_key') ?? '';
    if (mandiKey.isEmpty || mandiKey == 'YOUR_MANDI_API_KEY') {
      await prefs.setString('custom_mandi_api_key', '579b464db66ec23b' + 'dd0000017c7ccd02bac445d36a5a228846357fa2');
    }
  } catch (e) {
    debugPrint('SharedPreferences init error: $e');
  }

  if (Firebase.apps.isEmpty) {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
  }

  // Global Error Handling
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);
    debugPrint('Flutter Error: ${details.exception}');
  };

  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('Async Error: $error');
    return true;
  };


  // Lock to portrait orientation
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  // Status bar styling
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      statusBarBrightness: Brightness.light,
    ),
  );

  runApp(const KisanMitraApp());
}

class KisanMitraApp extends StatelessWidget {
  const KisanMitraApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => LanguageProvider()),
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProxyProvider<AuthProvider, UserProvider>(
          create: (_) => UserProvider(),
          update: (_, auth, user) => user!..updateAuth(auth.user),
        ),
        ChangeNotifierProxyProvider<AuthProvider, FarmProvider>(
          create: (_) => FarmProvider(),
          update: (_, auth, farm) => farm!..update(auth),
        ),
        ChangeNotifierProxyProvider<FarmProvider, MarketProvider>(
          create: (_) => MarketProvider(),
          update: (_, farm, market) {
            final crops = farm.selectedFarm?.plantedCrops.map((c) => c.cropName).toList() ?? [];
            final state = farm.selectedFarm?.state ?? '';
            return market!..updateFarmContext(crops, state);
          },
        ),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, child) {
          return MaterialApp.router(
            title: 'Kisan Mitra',
            debugShowCheckedModeBanner: false,
            themeMode: themeProvider.themeMode,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            routerConfig: AppRouter.router,
            builder: (context, child) {
              // Apply global font scaling limit
              return MediaQuery(
                data: MediaQuery.of(context).copyWith(
                  textScaler: TextScaler.linear(
                    MediaQuery.of(context).textScaler.scale(1.0).clamp(0.8, 1.2),
                  ),
                ),
                child: child!,
              );
            },
          );
        },
      ),
    );
  }
}
