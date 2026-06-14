import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../../core/constants/app_colors.dart';

class PrivacyPolicyScreen extends StatefulWidget {
  const PrivacyPolicyScreen({super.key});

  @override
  State<PrivacyPolicyScreen> createState() => _PrivacyPolicyScreenState();
}

class _PrivacyPolicyScreenState extends State<PrivacyPolicyScreen> with SingleTickerProviderStateMixin {
  late ScrollController _scrollController;
  double _progress = 0;
  String _searchQuery = '';
  final TextEditingController _searchController = TextEditingController();

  final List<PolicySection> _sections = [
    PolicySection(
      title: "1. INTRODUCTION",
      content: "Kisan Mitra values your privacy and is committed to protecting your personal information, farm records, and agricultural data. This policy explains how we handle your data.",
      icon: Icons.info_outline_rounded,
    ),
    PolicySection(
      title: "2. INFORMATION WE COLLECT",
      content: "We collect the following data to provide better services:\n• Name, Email, and Phone number\n• Farm location and Crop information\n• Soil and weather preferences\n• Device information and Usage analytics",
      icon: Icons.data_usage_rounded,
    ),
    PolicySection(
      title: "3. HOW WE USE YOUR DATA",
      content: "Your data helps us offer:\n• Personalized farming recommendations\n• Weather alerts & Market price notifications\n• Crop management insights\n• App improvements & Customer support",
      icon: Icons.analytics_outlined,
    ),
    PolicySection(
      title: "4. DATA SECURITY",
      content: "We employ industry-standard measures including:\n• Encrypted storage\n• Secure cloud systems\n• Access protection\n• Authentication security",
      icon: Icons.security_rounded,
    ),
    PolicySection(
      title: "5. DATA SHARING POLICY",
      content: "We never sell personal data. We only share data with trusted third-party services when strictly necessary to provide features, or as required for legal compliance.",
      icon: Icons.handshake_outlined,
    ),
    PolicySection(
      title: "6. LOCATION SERVICES",
      content: "Location data is utilized exclusively for:\n• Weather forecasts\n• Nearby mandi prices\n• Local farming recommendations",
      icon: Icons.location_on_outlined,
    ),
    PolicySection(
      title: "7. USER RIGHTS",
      content: "You retain full control over your data. You can:\n• View your data\n• Edit your profile\n• Delete your account\n• Request data removal",
      icon: Icons.gavel_rounded,
    ),
    PolicySection(
      title: "8. COOKIES & ANALYTICS",
      content: "We use basic analytics for:\n• Performance monitoring\n• User experience improvements\n• Application usage analytics",
      icon: Icons.cookie_outlined,
    ),
    PolicySection(
      title: "9. CHILDREN'S PRIVACY",
      content: "Kisan Mitra is intended for adult farmers. Our app is not intended for children under 13.",
      icon: Icons.child_care_rounded,
    ),
    PolicySection(
      title: "10. POLICY UPDATES",
      content: "We may update this policy periodically. Users will be notified within the app for any important changes.",
      icon: Icons.update_rounded,
    ),
  ];

  @override
  void initState() {
    super.initState();
    _scrollController = ScrollController()..addListener(() {
      if (_scrollController.hasClients) {
        final maxScroll = _scrollController.position.maxScrollExtent;
        final currentScroll = _scrollController.position.pixels;
        if (maxScroll > 0) {
          setState(() {
            _progress = currentScroll / maxScroll;
          });
        }
      }
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _launchURL(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final filteredSections = _searchQuery.isEmpty
        ? _sections
        : _sections.where((s) => s.title.toLowerCase().contains(_searchQuery.toLowerCase()) || s.content.toLowerCase().contains(_searchQuery.toLowerCase())).toList();

    return Scaffold(
      
      body: CustomScrollView(
        controller: _scrollController,
        slivers: [
          SliverAppBar(
            expandedHeight: 280,
            pinned: true,
            backgroundColor: AppColors.primary,
            elevation: 0,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white),
              onPressed: () => Navigator.pop(context),
            ),
            actions: [
              IconButton(icon: const Icon(Icons.download_rounded, color: Colors.white), onPressed: () {}),
              IconButton(icon: const Icon(Icons.share_rounded, color: Colors.white), onPressed: () {}),
            ],
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Color(0xFF2E7D32), Color(0xFF66BB6A)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        const Icon(Icons.shield_rounded, color: Colors.white, size: 48),
                        const SizedBox(height: 16),
                        Text(
                          "Privacy Policy",
                          style: GoogleFonts.poppins(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          "Your privacy and farm data security matter to us.",
                          style: GoogleFonts.poppins(color: Colors.white70, fontSize: 14),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(color: Theme.of(context).cardColor.withOpacity(0.24), borderRadius: BorderRadius.circular(12)),
                              child: Text("Updated: Today".tr(context), style: GoogleFonts.poppins(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w500)),
                            ),
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(color: Theme.of(context).cardColor.withOpacity(0.24), borderRadius: BorderRadius.circular(12)),
                              child: Text("v1.0.0".tr(context), style: GoogleFonts.poppins(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w500)),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24), // Space for search bar overlap
                      ],
                    ),
                  ),
                ),
              ),
            ),
            bottom: PreferredSize(
              preferredSize: const Size.fromHeight(64),
              child: Stack(
                children: [
                  Container(
                    height: 64,
                    decoration: BoxDecoration(
                      color: Theme.of(context).scaffoldBackgroundColor,
                      borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
                    ),
                  ),
                  Positioned(
                    top: 0, left: 0, right: 0,
                    child: LinearProgressIndicator(
                      value: _progress,
                      backgroundColor: Colors.transparent,
                      valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF66BB6A)),
                      minHeight: 4,
                    ),
                  ),
                  Positioned(
                    top: 8, left: 16, right: 16, bottom: 8,
                    child: TextField(
                      controller: _searchController,
                      onChanged: (val) => setState(() => _searchQuery = val),
                      style: GoogleFonts.poppins(fontSize: 14),
                      decoration: InputDecoration(
                        hintText: "Search in policy...",
                        hintStyle: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5), fontSize: 14),
                        prefixIcon: Icon(Icons.search, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5), size: 20),
                        filled: true,
                        fillColor: Theme.of(context).cardColor,
                        contentPadding: const EdgeInsets.symmetric(vertical: 0),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(30), borderSide: BorderSide(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5).withOpacity(0.2))),
                        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(30), borderSide: BorderSide(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5).withOpacity(0.2))),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (filteredSections.isEmpty)
                    Center(
                      child: Padding(
                        padding: const EdgeInsets.all(40.0),
                        child: Text("No sections found for '$_searchQuery'", style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5), fontSize: 16)),
                      ),
                    ),
                  ...filteredSections.map((section) => _buildExpandableSection(section)).toList(),
                  
                  const SizedBox(height: 32),
                  _buildContactSection(),
                  const SizedBox(height: 32),
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: ElevatedButton(
                      onPressed: () => Navigator.pop(context),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        elevation: 2,
                      ),
                      child: Text("I Accept & Agree".tr(context), style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                    ),
                  ),
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildExpandableSection(PolicySection section) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 10, offset: const Offset(0, 4)),
        ],
        border: Border.all(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5).withOpacity(0.1)),
      ),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        iconColor: const Color(0xFF2E7D32),
        collapsedIconColor: Colors.grey,
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: const Color(0xFFE8F5E9),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(section.icon, color: const Color(0xFF2E7D32), size: 22),
        ),
        title: Text(
          section.title,
          style: GoogleFonts.poppins(fontSize: 15, fontWeight: FontWeight.w600, color: const Color(0xFF2E7D32)),
        ),
        childrenPadding: const EdgeInsets.only(left: 20, right: 20, bottom: 20),
        expandedCrossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Divider(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5).withOpacity(0.1)),
          const SizedBox(height: 8),
          Text(
            section.content,
            style: GoogleFonts.poppins(fontSize: 14, color: Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey[700], height: 1.6),
          ),
        ],
      ),
    );
  }

  Widget _buildContactSection() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFFE8F5E9),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("11. CONTACT US".tr(context), style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF2E7D32))),
          const SizedBox(height: 16),
          Text("If you have any questions or concerns about this privacy policy, please contact our support team.".tr(context), style: GoogleFonts.poppins(fontSize: 14, color: Colors.black87)),
          const SizedBox(height: 20),
          _contactButton(Icons.email_rounded, "support@kisanmitra.com", () => _launchURL('mailto:support@kisanmitra.com')),
          const SizedBox(height: 12),
          _contactButton(Icons.phone_rounded, "+91 1800-123-4567", () => _launchURL('tel:+9118001234567')),
          const SizedBox(height: 12),
          _contactButton(Icons.chat_rounded, "WhatsApp Support", () => _launchURL('https://wa.me/9118001234567')),
        ],
      ),
    );
  }

  Widget _contactButton(IconData icon, String text, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.green.withOpacity(0.2)),
        ),
        child: Row(
          children: [
            Icon(icon, color: const Color(0xFF2E7D32), size: 20),
            const SizedBox(width: 12),
            Expanded(child: Text(text, style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w500, color: const Color(0xFF2E7D32)))),
            Icon(Icons.arrow_forward_ios_rounded, size: 14, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5)),
          ],
        ),
      ),
    );
  }
}

class PolicySection {
  final String title;
  final String content;
  final IconData icon;

  PolicySection({required this.title, required this.content, required this.icon});
}
