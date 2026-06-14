import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../providers/profit_provider.dart';
import '../widgets/profit_widgets.dart';
import 'new_profit_record_screen.dart';
import '../../../../core/localization/app_translations.dart';

class ProfitAnalyzerScreen extends StatelessWidget {
  const ProfitAnalyzerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => ProfitProvider(),
      child: const _ProfitAnalyzerContent(),
    );
  }
}

class _ProfitAnalyzerContent extends StatelessWidget {
  const _ProfitAnalyzerContent();

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ProfitProvider>();

    return Scaffold(
      
      appBar: AppBar(
        title: Text('Profit Analyzer'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18)),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list_rounded),
            onPressed: () => _showFilterDialog(context, provider),
          ),
        ],
      ),
      body: provider.records.isEmpty && !provider.isLoading
          ? _buildEmptyState(context)
          : SingleChildScrollView(
              padding: const EdgeInsets.all(AppDimensions.paddingLG),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildYearlySummary(context, provider.totalYearlyProfit),
                  const SizedBox(height: 32),
                  
                  if (provider.records.isNotEmpty) ...[
                    _sectionTitle('AI-Driven Recommendations'),
                    const SizedBox(height: 16),
                    _buildRecommendations(provider),
                    const SizedBox(height: 32),
                  ],

                  _sectionTitle('Financial History'),
                  const SizedBox(height: 16),
                  ...provider.records.map((record) => ProfitCard(
                    record: record,
                    onDelete: () => provider.deleteRecord(record.id),
                  )),
                  
                  if (provider.records.isNotEmpty) ...[
                    const SizedBox(height: 32),
                    _sectionTitle('Expense Distribution'),
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(color: Theme.of(context).cardColor, borderRadius: BorderRadius.circular(24), border: Border.all(color: AppColors.divider)),
                      child: ExpensePieChart(distribution: provider.expenseDistribution),
                    ),
                  ],
                  const SizedBox(height: 80),
                ],
              ),
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          final profitProvider = Provider.of<ProfitProvider>(context, listen: false);
          Navigator.push(context, MaterialPageRoute(builder: (_) => ChangeNotifierProvider.value(
            value: profitProvider,
            child: const NewProfitRecordScreen(),
          )));
        },
        backgroundColor: AppColors.primary,
        icon: const Icon(Icons.add_chart_rounded, color: Colors.white),
        label: Text('New Analysis'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: Colors.white)),
      ),
    );
  }

  Widget _buildYearlySummary(BuildContext context, double profit) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: AppColors.primaryGradient,
        borderRadius: BorderRadius.circular(30),
        boxShadow: [BoxShadow(color: Colors.white.withValues(alpha: 0.3), blurRadius: 20, offset: const Offset(0, 10))],
      ),
      child: Column(
        children: [
          Text('Total Yearly Net Profit'.tr(context), style: GoogleFonts.poppins(fontSize: 14, color: Colors.white.withValues(alpha: 0.8), fontWeight: FontWeight.w500)),
          const SizedBox(height: 8),
          Text('₹${profit.toInt().toString().replaceAllMapped(RegExp(r"(\d{1,3})(?=(\d{3})+(?!\d))"), (Match m) => "${m[1]},")}', 
            style: GoogleFonts.poppins(fontSize: 36, fontWeight: FontWeight.w700, color: Colors.white)),
        ],
      ),
    ).animate().fadeIn().scale();
  }

  Widget _sectionTitle(String title) {
    return Text(title, style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.w700, color: Colors.white));
  }

  Widget _buildRecommendations(ProfitProvider provider) {
    final Map<String, double> dist = provider.expenseDistribution;
    final double total = dist.values.fold(0, (s, v) => s + v);
    
    return Column(
      children: [
        if (dist['Irrigation']! > total * 0.2)
          const RecommendationCard(
            title: 'Water Management',
            message: 'Irrigation costs are higher than 20% of total expenses. Consider drip irrigation to save up to 40% on water costs.',
            icon: Icons.water_drop_outlined,
            color: Colors.blue,
          ),
        const SizedBox(height: 12),
        if (dist['Labor']! > total * 0.25)
          const RecommendationCard(
            title: 'Labor Optimization',
            message: 'High labor costs detected. Explore small-scale machinery options to improve efficiency and reduce manual dependency.',
            icon: Icons.engineering_outlined,
            color: Colors.orange,
          ),
      ],
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.analytics_outlined, size: 80, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5)),
          const SizedBox(height: 24),
          Text('No Analysis Found'.tr(context), style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface)),
          const SizedBox(height: 8),
          Text('Start your first profit analysis now.'.tr(context), style: GoogleFonts.poppins(fontSize: 14, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
        ],
      ),
    );
  }

  void _showFilterDialog(BuildContext context, ProfitProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Filter History'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w700)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            DropdownButtonFormField<String>(
              value: provider.filterSeason,
              decoration: const InputDecoration(labelText: 'Season'),
              items: ['All', 'Kharif', 'Rabi', 'Zaid'].map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
              onChanged: (val) => provider.setSeasonFilter(val!),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: provider.filterCrop,
              decoration: const InputDecoration(labelText: 'Crop'),
              items: provider.availableCrops.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
              onChanged: (val) => provider.setCropFilter(val!),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: Text('Close'.tr(context))),
        ],
      ),
    );
  }
}
