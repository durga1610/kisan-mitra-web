import 'dart:io';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:image_picker/image_picker.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import '../../../../config/routes/app_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/providers/language_provider.dart';
import 'package:provider/provider.dart';
import '../../data/models/disease_report.dart';
import '../../data/services/disease_detection_service.dart';
import '../widgets/web_camera_dialog.dart';

class DiseaseDetectionScreen extends StatefulWidget {
  const DiseaseDetectionScreen({super.key});

  @override
  State<DiseaseDetectionScreen> createState() => _DiseaseDetectionScreenState();
}

class _DiseaseDetectionScreenState extends State<DiseaseDetectionScreen> {
  final ImagePicker _picker = ImagePicker();
  final DiseaseDetectionService _detectionService = DiseaseDetectionService();
  
  XFile? _selectedImage;
  bool _isProcessing = false;
  DiseaseReport? _result;

  Future<void> _pickImage(ImageSource source) async {
    if (_isProcessing) return;

    try {
      XFile? image;
      
      if (kIsWeb && source == ImageSource.camera) {
        image = await showDialog<XFile>(
          context: context,
          barrierDismissible: false,
          builder: (context) => const WebCameraDialog(),
        );
      } else {
        image = await _picker.pickImage(
          source: source,
          imageQuality: 80,
          maxWidth: 1024,
          preferredCameraDevice: source == ImageSource.camera ? CameraDevice.rear : CameraDevice.front,
        );
      }

      if (image != null) {
        setState(() {
          _selectedImage = image;
          _result = null;
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(source == ImageSource.camera ? 'Photo captured successfully!' : 'Image selected successfully!'),
            backgroundColor: AppColors.success,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      _showError('Failed to access ${source == ImageSource.camera ? 'camera' : 'gallery'}. Please check permissions.');
    }
  }

  Future<void> _processImage() async {
    if (_selectedImage == null || _isProcessing) return;

    setState(() {
      _isProcessing = true;
    });

    try {
      final lang = Provider.of<LanguageProvider>(context, listen: false).currentLanguage;
      final report = await _detectionService.detectAndSave(_selectedImage!, languageCode: lang);
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });
        context.push(AppRouter.diseaseResult, extra: report);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });
        _showError('AI analysis failed. Please try again.');
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppColors.error),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      
      appBar: AppBar(
        title: Text('Scan Plant Disease'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: Colors.white)),
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            icon: const Icon(Icons.history_rounded, color: Colors.white),
            onPressed: () => context.push(AppRouter.diseaseHistory),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppDimensions.paddingLG),
        child: Column(
          children: [
            if (_selectedImage == null) _buildUploadPlaceholder(),
            if (_selectedImage != null && !_isProcessing && _result == null) _buildImagePreview(),
            if (_isProcessing) _buildScanningEffect(),
            if (_result != null) _buildResultCard(),
            
            const SizedBox(height: 24),
            if (!_isProcessing) _buildActionButtons(),
          ],
        ),
      ),
    );
  }

  Widget _buildUploadPlaceholder() {
    return Container(
      width: double.infinity,
      height: 300,
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.divider, width: 2),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.add_a_photo_outlined, size: 64, color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.5)),
          const SizedBox(height: 16),
          Text(
            'Upload Leaf Photo',
            style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.onSurface),
          ),
          const SizedBox(height: 8),
          Text(
            'Capture or select an image of the affected plant leaf',
            textAlign: TextAlign.center,
            style: GoogleFonts.poppins(fontSize: 14, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
          ),
        ],
      ),
    ).animate().fadeIn().scale();
  }

  Widget _buildImagePreview() {
    return Column(
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: kIsWeb 
            ? Image.network(_selectedImage!.path, height: 300, width: double.infinity, fit: BoxFit.cover)
            : Image.file(File(_selectedImage!.path), height: 300, width: double.infinity, fit: BoxFit.cover),
        ),
        const SizedBox(height: 20),
        ElevatedButton.icon(
          onPressed: _processImage,
          icon: const Icon(Icons.analytics_outlined, color: Colors.white),
          label: Text('Start AI Analysis'.tr(context)),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          ),
        ).animate().shimmer(delay: 400.ms),
      ],
    );
  }

  Widget _buildScanningEffect() {
    return Column(
      children: [
        Stack(
          alignment: Alignment.center,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(24),
              child: kIsWeb
                ? Image.network(_selectedImage!.path, height: 300, width: double.infinity, fit: BoxFit.cover, opacity: const AlwaysStoppedAnimation(0.6))
                : Image.file(File(_selectedImage!.path), height: 300, width: double.infinity, fit: BoxFit.cover, opacity: const AlwaysStoppedAnimation(0.6)),
            ),
            Positioned.fill(
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(24),
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.transparent,
                      AppColors.primary.withValues(alpha: 0.3),
                      Colors.transparent,
                    ],
                    stops: const [0.0, 0.5, 1.0],
                  ),
                ),
              ).animate(onPlay: (controller) => controller.repeat())
               .moveY(begin: -150, end: 150, duration: 1500.ms),
            ),
          ],
        ),
        const SizedBox(height: 24),
        const CircularProgressIndicator(color: AppColors.primary),
        const SizedBox(height: 16),
        Text(
          'Kisan Mitra AI is scanning...',
          style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.onSurface),
        ),
      ],
    );
  }

  Widget _buildResultCard() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildInfoCard(
          title: 'Detection Result',
          color: _result!.severity == 'High' ? AppColors.error : AppColors.primary,
          child: Column(
            children: [
              _buildResultRow('Plant', _result!.plantName, Icons.grass_rounded),
              _buildResultRow('Disease', _result!.diseaseName, Icons.bug_report_rounded),
              _buildResultRow('Confidence', '${_result!.confidence.toStringAsFixed(1)}%', Icons.analytics_rounded),
              _buildResultRow('Severity', _result!.severity, Icons.warning_rounded, color: _getSeverityColor(_result!.severity)),
            ],
          ),
        ),
        const SizedBox(height: 16),
        _buildInfoCard(
          title: 'Symptoms & Causes',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDetailSection('Symptoms', _result!.symptoms),
              const Divider(),
              _buildDetailSection('Causes', _result!.causes),
            ],
          ),
        ),
        const SizedBox(height: 16),
        _buildInfoCard(
          title: 'Recommendations',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildDetailSection('Treatment', _result!.treatment, icon: Icons.medication_rounded),
              const Divider(),
              _buildDetailSection('Prevention', _result!.prevention, icon: Icons.shield_rounded),
            ],
          ),
        ),
      ],
    ).animate().fadeIn(duration: 600.ms).slideY(begin: 0.1, end: 0);
  }

  Widget _buildInfoCard({required String title, required Widget child, Color? color}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10, offset: const Offset(0, 4)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700, color: color ?? Theme.of(context).colorScheme.onSurface)),
          const SizedBox(height: 16),
          child,
        ],
      ),
    );
  }

  Widget _buildResultRow(String label, String value, IconData icon, {Color? color}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(icon, size: 20, color: color ?? AppColors.primary),
          const SizedBox(width: 12),
          Text('$label:', style: GoogleFonts.poppins(fontSize: 14, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
          const SizedBox(width: 8),
          Expanded(child: Text(value, style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w600, color: color ?? Theme.of(context).colorScheme.onSurface))),
        ],
      ),
    );
  }

  Widget _buildDetailSection(String title, String content, {IconData? icon}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              if (icon != null) Icon(icon, size: 18, color: Colors.white),
              if (icon != null) const SizedBox(width: 8),
              Text(title, style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: 4),
          Text(content, style: GoogleFonts.poppins(fontSize: 13, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7), height: 1.5)),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    return Row(
      children: [
        Expanded(
          child: _buildGradientButton(
            onPressed: _isProcessing ? () {} : () => _pickImage(ImageSource.camera),
            label: 'Camera',
            icon: Icons.camera_alt_rounded,
            colors: _isProcessing 
                ? [Colors.grey, Colors.grey] 
                : [const Color(0xFF4CAF50), const Color(0xFF2E7D32)],
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildGradientButton(
            onPressed: _isProcessing ? () {} : () => _pickImage(ImageSource.gallery),
            label: 'Gallery',
            icon: Icons.photo_library_rounded,
            colors: _isProcessing 
                ? [Colors.grey, Colors.grey] 
                : [const Color(0xFF8BC34A), const Color(0xFF558B2F)],
          ),
        ),
      ],
    );
  }

  Widget _buildGradientButton({required VoidCallback onPressed, required String label, required IconData icon, required List<Color> colors}) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(colors: colors),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(color: colors[0].withValues(alpha: 0.3), blurRadius: 8, offset: const Offset(0, 4)),
        ],
      ),
      child: ElevatedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon, color: Colors.white, size: 20),
        label: Text(label, style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.w600)),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
      ),
    );
  }

  Color _getSeverityColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'high': return AppColors.error;
      case 'medium': return Colors.orange;
      case 'low': return AppColors.success;
      default: return Theme.of(context).colorScheme.onSurface;
    }
  }
}
