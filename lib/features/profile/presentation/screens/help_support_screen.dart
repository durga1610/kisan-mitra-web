import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../../core/constants/app_colors.dart';

class HelpSupportScreen extends StatelessWidget {
  const HelpSupportScreen({super.key});

  Future<void> _launchURL(BuildContext context, String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not perform action.'.tr(context))),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      
      appBar: AppBar(
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: AppColors.primaryGradient,
          ),
        ),
        title: Text(
          'Help & Support',
          style: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: Colors.white),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 4)),
                ],
              ),
              child: Column(
                children: [
                  Icon(Icons.support_agent_rounded, size: 64, color: Theme.of(context).colorScheme.primary),
                  const SizedBox(height: 16),
                  Text(
                    "How can we help you?",
                    style: GoogleFonts.poppins(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    "Our support team is available 24/7 to assist you with any issues related to farming or the app.",
                    textAlign: TextAlign.center,
                    style: GoogleFonts.poppins(fontSize: 14, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),
            Text(
              "Contact Options",
              style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.onSurface),
            ),
            const SizedBox(height: 16),
            _buildSupportTile(
              context: context,
              icon: Icons.phone_rounded,
              title: "Call Us",
              subtitle: "+91 1800-123-4567",
              onTap: () => _launchURL(context, "tel:+9118001234567"),
            ),
            _buildSupportTile(
              context: context,
              icon: Icons.email_rounded,
              title: "Email Support",
              subtitle: "support@kisanmitra.com",
              onTap: () => _launchURL(context, "mailto:support@kisanmitra.com"),
            ),
            _buildSupportTile(
              context: context,
              icon: Icons.chat_rounded,
              title: "WhatsApp Chat",
              subtitle: "Instant messaging support",
              onTap: () => _launchURL(context, "https://wa.me/9118001234567"),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSupportTile({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 5, offset: const Offset(0, 2)),
        ],
        border: Border.all(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5).withOpacity(0.1)),
      ),
      child: ListTile(
        onTap: onTap,
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        leading: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: Theme.of(context).colorScheme.primary),
        ),
        title: Text(title, style: GoogleFonts.poppins(fontWeight: FontWeight.w600)),
        subtitle: Text(subtitle, style: GoogleFonts.poppins(fontSize: 12, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5))),
        trailing: Icon(Icons.arrow_forward_ios_rounded, size: 16, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5)),
      ),
    );
  }
}
