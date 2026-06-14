import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../constants/app_colors.dart';
import '../providers/language_provider.dart';
import '../localization/app_translations.dart';

void showLanguageSelectorSheet(BuildContext context) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (context) {
      final langProvider = Provider.of<LanguageProvider>(context);
      final languages = [
        {'code': 'en', 'name': 'English'},
        {'code': 'hi', 'name': 'हिंदी (Hindi)'},
        {'code': 'as', 'name': 'অসমীয়া (Assamese)'},
        {'code': 'bn', 'name': 'বাংলা (Bengali)'},
        {'code': 'gu', 'name': 'ગુજરાતી (Gujarati)'},
        {'code': 'kn', 'name': 'ಕನ್ನಡ (Kannada)'},
        {'code': 'ks', 'name': 'कॉशुर (Kashmiri)'},
        {'code': 'kok', 'name': 'कोंकणी (Konkani)'},
        {'code': 'ml', 'name': 'മലയാളം (Malayalam)'},
        {'code': 'mr', 'name': 'मराठी (Marathi)'},
        {'code': 'ne', 'name': 'नेपाली (Nepali)'},
        {'code': 'or', 'name': 'ଓଡ଼ିଆ (Odia)'},
        {'code': 'pa', 'name': 'ਪੰਜਾਬੀ (Punjabi)'},
        {'code': 'sa', 'name': 'संस्कृतम् (Sanskrit)'},
        {'code': 'ta', 'name': 'தமிழ் (Tamil)'},
        {'code': 'te', 'name': 'తెలుగు (Telugu)'},
        {'code': 'ur', 'name': 'اردو (Urdu)'},
      ];

      return Container(
        height: MediaQuery.of(context).size.height * 0.7,
        padding: const EdgeInsets.only(top: 24.0, left: 24.0, right: 24.0),
        decoration: BoxDecoration(
          color: Theme.of(context).scaffoldBackgroundColor,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Select Language'.tr(context), style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                itemCount: languages.length,
                itemBuilder: (context, index) {
                  final lang = languages[index];
                  final isSelected = langProvider.currentLanguage == lang['code'];
                  return ListTile(
                    title: Text(
                      lang['name']!,
                      style: GoogleFonts.poppins(
                        fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                        color: isSelected ? AppColors.primary : Theme.of(context).textTheme.bodyLarge?.color,
                      ),
                    ),
                    trailing: isSelected ? const Icon(Icons.check_circle, color: AppColors.primary) : null,
                    onTap: () {
                      langProvider.setLanguage(lang['code']!);
                      Navigator.pop(context);
                    },
                  );
                },
              ),
            ),
          ],
        ),
      );
    },
  );
}
