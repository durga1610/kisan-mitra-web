import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../config/routes/app_router.dart';
import '../widgets/home_bottom_nav.dart';

class MainNavigationShell extends StatelessWidget {
  final Widget child;

  const MainNavigationShell({
    super.key,
    required this.child,
  });

  int _getCurrentIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith(AppRouter.crops)) {
      return 1;
    } else if (location.startsWith(AppRouter.profile)) {
      return 2;
    }
    return 0; // default to Home
  }

  void _onTap(BuildContext context, int index) async {
    final prefs = await SharedPreferences.getInstance();
    switch (index) {
      case 0:
        await prefs.setString('last_route', AppRouter.home);
        AppRouter.initialRoute = AppRouter.home;
        if (context.mounted) context.go(AppRouter.home);
        break;
      case 1:
        await prefs.setString('last_route', AppRouter.crops);
        AppRouter.initialRoute = AppRouter.crops;
        if (context.mounted) context.go(AppRouter.crops);
        break;
      case 2:
        await prefs.setString('last_route', AppRouter.profile);
        AppRouter.initialRoute = AppRouter.profile;
        if (context.mounted) context.go(AppRouter.profile);
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentIndex = _getCurrentIndex(context);
    return Scaffold(
      body: child,
      bottomNavigationBar: HomeBottomNav(
        currentIndex: currentIndex,
        onTap: (index) => _onTap(context, index),
      ),
    );
  }
}
