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

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

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
