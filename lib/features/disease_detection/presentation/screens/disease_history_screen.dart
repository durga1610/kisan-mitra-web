import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../data/models/disease_report.dart';
import '../../data/services/disease_detection_service.dart';

class DiseaseHistoryScreen extends StatelessWidget {
  const DiseaseHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final detectionService = DiseaseDetectionService();

    return Scaffold(
      
      appBar: AppBar(
        title: Text('Scan History'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w600)),
        
        elevation: 0,
      ),
      body: StreamBuilder<List<DiseaseReport>>(
        stream: detectionService.getHistory(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator(color: Colors.white));
          }
          
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return _buildEmptyState(context);
          }

          final history = snapshot.data!;
          return ListView.builder(
            padding: const EdgeInsets.all(AppDimensions.paddingLG),
            itemCount: history.length,
            itemBuilder: (context, index) {
              return _buildHistoryCard(context, history[index]);
            },
          );
        },
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.history_rounded, size: 80, color: AppColors.divider),
          const SizedBox(height: 16),
          Text(
            'No Scan History',
            style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.w600, color: Colors.white),
          ),
          const SizedBox(height: 8),
          Text(
            'Start scanning plant leaves to detect diseases.',
            style: GoogleFonts.poppins(fontSize: 14, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryCard(BuildContext context, DiseaseReport report) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 10, offset: const Offset(0, 4)),
        ],
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(12),
        leading: ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: Image.network(
            report.imageUrl,
            width: 60,
            height: 60,
            fit: BoxFit.cover,
            errorBuilder: (_, __, ___) => Container(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5), child: Icon(Icons.broken_image)),
          ),
        ),
        title: Text(
          report.diseaseName,
          style: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 15),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(report.plantName, style: GoogleFonts.poppins(fontSize: 13, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
            const SizedBox(height: 4),
            Text(
              DateFormat('MMM dd, yyyy • hh:mm a').format(report.timestamp),
              style: GoogleFonts.poppins(fontSize: 11, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
            ),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: _getSeverityColor(context, report.severity).withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            report.severity,
            style: GoogleFonts.poppins(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: _getSeverityColor(context, report.severity),
            ),
          ),
        ),
        onTap: () {
          // You could navigate to a detail view here, 
          // or just show a simplified version of the result card
        },
      ),
    );
  }

  Color _getSeverityColor(BuildContext context, String severity) {
    switch (severity.toLowerCase()) {
      case 'high': return AppColors.error;
      case 'medium': return Colors.orange;
      case 'low': return AppColors.success;
      default: return Theme.of(context).colorScheme.onSurface;
    }
  }
}
