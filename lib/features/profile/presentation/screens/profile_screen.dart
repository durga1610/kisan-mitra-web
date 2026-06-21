import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:go_router/go_router.dart';
import 'settings_screen.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../../core/constants/app_colors.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../config/routes/app_router.dart';
import 'package:go_router/go_router.dart';
import '../../../../config/routes/app_router.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/providers/farm_provider.dart';
import '../../../../core/services/firestore_service.dart';
import '../../../../core/models/user_model.dart';
import '../../../../core/providers/language_provider.dart';
import '../../../../core/providers/user_provider.dart';
import '../../../../core/localization/app_translations.dart';
import 'edit_profile_screen.dart';
import 'manage_farms_screen.dart';
import 'privacy_policy_screen.dart';
import 'help_support_screen.dart';
import '../../../../core/widgets/language_selector_sheet.dart';


class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  @override
  void initState() {
    super.initState();
  }

  Future<void> _makePhoneCall() async {
    debugPrint("Call Support clicked");
    final Uri phoneUri = Uri(scheme: 'tel', path: '+9118001234567');
    try {
      if (await canLaunchUrl(phoneUri)) {
        await launchUrl(phoneUri);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Could not launch dialer'.tr(context))));
        }
      }
    } catch (e) {
      debugPrint("Phone call error: $e");
    }
  }

  Future<void> _sendEmail() async {
    debugPrint("Email Support clicked");
    final Uri emailUri = Uri(scheme: 'mailto', path: 'support@kisanmitra.com');
    try {
      if (await canLaunchUrl(emailUri)) {
        await launchUrl(emailUri);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Could not open email client'.tr(context))));
        }
      }
    } catch (e) {
      debugPrint("Email error: $e");
    }
  }

  Future<void> _openWhatsApp() async {
    debugPrint("WhatsApp Support clicked");
    final Uri whatsappUri = Uri.parse("https://wa.me/9118001234567");
    try {
      if (await canLaunchUrl(whatsappUri)) {
        await launchUrl(whatsappUri, mode: LaunchMode.externalApplication);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Could not open WhatsApp'.tr(context))));
        }
      }
    } catch (e) {
      debugPrint("WhatsApp error: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    final farmProvider = context.watch<FarmProvider>();
    final farm = farmProvider.selectedFarm;
    final userProvider = context.watch<UserProvider>();
    final _user = userProvider.userModel;
    final langProvider = Provider.of<LanguageProvider>(context);

    if (userProvider.isLoading || farmProvider.isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator(color: Colors.white)),
      );
    }

    final name = _user?.name ?? 'Farmer';
    final state = farm?.state ?? 'India';
    final district = farm?.district ?? '';
    final village = farm?.village ?? '';
    final landArea = farm?.landArea?.toString() ?? '0';
    final preferredCrops = farm?.preferredCrops.length.toString() ?? '0';

    return Scaffold(
      
      appBar: AppBar(
        title: Text('Profile'.tr(context),
            style: GoogleFonts.poppins(fontWeight: FontWeight.w600)),
        
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: Colors.white),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const SettingsScreen(),
                ),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const SizedBox(height: 24),
            // Avatar
            Container(
              width: 96,
              height: 96,
              decoration: BoxDecoration(
                gradient: AppColors.primaryGradient,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(color: Theme.of(context).cardColor.withOpacity(0.3), blurRadius: 20, offset: const Offset(0, 6)),
                ],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(48),
                child: _user?.profileImageUrl != null
                    ? Image.network(_user!.profileImageUrl!, fit: BoxFit.cover)
                    : const Icon(Icons.person_rounded, color: Colors.white, size: 50),
              ),
            ),
            const SizedBox(height: 16),
            Text(name,
                style: GoogleFonts.poppins(
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    color: Theme.of(context).colorScheme.onSurface)),
            const SizedBox(height: 4),
            Text(_user?.phone ?? Provider.of<AuthProvider>(context).user?.email ?? '',
                style: GoogleFonts.poppins(
                    fontSize: 14, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
            const SizedBox(height: 8),
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: AppColors.primaryContainer,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(village.isNotEmpty ? '$village, $district, $state' : (district.isNotEmpty ? '$district, $state' : state),
                  style: GoogleFonts.poppins(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: AppColors.primary)),
            ),
            const SizedBox(height: 32),

            // Stats Row
            Row(
              children: [
                _statCard(landArea, 'Acres'.tr(context), Icons.landscape_outlined),
                const SizedBox(width: 12),
                _statCard(preferredCrops, 'Crops'.tr(context), Icons.grass_rounded),
                const SizedBox(width: 12),
                _statCard(farm?.soilType.split(' ')[0] ?? 'Alluvial', 'Soil'.tr(context), Icons.layers_outlined),
              ],
            ),
            const SizedBox(height: 24),

            // Menu Items
            _menuItem(Icons.person_outline_rounded, 'Personal Info'.tr(context), () {
              if (_user != null) {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => EditProfileScreen(user: _user, farm: farm),
                  ),
                );
              }
            }),
            _menuItem(Icons.agriculture_outlined, 'Manage Fields'.tr(context), () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ManageFarmsScreen(),
                ),
              );
            }),
            _menuItem(Icons.language_outlined, 'Language'.tr(context), () {
              showLanguageSelectorSheet(context);
            }),
            const SizedBox(height: 8),

            // Logout
            Container(
              decoration: BoxDecoration(
                color: const Color(0xFFFFEBEE),
                borderRadius: BorderRadius.circular(14),
              ),
              child: ListTile(
                leading: const Icon(Icons.logout_rounded,
                    color: AppColors.error, size: 22),
                title: Text('Logout'.tr(context),
                    style: GoogleFonts.poppins(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.error)),
                onTap: () async {
                  final prefs = await SharedPreferences.getInstance();
                  await prefs.clear();
                  if (context.mounted) {
                    await Provider.of<AuthProvider>(context, listen: false).signOut();
                  }
                  if (context.mounted) {
                    context.go(AppRouter.login);
                  }
                },
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14)),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _statCard(String value, String label, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withOpacity(0.04),
                blurRadius: 8,
                offset: const Offset(0, 2)),
          ],
        ),
        child: Column(
          children: [
            Icon(icon, color: AppColors.primary, size: 22),
            const SizedBox(height: 6),
            Text(value,
                style: GoogleFonts.poppins(
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                    color: Theme.of(context).colorScheme.onSurface)),
            Text(label,
                style: GoogleFonts.poppins(
                    fontSize: 11, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
          ],
        ),
      ),
    );
  }

  Widget _menuItem(IconData icon, String label, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Container(
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(14),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withOpacity(0.03),
                blurRadius: 6,
                offset: const Offset(0, 2)),
          ],
        ),
        child: ListTile(
          leading: Icon(icon, color: AppColors.primary, size: 22),
          title: Text(label,
              style: GoogleFonts.poppins(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: Theme.of(context).colorScheme.onSurface)),
          trailing: const Icon(Icons.chevron_right_rounded,
              color: AppColors.textHint),
          onTap: onTap,
          shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14)),
        ),
      ),
    );
  }

  Widget supportCard(
    IconData icon,
    String title,
    String subtitle,
    VoidCallback onTap,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: const Color(0xFFF5F7F5),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(20),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                CircleAvatar(
                  backgroundColor: const Color(0xFFE8F5E9),
                  child: Icon(icon, color: const Color(0xFF2E7D32)),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(subtitle),
                    ],
                  ),
                ),
                const Icon(Icons.arrow_forward_ios_rounded, size: 16),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
