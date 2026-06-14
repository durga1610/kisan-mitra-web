import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../../core/constants/app_colors.dart';
import '../../data/models/profit_models.dart';

class ProfitCard extends StatelessWidget {
  final CropProfit record;
  final VoidCallback onDelete;

  const ProfitCard({super.key, required this.record, required this.onDelete});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 10, offset: const Offset(0, 4))],
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(record.cropName, style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
                  Text('${record.season} • ${record.landArea} Acres', style: GoogleFonts.poppins(fontSize: 12, color: AppColors.textSecondary)),
                ],
              ),
              IconButton(onPressed: onDelete, icon: const Icon(Icons.delete_outline, color: Colors.redAccent, size: 20)),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metric('Investment', '₹${record.totalInvestment.toInt()}', Colors.orange),
              _metric('Revenue', '₹${record.totalRevenue.toInt()}', AppColors.primary),
              _metric('Profit', '₹${record.netProfit.toInt()}', AppColors.success),
            ],
          ),
          const SizedBox(height: 20),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: record.profitMargin / 100,
              minHeight: 8,
              backgroundColor: AppColors.surfaceVariant,
              valueColor: AlwaysStoppedAnimation<Color>(record.netProfit >= 0 ? AppColors.success : Colors.red),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Profit Margin'.tr(context), style: GoogleFonts.poppins(fontSize: 11, color: AppColors.textSecondary)),
              Text('${record.profitMargin.toStringAsFixed(1)}%', style: GoogleFonts.poppins(fontSize: 11, fontWeight: FontWeight.w700, color: record.netProfit >= 0 ? AppColors.success : Colors.red)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metric(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: GoogleFonts.poppins(fontSize: 11, color: AppColors.textSecondary)),
        Text(value, style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w700, color: color)),
      ],
    );
  }
}

class ExpensePieChart extends StatelessWidget {
  final Map<String, double> distribution;

  const ExpensePieChart({super.key, required this.distribution});

  @override
  Widget build(BuildContext context) {
    final List<Color> colors = [
      Colors.blue, Colors.green, Colors.orange, Colors.purple,
      Colors.red, Colors.teal, Colors.indigo, Colors.brown,
    ];

    int i = 0;
    final sections = distribution.entries.where((e) => e.value > 0).map((e) {
      final color = colors[i % colors.length];
      i++;
      return PieChartSectionData(
        color: color,
        value: e.value,
        title: '${(e.value / distribution.values.fold(0.0, (s, v) => s + v) * 100).toInt()}%',
        radius: 50,
        titleStyle: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white),
      );
    }).toList();

    return Column(
      children: [
        SizedBox(
          height: 200,
          child: PieChart(PieChartData(sections: sections, sectionsSpace: 2, centerSpaceRadius: 40)),
        ),
        const SizedBox(height: 20),
        Wrap(
          spacing: 16,
          runSpacing: 8,
          children: distribution.entries.where((e) => e.value > 0).map((e) {
            final colorIndex = distribution.keys.toList().indexOf(e.key);
            return Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(width: 12, height: 12, decoration: BoxDecoration(color: colors[colorIndex % colors.length], shape: BoxShape.circle)),
                const SizedBox(width: 8),
                Text(e.key, style: GoogleFonts.poppins(fontSize: 12, color: AppColors.textSecondary)),
              ],
            );
          }).toList(),
        ),
      ],
    );
  }
}

class RecommendationCard extends StatelessWidget {
  final String title;
  final String message;
  final IconData icon;
  final Color color;

  const RecommendationCard({super.key, required this.title, required this.message, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w700, color: color)),
                const SizedBox(height: 4),
                Text(message, style: GoogleFonts.poppins(fontSize: 12, color: AppColors.textPrimary, height: 1.4)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
