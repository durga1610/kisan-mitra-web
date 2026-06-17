import 'dart:io';
import 'dart:convert';
import 'dart:js' as js;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../data/models/disease_report.dart';
import '../../../../config/routes/app_router.dart';

class DiseaseResultScreen extends StatefulWidget {
  final DiseaseReport report;

  const DiseaseResultScreen({super.key, required this.report});

  @override
  State<DiseaseResultScreen> createState() => _DiseaseResultScreenState();
}

class _DiseaseResultScreenState extends State<DiseaseResultScreen> {
  bool _showGradCam = false;
  bool _isSpeaking = false;

  bool get isHealthy => widget.report.diseaseName.toLowerCase().contains('healthy') || widget.report.diseaseName.toLowerCase() == 'none';

  @override
  void initState() {
    super.initState();
    if (kIsWeb) {
      js.context['speechSynthesisOnEnd'] = () {
        if (mounted) {
          setState(() {
            _isSpeaking = false;
          });
        }
      };
    }
  }

  void _toggleTTS() {
    if (_isSpeaking) {
      _stopTTS();
    } else {
      _speakReport();
    }
  }

  void _stopTTS() {
    if (kIsWeb) {
      try {
        js.context.callMethod('eval', ["window.speechSynthesis.cancel();"]);
      } catch (e) {
        debugPrint('Web Speech synthesis stop failed: $e');
      }
    }
    setState(() {
      _isSpeaking = false;
    });
  }

  void _speakReport() {
    final report = widget.report;
    final text = 'Kisan Mitra AI Scan Report. Crop type is ${report.plantName}. '
        'Diagnosis is ${report.diseaseName} with ${report.severity} severity level. '
        'Symptoms: ${report.symptoms}. '
        'Treatment: ${report.treatment}. '
        'Organic alternatives: ${report.organicTreatment}.';

    setState(() {
      _isSpeaking = true;
    });

    if (kIsWeb) {
      try {
        final cleanText = text.replaceAll("'", "\\'").replaceAll("\n", " ");
        js.context.callMethod('eval', [
          "var msg = new SpeechSynthesisUtterance('$cleanText');"
          "msg.onend = function() { window.speechSynthesisOnEnd(); };"
          "window.speechSynthesis.cancel();"
          "window.speechSynthesis.speak(msg);"
        ]);
      } catch (e) {
        debugPrint('Web Speech synthesis failed: $e');
        setState(() {
          _isSpeaking = false;
        });
      }
    } else {
      debugPrint('TTS Audio Output: $text');
      // Graceful local timer on mobile mock
      Future.delayed(const Duration(seconds: 4), () {
        if (mounted) {
          setState(() {
            _isSpeaking = false;
          });
        }
      });
    }
  }

  void _shareToWhatsApp() async {
    final report = widget.report;
    final message = '*Kisan Mitra AI Disease Report*\n\n'
        '• *Crop Type:* ${report.plantName}\n'
        '• *Diagnosis:* ${report.diseaseName}\n'
        '• *Confidence:* ${report.confidence.toStringAsFixed(1)}%\n'
        '• *Severity:* ${report.severity}\n\n'
        '*Symptoms:*\n${report.symptoms}\n\n'
        '*Recommended Treatment:*\n${report.treatment}\n\n'
        '*Organic Alternative:*\n${report.organicTreatment}\n\n'
        '*Prevention Advice:*\n${report.prevention}\n\n'
        '_Diagnosed automatically by Kisan Mitra Offline TFLite pipeline_';

    final url = 'https://wa.me/?text=${Uri.encodeComponent(message)}';
    try {
      if (await canLaunchUrl(Uri.parse(url))) {
        await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not launch WhatsApp')),
        );
      }
    } catch (e) {
      debugPrint('WhatsApp share failed: $e');
    }
  }

  @override
  void dispose() {
    if (_isSpeaking) {
      _stopTTS();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          _buildSliverAppBar(context),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(AppDimensions.paddingLG),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeaderCard(context),
                  const SizedBox(height: 20),
                  if (widget.report.warning != null && widget.report.warning!.isNotEmpty) ...[
                    _buildWarningCard(context),
                    const SizedBox(height: 20),
                  ],
                  _buildConfidenceCard(context),
                  const SizedBox(height: 20),
                  _buildTopPredictionsCard(context),
                  const SizedBox(height: 20),
                  if (!isHealthy) ...[
                    _buildSeveritySection(),
                    const SizedBox(height: 20),
                    _buildDetailedCard(
                      context: context,
                      title: 'AI Decision Explanation',
                      content: widget.report.explanation,
                      icon: Icons.psychology_rounded,
                      color: Colors.purple,
                    ),
                    const SizedBox(height: 16),
                    _buildDetailedCard(
                      context: context,
                      title: 'Organic Treatment Options',
                      content: widget.report.organicTreatment,
                      icon: Icons.eco_rounded,
                      color: Colors.green,
                    ),
                    const SizedBox(height: 16),
                    _buildDetailedCard(
                      context: context,
                      title: 'Chemical Treatment Plan',
                      content: widget.report.treatment,
                      icon: Icons.medication_rounded,
                      color: Colors.redAccent,
                    ),
                    const SizedBox(height: 16),
                    _buildDetailedCard(
                      context: context,
                      title: 'Suggested Products',
                      content: widget.report.suggestedProducts,
                      icon: Icons.shopping_bag_rounded,
                      color: Colors.orange,
                    ),
                    const SizedBox(height: 16),
                    _buildDetailedCard(
                      context: context,
                      title: 'Prevention Tips',
                      content: widget.report.prevention,
                      icon: Icons.shield_rounded,
                      color: Colors.blue,
                    ),
                  ] else ...[
                    _buildHealthyMessage(),
                  ],
                  const SizedBox(height: 32),
                  _buildActionButtons(context),
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSliverAppBar(BuildContext context) {
    Widget imageWidget;
    if (_showGradCam && widget.report.gradcamBase64.isNotEmpty) {
      try {
        final bytes = base64Decode(widget.report.gradcamBase64);
        imageWidget = Image.memory(bytes, fit: BoxFit.cover, key: const ValueKey('gradcam_image'));
      } catch (e) {
        imageWidget = const Center(child: Icon(Icons.broken_image, size: 50));
      }
    } else {
      imageWidget = (kIsWeb || widget.report.imageUrl.startsWith('http') || widget.report.imageUrl.startsWith('https') || widget.report.imageUrl.startsWith('blob:'))
          ? Image.network(widget.report.imageUrl, fit: BoxFit.cover, key: const ValueKey('original_image'))
          : Image.file(File(widget.report.imageUrl), fit: BoxFit.cover, key: const ValueKey('original_image'));
    }

    return SliverAppBar(
      expandedHeight: 320,
      pinned: true,
      backgroundColor: AppColors.primary,
      leading: Padding(
        padding: const EdgeInsets.all(8.0),
        child: CircleAvatar(
          backgroundColor: Colors.black38,
          child: IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: () => context.pop(),
          ),
        ),
      ),
      flexibleSpace: FlexibleSpaceBar(
        background: Stack(
          fit: StackFit.expand,
          children: [
            Hero(
              tag: 'disease_image_${widget.report.id}',
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 300),
                child: imageWidget,
              ),
            ),
            Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Colors.transparent, Colors.black54],
                ),
              ),
            ),
            if (widget.report.gradcamBase64.isNotEmpty)
              Positioned(
                bottom: 16,
                right: 16,
                child: FloatingActionButton.extended(
                  onPressed: () {
                    setState(() {
                      _showGradCam = !_showGradCam;
                    });
                  },
                  icon: Icon(_showGradCam ? Icons.photo_library_rounded : Icons.psychology_rounded),
                  label: Text(_showGradCam ? 'Show Original' : 'Show AI Heatmap'),
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  elevation: 6,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeaderCard(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(28),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'CROP TYPE: ${widget.report.plantName.toUpperCase()}',
            style: GoogleFonts.poppins(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: AppColors.primary,
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            widget.report.diseaseName,
            style: GoogleFonts.poppins(
              fontSize: 22,
              fontWeight: FontWeight.w700,
              color: isHealthy ? AppColors.success : AppColors.error,
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 500.ms).slideY(begin: 0.1, end: 0);
  }

  Widget _buildWarningCard(BuildContext context) {
    final warning = widget.report.warning;
    if (warning == null || warning.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.amber.shade50,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.amber.shade200, width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.amber.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.warning_amber_rounded, color: Colors.amber.shade800, size: 24),
          const SizedBox(width: 14),
          Expanded(
            child: Text(
              warning,
              style: GoogleFonts.poppins(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: Colors.amber.shade900,
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 500.ms).slideY(begin: 0.1, end: 0);
  }

  Widget _buildConfidenceCard(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'AI Prediction Confidence',
                style: GoogleFonts.poppins(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).colorScheme.onSurface,
                ),
              ),
              Text(
                '${widget.report.confidence.toStringAsFixed(1)}%',
                style: GoogleFonts.poppins(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AppColors.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: LinearProgressIndicator(
              value: widget.report.confidence / 100.0,
              minHeight: 12,
              backgroundColor: Colors.grey.withOpacity(0.2),
              valueColor: AlwaysStoppedAnimation<Color>(
                widget.report.confidence >= 90 ? AppColors.success : Colors.orange,
              ),
            ),
          ),
        ],
      ),
    ).animate().fadeIn(delay: 100.ms);
  }

  Widget _buildSeveritySection() {
    Color severityColor = _getSeverityColor(widget.report.severity);
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: severityColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: severityColor.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          Icon(Icons.warning_amber_rounded, color: severityColor, size: 28),
          const SizedBox(width: 16),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Severity level estimate',
                style: GoogleFonts.poppins(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                  color: severityColor.withOpacity(0.8),
                ),
              ),
              Text(
                widget.report.severity,
                style: GoogleFonts.poppins(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: severityColor,
                ),
              ),
            ],
          ),
        ],
      ),
    ).animate().fadeIn(delay: 200.ms).slideX(begin: -0.05, end: 0);
  }

  Widget _buildDetailedCard({
    required BuildContext context,
    required String title,
    required String content,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              const SizedBox(width: 12),
              Text(
                title,
                style: GoogleFonts.poppins(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: Theme.of(context).colorScheme.onSurface,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...content.split(',').map((item) {
            final text = item.trim();
            if (text.isEmpty) return const SizedBox.shrink();
            return Padding(
              padding: const EdgeInsets.only(bottom: 8.0),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '• ',
                    style: GoogleFonts.poppins(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                  Expanded(
                    child: Text(
                      text,
                      style: GoogleFonts.poppins(
                        fontSize: 14,
                        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.75),
                        height: 1.6,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    ).animate().fadeIn(delay: 300.ms);
  }

  Widget _buildHealthyMessage() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [AppColors.success, AppColors.success.withOpacity(0.7)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(32),
        boxShadow: [
          BoxShadow(
            color: AppColors.success.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          const Icon(Icons.check_circle_outline_rounded, color: Colors.white, size: 80),
          const SizedBox(height: 20),
          Text(
            'Healthy Crop!',
            style: GoogleFonts.poppins(
              fontSize: 26,
              fontWeight: FontWeight.w800,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'Your plant shows no signs of disease. Keep up the good work with regular care and monitoring.',
            textAlign: TextAlign.center,
            style: GoogleFonts.poppins(
              fontSize: 14,
              color: Colors.white.withOpacity(0.9),
              height: 1.5,
            ),
          ),
        ],
      ),
    ).animate().scale(duration: 500.ms, curve: Curves.elasticOut);
  }

  Widget _buildActionButtons(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          height: 58,
          child: OutlinedButton.icon(
            onPressed: () => context.go(AppRouter.diseaseDetection),
            icon: const Icon(Icons.qr_code_scanner_rounded, color: AppColors.primary),
            label: Text(
              'Scan Another Leaf'.tr(context),
              style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 15, color: AppColors.primary),
            ),
            style: OutlinedButton.styleFrom(
              side: const BorderSide(color: AppColors.primary, width: 2),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
            ),
          ),
        ),
      ],
    ).animate().fadeIn(delay: 400.ms);
  }

  Widget _buildTopPredictionsCard(BuildContext context) {
    final predictions = widget.report.topPredictions;
    if (predictions.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Alternative Predictions',
            style: GoogleFonts.poppins(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: Theme.of(context).colorScheme.onSurface,
            ),
          ),
          const SizedBox(height: 12),
          ...predictions.map((pred) {
            final String className = pred['class'] ?? 'Unknown';
            final double conf = (pred['confidence'] ?? 0.0).toDouble();
            final displayLabel = className.replaceAll('___', ': ').replaceAll('_', ' ');

            return Padding(
              padding: const EdgeInsets.only(bottom: 12.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          displayLabel,
                          style: GoogleFonts.poppins(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.85),
                          ),
                        ),
                      ),
                      Text(
                        '${conf.toStringAsFixed(1)}%',
                        style: GoogleFonts.poppins(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          color: AppColors.primary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(6),
                    child: LinearProgressIndicator(
                      value: conf / 100.0,
                      minHeight: 6,
                      backgroundColor: Colors.grey.withOpacity(0.15),
                      valueColor: AlwaysStoppedAnimation<Color>(
                        conf >= 80 ? AppColors.success : (conf >= 30 ? Colors.orange : Colors.grey),
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    ).animate().fadeIn(delay: 150.ms);
  }

  Color _getSeverityColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'high': return AppColors.error;
      case 'medium': return Colors.orange;
      case 'low': return AppColors.success;
      default: return AppColors.primary;
    }
  }
}
