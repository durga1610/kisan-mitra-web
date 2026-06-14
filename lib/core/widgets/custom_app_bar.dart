import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final bool showBackButton;
  final VoidCallback? onBackPressed;
  final Widget? titleWidget;

  const CustomAppBar({
    super.key,
    this.title = '',
    this.titleWidget,
    this.actions,
    this.showBackButton = true,
    this.onBackPressed,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      backgroundColor: const Color(0xFF2E7D32),
      elevation: 0,
      centerTitle: false,
      leading: showBackButton 
        ? IconButton(
            icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white, size: 20),
            onPressed: onBackPressed ?? () {
              if (Navigator.canPop(context)) {
                Navigator.pop(context);
              }
            },
          )
        : null,
      title: titleWidget ?? Text(
        title,
        style: GoogleFonts.poppins(
          color: Colors.white,
          fontSize: 18,
          fontWeight: FontWeight.w600,
        ),
      ),
      actions: actions,
      iconTheme: const IconThemeData(color: Colors.white),
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}

class CustomSliverAppBar extends StatelessWidget {
  final String title;
  final List<Widget>? actions;
  final bool showBackButton;
  final Widget? background;
  final double expandedHeight;

  const CustomSliverAppBar({
    super.key,
    required this.title,
    this.actions,
    this.showBackButton = true,
    this.background,
    this.expandedHeight = 120.0,
  });

  @override
  Widget build(BuildContext context) {
    return SliverAppBar(
      backgroundColor: const Color(0xFF2E7D32),
      elevation: 0,
      pinned: true,
      expandedHeight: expandedHeight,
      leading: showBackButton 
        ? IconButton(
            icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white, size: 20),
            onPressed: () {
              if (Navigator.canPop(context)) {
                Navigator.pop(context);
              }
            },
          )
        : null,
      flexibleSpace: FlexibleSpaceBar(
        title: Text(
          title,
          style: GoogleFonts.poppins(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        background: background,
      ),
      actions: actions,
      iconTheme: const IconThemeData(color: Colors.white),
    );
  }
}
