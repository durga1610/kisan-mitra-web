import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../../core/constants/app_colors.dart';
import '../../data/models/profit_models.dart';
import '../providers/profit_provider.dart';

class NewProfitRecordScreen extends StatefulWidget {
  const NewProfitRecordScreen({super.key});

  @override
  State<NewProfitRecordScreen> createState() => _NewProfitRecordScreenState();
}

class _NewProfitRecordScreenState extends State<NewProfitRecordScreen> {
  final _formKey = GlobalKey<FormState>();
  
  String _cropName = '';
  String _season = 'Kharif';
  double _landArea = 0;
  double _yield = 0;
  double _price = 0;
  
  final Map<String, double> _expenses = {
    'seed': 0,
    'fertilizer': 0,
    'pesticide': 0,
    'irrigation': 0,
    'labor': 0,
    'machinery': 0,
    'transport': 0,
    'other': 0,
  };

  double get _totalInvestment {
    return _expenses.values.fold(0, (sum, val) => sum + val);
  }

  double get _totalRevenue => _yield * _price;
  double get _netProfit => _totalRevenue - _totalInvestment;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      
      appBar: AppBar(
        title: Text('New Profit Analysis'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w700)),
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildLiveSummary(),
              const SizedBox(height: 24),
              _sectionTitle('Basic Information'),
              const SizedBox(height: 16),
              _buildTextField('Crop Name', (val) => _cropName = val),
              const SizedBox(height: 12),
              _buildDropdown('Season', ['Kharif', 'Rabi', 'Zaid'], (val) => setState(() => _season = val!)),
              const SizedBox(height: 12),
              _buildNumberField('Land Area (Acres)', (val) => setState(() => _landArea = val)),
              
              const SizedBox(height: 32),
              _sectionTitle('Expenses (₹)'),
              const SizedBox(height: 16),
              _buildExpenseGrid(),
              
              const SizedBox(height: 32),
              _sectionTitle('Yield & Selling Price'),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(child: _buildNumberField('Total Yield (Quintals)', (val) => setState(() => _yield = val))),
                  const SizedBox(width: 12),
                  Expanded(child: _buildNumberField('Price per Quintal (₹)', (val) => setState(() => _price = val))),
                ],
              ),
              const SizedBox(height: 40),
              
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: _submit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text('Save Analysis'.tr(context), style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700, color: Colors.white)),
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLiveSummary() {
    final bool isProfit = _netProfit >= 0;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: isProfit ? AppColors.primaryGradient : const LinearGradient(colors: [Colors.redAccent, Colors.red]),
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        children: [
          Text('Estimated Net Profit'.tr(context), style: GoogleFonts.poppins(color: Colors.white.withValues(alpha: 0.8), fontSize: 13)),
          const SizedBox(height: 4),
          Text('₹${_netProfit.toInt()}', style: GoogleFonts.poppins(color: Colors.white, fontSize: 32, fontWeight: FontWeight.w800)),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _summaryItem('Investment', '₹${_totalInvestment.toInt()}'),
              _summaryItem('Revenue', '₹${_totalRevenue.toInt()}'),
              _summaryItem('Margin', '${(_totalRevenue > 0 ? (_netProfit / _totalRevenue * 100) : 0).toInt()}%'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _summaryItem(String label, String value) {
    return Column(
      children: [
        Text(label, style: GoogleFonts.poppins(color: Colors.white70, fontSize: 11)),
        Text(value, style: GoogleFonts.poppins(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w700)),
      ],
    );
  }

  Widget _sectionTitle(String title) {
    return Text(title, style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.primary));
  }

  Widget _buildTextField(String label, Function(String) onChanged) {
    return TextFormField(
      decoration: _inputDecoration(label),
      validator: (val) => val == null || val.isEmpty ? 'Required' : null,
      onChanged: onChanged,
    );
  }

  Widget _buildNumberField(String label, Function(double) onChanged) {
    return TextFormField(
      keyboardType: TextInputType.number,
      decoration: _inputDecoration(label),
      validator: (val) => val == null || double.tryParse(val) == null ? 'Invalid number' : null,
      onChanged: (val) => onChanged(double.tryParse(val) ?? 0),
    );
  }

  Widget _buildDropdown(String label, List<String> items, Function(String?) onChanged) {
    return DropdownButtonFormField<String>(
      value: _season,
      decoration: _inputDecoration(label),
      items: items.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
      onChanged: onChanged,
    );
  }

  InputDecoration _inputDecoration(String label) {
    return InputDecoration(
      labelText: label,
      labelStyle: GoogleFonts.poppins(fontSize: 14, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
      filled: true,
      fillColor: Theme.of(context).cardColor,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppColors.divider)),
      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: AppColors.divider)),
    );
  }

  Widget _buildExpenseGrid() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      childAspectRatio: 2.5,
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      children: _expenses.keys.map((key) {
        return _buildNumberField(key.capitalize(), (val) => setState(() => _expenses[key] = val));
      }).toList(),
    );
  }

  void _submit() async {
    if (_formKey.currentState!.validate()) {
      final record = CropProfit(
        id: '',
        cropName: _cropName,
        season: _season,
        landArea: _landArea,
        expenses: ExpenseModel(
          seed: _expenses['seed']!,
          fertilizer: _expenses['fertilizer']!,
          pesticide: _expenses['pesticide']!,
          irrigation: _expenses['irrigation']!,
          labor: _expenses['labor']!,
          machinery: _expenses['machinery']!,
          transport: _expenses['transport']!,
          other: _expenses['other']!,
        ),
        yieldAmount: _yield,
        pricePerQuintal: _price,
        createdAt: DateTime.now(),
      );

      try {
        await Provider.of<ProfitProvider>(context, listen: false).addRecord(record);
        if (mounted) {
          Navigator.pop(context);
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Analysis saved successfully!'.tr(context))));
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
        }
      }
    }
  }
}

extension StringExtension on String {
  String capitalize() => this[0].toUpperCase() + substring(1);
}
