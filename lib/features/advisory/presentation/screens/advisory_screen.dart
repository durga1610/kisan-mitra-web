import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import '../../../../core/constants/app_colors.dart';

class AdvisoryScreen extends StatelessWidget {
  const AdvisoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      
      appBar: AppBar(
        title: Text('Advisory'.tr(context),
            style: GoogleFonts.poppins(fontWeight: FontWeight.w600)),
        
        elevation: 0,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.tips_and_updates_rounded,
                size: 80, color: AppColors.primaryLight),
            const SizedBox(height: 16),
            Text('Advisory Module'.tr(context),
                style: GoogleFonts.poppins(
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    color: Colors.white)),
            const SizedBox(height: 8),
            Text('Expert farming advice & tips'.tr(context),
                style: GoogleFonts.poppins(
                    fontSize: 14, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
          ],
        ),
      ),
    );
  }
}
