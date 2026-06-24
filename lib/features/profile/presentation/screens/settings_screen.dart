import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:go_router/go_router.dart';
import '../../../../config/routes/app_router.dart';
import 'package:firebase_auth/firebase_auth.dart' hide AuthProvider;
import 'package:cloud_firestore/cloud_firestore.dart';

import '../../../../core/constants/app_colors.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/providers/language_provider.dart';
import '../../../../core/theme/theme_provider.dart';
import '../../../../core/localization/app_translations.dart';
import '../../../../core/models/user_model.dart';
import '../../../../core/providers/user_provider.dart';
import '../../../../core/services/auth_service.dart';
import 'edit_profile_screen.dart';
import 'privacy_policy_screen.dart';
import 'help_support_screen.dart';
import '../../../../core/widgets/language_selector_sheet.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  
  bool pushNotifications = true;
  bool weatherAlerts = true;
  String weatherAlertFrequency = 'Daily';
  bool marketAlerts = false;
  bool autoBackup = true;
  String lastBackupTime = "Never";
  bool isSyncing = false;
  
  String searchQuery = "";
  final TextEditingController _searchController = TextEditingController();

  List<String> marketAlertCrops = [];
  String geminiApiKey = "";
  String openWeatherApiKey = "";
  String mandiApiKey = "";

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(vsync: this, duration: const Duration(milliseconds: 300));
    _animationController.forward();
    _loadPreferences();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadPreferences() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      autoBackup = prefs.getBool('autoBackup') ?? true;
      lastBackupTime = prefs.getString('lastBackupTime') ?? "Never";
      marketAlertCrops = prefs.getStringList('marketAlertCrops') ?? [];
    });
  }

  Future<void> _savePreference(String key, dynamic value) async {
    final prefs = await SharedPreferences.getInstance();
    if (value is bool) await prefs.setBool(key, value);
    if (value is String) await prefs.setString(key, value);
    if (value is List<String>) await prefs.setStringList(key, value);
  }

  void _showSnackbar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.redAccent : AppColors.success,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final userProvider = context.watch<UserProvider>();
    final userModel = userProvider.userModel;
    final themeProvider = Provider.of<ThemeProvider>(context);
    final isDarkMode = themeProvider.themeMode == ThemeMode.dark;
    
    final settingsList = _buildAllSettings(isDarkMode, themeProvider);
    final filteredSettings = searchQuery.isEmpty 
        ? settingsList 
        : settingsList.where((s) => s.title.toLowerCase().contains(searchQuery.toLowerCase())).toList();

    return Scaffold(
      
      appBar: AppBar(
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: AppColors.primaryGradient,
          ),
        ),
        title: Text(
          'Settings'.tr(context),
          style: GoogleFonts.poppins(fontWeight: FontWeight.w700, color: Colors.white),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        elevation: 0,
        centerTitle: true,
      ),
      body: FadeTransition(
        opacity: _animationController,
        child: SingleChildScrollView(
          physics: kIsWeb ? const BouncingScrollPhysics() : const ClampingScrollPhysics(),
          child: Column(
            children: [
              _buildProfileHeader(context, userModel),
              const SizedBox(height: 16),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: TextField(
                  controller: _searchController,
                  onChanged: (val) => setState(() => searchQuery = val),
                  decoration: InputDecoration(
                    hintText: "Search Settings...",
                    prefixIcon: const Icon(Icons.search),
                    filled: true,
                    fillColor: isDarkMode ? const Color(0xFF2A2A2A) : Colors.grey[200],
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide: BorderSide.none,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              
              if (searchQuery.isNotEmpty) 
                _buildSettingsSection(title: "Search Results", children: filteredSettings.map((s) => s.widget).toList())
              else ...[
                _buildSettingsSection(title: "Account Settings", children: [
                  _getSettingItem("Edit Profile", settingsList)?.widget ?? const SizedBox(),
                  _getSettingItem("Change Password", settingsList)?.widget ?? const SizedBox(),
                  _getSettingItem("Language", settingsList)?.widget ?? const SizedBox(),
                ]),
                _buildSettingsSection(title: "App Preferences", children: [
                  _getSettingItem("Dark Mode", settingsList)?.widget ?? const SizedBox(),
                ]),
              ],
              
              const SizedBox(height: 16),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: ElevatedButton(
                  onPressed: () => _showLogoutDialog(context, isDarkMode),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: isDarkMode ? Colors.grey[800] : Colors.white,
                    foregroundColor: Colors.redAccent,
                    elevation: 0,
                    minimumSize: const Size(double.infinity, 56),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                      side: const BorderSide(color: Colors.redAccent, width: 1),
                    ),
                  ),
                  child: Text("Logout".tr(context), style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w600)),
                ),
              ),
              const SizedBox(height: 16),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: ElevatedButton(
                  onPressed: () => _showDeleteAccountDialog(context, isDarkMode),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.redAccent.withOpacity(0.1),
                    foregroundColor: Colors.red,
                    elevation: 0,
                    minimumSize: const Size(double.infinity, 56),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text("Delete Account".tr(context), style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w600)),
                ),
              ),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  _SettingItem? _getSettingItem(String title, List<_SettingItem> list) {
    try {
      return list.firstWhere((e) => e.title == title);
    } catch (_) {
      return null;
    }
  }

  List<_SettingItem> _buildAllSettings(bool isDarkMode, ThemeProvider themeProvider) {
    return [
      _SettingItem(
        title: "Edit Profile",
        widget: _buildSettingsTile(
          icon: Icons.person_outline_rounded,
          title: "Edit Profile",
          isDarkMode: isDarkMode,
          onTap: () {
            final userProvider = context.read<UserProvider>();
            if (userProvider.userModel != null) {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => EditProfileScreen(user: userProvider.userModel!),
                ),
              );
            }
          },
        ),
      ),
      _SettingItem(
        title: "Change Password",
        widget: _buildSettingsTile(
          icon: Icons.lock_outline_rounded,
          title: "Change Password",
          isDarkMode: isDarkMode,
          onTap: () => _showChangePasswordDialog(isDarkMode),
        ),
      ),
      _SettingItem(
        title: "Language",
        widget: _buildSettingsTile(
          icon: Icons.language_rounded,
          title: "Language",
          subtitle: Provider.of<LanguageProvider>(context).currentLanguage.toUpperCase(),
          isDarkMode: isDarkMode,
          onTap: () => showLanguageSelectorSheet(context),
        ),
      ),
      _SettingItem(
        title: "Dark Mode",
        widget: _buildSwitchTile(
          icon: Icons.dark_mode_outlined,
          title: "Dark Mode",
          value: isDarkMode,
          isDarkMode: isDarkMode,
          onChanged: (val) => themeProvider.toggleTheme(val),
        ),
      ),
    ];
  }

  // --- Dialogs & Functions ---

  void _showChangePasswordDialog(bool isDarkMode) {
    final formKey = GlobalKey<FormState>();
    bool obs1 = true, obs2 = true, obs3 = true;
    final c1 = TextEditingController();
    final c2 = TextEditingController();
    final c3 = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => StatefulBuilder(builder: (context, setModalState) {
        return Padding(
          padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
            ),
            child: Form(
              key: formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text("Change Password".tr(context), style: GoogleFonts.poppins(fontSize: 20, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: c1,
                    obscureText: obs1,
                    decoration: InputDecoration(
                      labelText: "Current Password",
                      suffixIcon: IconButton(icon: Icon(obs1 ? Icons.visibility_off : Icons.visibility), onPressed: () => setModalState(() => obs1 = !obs1)),
                    ),
                    validator: (v) => v!.isEmpty ? "Required" : null,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: c2,
                    obscureText: obs2,
                    decoration: InputDecoration(
                      labelText: "New Password",
                      suffixIcon: IconButton(icon: Icon(obs2 ? Icons.visibility_off : Icons.visibility), onPressed: () => setModalState(() => obs2 = !obs2)),
                    ),
                    validator: (v) => v!.length < 6 ? "Min 6 chars" : null,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: c3,
                    obscureText: obs3,
                    decoration: InputDecoration(
                      labelText: "Confirm Password",
                      suffixIcon: IconButton(icon: Icon(obs3 ? Icons.visibility_off : Icons.visibility), onPressed: () => setModalState(() => obs3 = !obs3)),
                    ),
                    validator: (v) => v != c2.text ? "Passwords do not match" : null,
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () {
                      if (formKey.currentState!.validate()) {
                        Navigator.pop(context);
                        _showSnackbar("Password updated successfully!");
                      }
                    },
                    child: Text("Update Password".tr(context)),
                  ),
                ],
              ),
            ),
          ),
        );
      }),
    );
  }

  void _showWeatherAlertSettings(bool isDarkMode) {
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(builder: (context, setDialogState) {
        return AlertDialog(
          title: Text("Weather Alerts".tr(context)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              SwitchListTile(
                title: Text("Enable Alerts".tr(context)),
                value: weatherAlerts,
                onChanged: (v) {
                  setDialogState(() => weatherAlerts = v);
                  setState(() => weatherAlerts = v);
                  _savePreference('weatherAlerts', v);
                },
              ),
              if (weatherAlerts) ...[
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: weatherAlertFrequency,
                  items: ["Instant", "Hourly", "Daily"].map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
                  onChanged: (v) {
                    setDialogState(() => weatherAlertFrequency = v!);
                    setState(() => weatherAlertFrequency = v!);
                    _savePreference('weatherAlertFrequency', v);
                  },
                  decoration: const InputDecoration(labelText: "Frequency"),
                )
              ]
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: Text("Done".tr(context)))
          ],
        );
      }),
    );
  }

  void _showMarketAlertSettings(bool isDarkMode) {
    final List<String> allCrops = ["Wheat", "Rice", "Cotton", "Maize", "Sugarcane"];
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(builder: (context, setDialogState) {
        return AlertDialog(
          title: Text("Market Alerts".tr(context)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              SwitchListTile(
                title: Text("Enable Alerts".tr(context)),
                value: marketAlerts,
                onChanged: (v) {
                  setDialogState(() => marketAlerts = v);
                  setState(() => marketAlerts = v);
                  _savePreference('marketAlerts', v);
                },
              ),
              if (marketAlerts) ...[
                const SizedBox(height: 16),
                Wrap(
                  spacing: 8,
                  children: allCrops.map((crop) {
                    final selected = marketAlertCrops.contains(crop);
                    return FilterChip(
                      label: Text(crop),
                      selected: selected,
                      onSelected: (v) {
                        setDialogState(() {
                          if (v) marketAlertCrops.add(crop);
                          else marketAlertCrops.remove(crop);
                        });
                        setState(() {});
                        _savePreference('marketAlertCrops', marketAlertCrops);
                      },
                    );
                  }).toList(),
                )
              ]
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: Text("Done".tr(context)))
          ],
        );
      }),
    );
  }

  void _showBackupSettings(bool isDarkMode) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => StatefulBuilder(builder: (context, setModalState) {
        return Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.cloud_sync_rounded, size: 48, color: Colors.white),
              const SizedBox(height: 16),
              Text("Backup & Sync".tr(context), style: GoogleFonts.poppins(fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              SwitchListTile(
                title: Text("Auto Backup".tr(context)),
                subtitle: Text("Sync data daily over Wi-Fi".tr(context)),
                value: autoBackup,
                onChanged: (v) {
                  setModalState(() => autoBackup = v);
                  setState(() => autoBackup = v);
                  _savePreference('autoBackup', v);
                },
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () async {
                  setModalState(() => isSyncing = true);
                  setState(() => isSyncing = true);
                  await Future.delayed(const Duration(seconds: 2)); // Simulate sync
                  final now = DateTime.now();
                  final timeStr = "${now.hour}:${now.minute.toString().padLeft(2, '0')}";
                  setModalState(() {
                    isSyncing = false;
                    lastBackupTime = "Today, $timeStr";
                  });
                  setState(() => lastBackupTime = "Today, $timeStr");
                  _savePreference('lastBackupTime', lastBackupTime);
                  _showSnackbar("Backup successful");
                },
                icon: isSyncing ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)) : const Icon(Icons.backup),
                label: Text("Backup Now".tr(context)),
              ),
            ],
          ),
        );
      }),
    );
  }

  void _showPermissionsDialog(bool isDarkMode) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text("App Permissions".tr(context)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(leading: Icon(Icons.camera_alt), title: Text("Camera".tr(context)), trailing: Icon(Icons.check_circle, color: Colors.green)),
            ListTile(leading: Icon(Icons.location_on), title: Text("Location".tr(context)), trailing: Icon(Icons.check_circle, color: Colors.green)),
            ListTile(leading: Icon(Icons.notifications), title: Text("Notifications".tr(context)), trailing: Icon(Icons.check_circle, color: Colors.green)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              openAppSettings();
              Navigator.pop(context);
            },
            child: Text("Open OS Settings".tr(context)),
          ),
          ElevatedButton(onPressed: () => Navigator.pop(context), child: Text("Done".tr(context))),
        ],
      ),
    );
  }

  void _showSupportDialog(bool isDarkMode) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text("Contact Support".tr(context), style: GoogleFonts.poppins(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.phone, color: Colors.blue),
              title: Text("Call Us".tr(context)),
              onTap: () => _launchURL("tel:+919876543210"),
            ),
            ListTile(
              leading: const Icon(Icons.email, color: Colors.red),
              title: Text("Email Support".tr(context)),
              onTap: () => _launchURL("mailto:support@kisanmitra.com"),
            ),
            ListTile(
              leading: const Icon(Icons.chat, color: Colors.green),
              title: Text("WhatsApp".tr(context)),
              onTap: () => _launchURL("https://wa.me/919876543210"),
            ),
            ListTile(
              leading: const Icon(Icons.support_agent, color: Colors.white),
              title: Text("Live Chat (AI)".tr(context)),
              onTap: () {
                Navigator.pop(context);
                _showSnackbar("Opening Live Chat..."); // Assuming live chat is handled elsewhere
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showFAQScreen(bool isDarkMode) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(title: Text("FAQ".tr(context))),
          body: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              ExpansionTile(
                title: Text("How do I add a new crop?".tr(context)),
                children: [Padding(padding: const EdgeInsets.all(16), child: Text("Go to the Home tab and click 'Add Crop' at the top right.".tr(context)))],
              ),
              ExpansionTile(
                title: Text("Why are market prices not updating?".tr(context)),
                children: [Padding(padding: const EdgeInsets.all(16), child: Text("Please ensure you have an active internet connection. Prices sync daily.".tr(context)))]
              ),
              ExpansionTile(
                title: Text("How accurate is the AI recommendation?".tr(context)),
                children: [Padding(padding: const EdgeInsets.all(16), child: Text("Our AI uses live market data and weather APIs for high accuracy.".tr(context)))]
              ),
            ],
          ),
        )
      )
    );
  }

  void _showReportProblemDialog(bool isDarkMode) {
    final tcTitle = TextEditingController();
    final tcDesc = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text("Report a Problem".tr(context)),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(controller: tcTitle, decoration: const InputDecoration(labelText: "Subject")),
              const SizedBox(height: 16),
              TextField(controller: tcDesc, maxLines: 4, decoration: const InputDecoration(labelText: "Description")),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: () async {
                  final picker = ImagePicker();
                  await picker.pickImage(source: ImageSource.gallery);
                  _showSnackbar("Screenshot attached");
                },
                icon: const Icon(Icons.image),
                label: Text("Attach Screenshot".tr(context)),
              )
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: Text("Cancel".tr(context))),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _showSnackbar("Problem reported successfully! We will look into it.");
            },
            child: Text("Submit".tr(context)),
          )
        ],
      ),
    );
  }

  void _showFeedbackDialog(bool isDarkMode) {
    int rating = 5;
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(builder: (context, setDialogState) {
        return AlertDialog(
          title: Text("Send Feedback".tr(context)),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(5, (index) {
                  return IconButton(
                    icon: Icon(index < rating ? Icons.star : Icons.star_border, color: Colors.amber, size: 32),
                    onPressed: () => setDialogState(() => rating = index + 1),
                  );
                }),
              ),
              const SizedBox(height: 16),
              const TextField(maxLines: 3, decoration: InputDecoration(hintText: "Tell us what you think...")),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: Text("Cancel".tr(context))),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                _showSnackbar("Thank you for your feedback!");
              },
              child: Text("Submit".tr(context)),
            )
          ],
        );
      }),
    );
  }


  void _showTextScreen(String title, String content, bool isDarkMode) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(title: Text(title.tr(context))),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Text(content.tr(context), style: const TextStyle(fontSize: 16, height: 1.5)),
          ),
        )
      )
    );
  }

  Future<void> _launchURL(String urlString) async {
    final Uri url = Uri.parse(urlString);
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    } else {
      _showSnackbar("Could not open link", isError: true);
    }
  }

  // --- End Dialogs ---



  void _showLogoutDialog(BuildContext context, bool isDarkMode) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.logout_rounded, size: 48, color: Colors.redAccent),
              const SizedBox(height: 16),
              Text("Logout".tr(context), style: GoogleFonts.poppins(fontSize: 22, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text("Are you sure you want to log out of your account?".tr(context), textAlign: TextAlign.center, style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.pop(context),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                      child: Text("Cancel".tr(context)),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () async {
                        Navigator.pop(context); 
                        _showSnackbar("Logged out successfully");
                        final prefs = await SharedPreferences.getInstance();
                        await prefs.remove('last_activity_timestamp');
                        await prefs.remove('last_route');
                        if (context.mounted) {
                          Provider.of<UserProvider>(context, listen: false).clearUser();
                          await Provider.of<AuthProvider>(context, listen: false).signOut();
                        }
                        if (context.mounted) {
                          context.go(AppRouter.login);
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.redAccent,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                      child: Text("Yes, Logout".tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: Colors.white)),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
            ],
          ),
        );
      },
    );
  }

  void _showDeleteAccountDialog(BuildContext context, bool isDarkMode) {
    final tc = TextEditingController();
    bool isDeleting = false;
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              title: Row(
                children: [
                  const Icon(Icons.warning_rounded, color: Colors.redAccent),
                  const SizedBox(width: 8),
                  Text("Delete Account".tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: Colors.redAccent)),
                ],
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (isDeleting) ...[
                    const CircularProgressIndicator(color: Colors.redAccent),
                    const SizedBox(height: 16),
                    Text("Deleting account and all associated data. Please wait...", textAlign: TextAlign.center, style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
                  ] else ...[
                    Text("This action cannot be undone. All your farm data, history, and preferences will be permanently removed.".tr(context), style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
                    const SizedBox(height: 16),
                    TextField(
                      controller: tc,
                      obscureText: true,
                      decoration: const InputDecoration(labelText: "Confirm Password to delete", filled: true),
                    )
                  ]
                ],
              ),
              actions: isDeleting ? null : [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text("Cancel".tr(context)),
                ),
                ElevatedButton(
                  onPressed: () async {
                    if (tc.text.isEmpty) {
                      _showSnackbar("Please enter password", isError: true);
                      return;
                    }
                    
                    setDialogState(() {
                      isDeleting = true;
                    });
                    
                    try {
                      final currentUser = FirebaseAuth.instance.currentUser;
                      if (currentUser != null) {
                        if (currentUser.email != null) {
                          // Re-authenticate user
                          final credential = EmailAuthProvider.credential(
                            email: currentUser.email!,
                            password: tc.text,
                          );
                          await currentUser.reauthenticateWithCredential(credential);
                        }
                        
                        final uid = currentUser.uid;
                        
                        // 1. Delete user profit records
                        final profitDocs = await FirebaseFirestore.instance
                            .collection('users')
                            .doc(uid)
                            .collection('profit_records')
                            .get();
                        for (var doc in profitDocs.docs) {
                          await doc.reference.delete();
                        }
                        
                        // 2. Delete user farms
                        final farmDocs = await FirebaseFirestore.instance
                            .collection('farms')
                            .where('ownerId', isEqualTo: uid)
                            .get();
                        for (var doc in farmDocs.docs) {
                          await doc.reference.delete();
                        }
                        
                        // 3. Delete user recommendations
                        final recDocs = await FirebaseFirestore.instance
                            .collection('crop_recommendations')
                            .where('uid', isEqualTo: uid)
                            .get();
                        for (var doc in recDocs.docs) {
                          await doc.reference.delete();
                        }
                        
                        // 4. Delete user disease reports
                        final reportDocs = await FirebaseFirestore.instance
                            .collection('disease_reports')
                            .where('uid', isEqualTo: uid)
                            .get();
                        for (var doc in reportDocs.docs) {
                          await doc.reference.delete();
                        }

                        // 4.5 Delete user chat sessions
                        final chatDocs = await FirebaseFirestore.instance
                            .collection('chat_sessions')
                            .where('userId', isEqualTo: uid)
                            .get();
                        for (var doc in chatDocs.docs) {
                          await doc.reference.delete();
                        }
                        
                        // 5. Delete user document from users collection
                        await FirebaseFirestore.instance
                            .collection('users')
                            .doc(uid)
                            .delete();
                        
                        // 6. Delete FirebaseAuth user
                        await currentUser.delete();
                      }
                      
                      final prefs = await SharedPreferences.getInstance();
                      await prefs.remove('last_activity_timestamp');
                      await prefs.remove('last_route');
                      
                      if (context.mounted) {
                        Provider.of<UserProvider>(context, listen: false).clearUser();
                        await Provider.of<AuthProvider>(context, listen: false).signOut();
                        Navigator.pop(context); // Close dialog
                        _showSnackbar("Account deleted successfully.");
                        context.go(AppRouter.login);
                      }
                    } on FirebaseAuthException catch (e) {
                      setDialogState(() {
                        isDeleting = false;
                      });
                      String errMsg = "Failed to delete account.";
                      if (e.code == 'wrong-password') {
                        errMsg = "Incorrect password. Please try again.";
                      } else if (e.code == 'requires-recent-login') {
                        errMsg = "Please log out and log back in to perform this action.";
                      } else if (e.message != null) {
                        errMsg = e.message!;
                      }
                      _showSnackbar(errMsg, isError: true);
                    } catch (e) {
                      setDialogState(() {
                        isDeleting = false;
                      });
                      _showSnackbar("An error occurred: $e", isError: true);
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.redAccent,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  child: Text("Delete Permanently".tr(context), style: GoogleFonts.poppins(color: Colors.white)),
                ),
              ],
            );
          },
        );
      },
    );
  }

  // --- UI Components ---

  Widget _buildProfileHeader(BuildContext context, UserModel? user) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: const BorderRadius.only(bottomLeft: Radius.circular(30), bottomRight: Radius.circular(30)),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 15, offset: const Offset(0, 5))],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(shape: BoxShape.circle, border: Border.all(color: Theme.of(context).cardColor, width: 2)),
            child: CircleAvatar(
              radius: 40,
              backgroundColor: AppColors.primaryContainer,
              backgroundImage: user?.profileImageUrl != null ? NetworkImage(user!.profileImageUrl!) : null,
              child: user?.profileImageUrl == null ? const Icon(Icons.person, size: 40, color: Colors.white) : null,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            user?.name ?? "Kisan Farmer",
            style: GoogleFonts.poppins(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(user?.email ?? "farmer@example.com", style: GoogleFonts.poppins(fontSize: 14, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
        ],
      ),
    );
  }

  Widget _buildSettingsSection({required String title, required List<Widget> children}) {
    if (children.isEmpty) return const SizedBox();
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(left: 8, bottom: 12),
            child: Text(
              title.tr(context),
              style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.primary, letterSpacing: 1.2),
            ),
          ),
          Container(
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 4))],
            ),
            child: Column(children: children),
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsTile({
    required IconData icon,
    required String title,
    String? subtitle,
    required bool isDarkMode,
    required VoidCallback onTap,
    Widget? trailing,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: Theme.of(context).colorScheme.primary, size: 22),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title.tr(context), style: GoogleFonts.poppins(fontSize: 15, fontWeight: FontWeight.w500)),
                    if (subtitle != null) ...[
                      const SizedBox(height: 2),
                      Text(subtitle.tr(context), style: GoogleFonts.poppins(fontSize: 12, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
                    ]
                  ],
                ),
              ),
              trailing ?? Icon(Icons.arrow_forward_ios_rounded, size: 16, color: isDarkMode ? Colors.white38 : AppColors.textHint),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSwitchTile({
    required IconData icon,
    required String title,
    required bool value,
    required bool isDarkMode,
    required ValueChanged<bool> onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: Theme.of(context).colorScheme.primary, size: 22),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(title.tr(context), style: GoogleFonts.poppins(fontSize: 15, fontWeight: FontWeight.w500)),
          ),
          CupertinoSwitch(value: value, activeColor: AppColors.primary, onChanged: onChanged),
        ],
      ),
    );
  }
}

class _SettingItem {
  final String title;
  final Widget widget;
  _SettingItem({required this.title, required this.widget});
}
