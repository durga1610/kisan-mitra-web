import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:provider/provider.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/models/farm_model.dart';
import '../../../../core/widgets/km_text_field.dart';
import '../../../../core/widgets/km_button.dart';
import '../../../profile_setup/data/profile_setup_data.dart';

class EditFarmScreen extends StatefulWidget {
  final FarmModel? farm; // Null if adding a new farm

  const EditFarmScreen({super.key, this.farm});

  @override
  State<EditFarmScreen> createState() => _EditFarmScreenState();
}

class _EditFarmScreenState extends State<EditFarmScreen> {
  final _formKey = GlobalKey<FormState>();
  
  late TextEditingController _nameController;
  late TextEditingController _districtController;
  late TextEditingController _stateController;
  late TextEditingController _villageController;
  late TextEditingController _landAreaController;
  
  String? _selectedSoilType;
  String? _selectedWater;
  bool _isLoading = false;

  final List<String> _soilTypes = ProfileSetupData.soilTypes.map((e) => e['name'] as String).toList();
  final List<String> _waterLevels = ProfileSetupData.waterAvailabilityOptions;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.farm?.name ?? '');
    _districtController = TextEditingController(text: widget.farm?.district ?? '');
    _stateController = TextEditingController(text: widget.farm?.state ?? '');
    _villageController = TextEditingController(text: widget.farm?.village ?? '');
    _landAreaController = TextEditingController(text: widget.farm?.landArea?.toString() ?? '');
    
    if (widget.farm != null) {
      if (_soilTypes.contains(widget.farm!.soilType)) {
        _selectedSoilType = widget.farm!.soilType;
      }
      if (_waterLevels.contains(widget.farm!.waterAvailability)) {
        _selectedWater = widget.farm!.waterAvailability;
      }
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _districtController.dispose();
    _stateController.dispose();
    _villageController.dispose();
    _landAreaController.dispose();
    super.dispose();
  }

  Future<void> _saveFarm() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedSoilType == null || _selectedWater == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please select Soil Type and Water Availability'.tr(context))),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final user = Provider.of<AuthProvider>(context, listen: false).user;
      if (user == null) return;

      final farmData = {
        'ownerId': user.uid,
        'name': _nameController.text.trim(),
        'state': _stateController.text.trim(),
        'district': _districtController.text.trim(),
        'village': _villageController.text.trim(),
        'soilType': _selectedSoilType,
        'landArea': double.tryParse(_landAreaController.text) ?? 0.0,
        'waterAvailability': _selectedWater,
        'updatedAt': DateTime.now().toIso8601String(),
        'preferredCrops': widget.farm?.preferredCrops ?? [],
      };

      if (widget.farm?.id != null) {
        await FirebaseFirestore.instance.collection('farms').doc(widget.farm!.id).update(farmData);
      } else {
        await FirebaseFirestore.instance.collection('farms').add(farmData);
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Field saved successfully!'.tr(context)), backgroundColor: AppColors.success),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: AppColors.error),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isNew = widget.farm == null;

    return Scaffold(
      
      appBar: AppBar(
        title: Text(isNew ? 'Add New Field' : 'Edit Field', style: GoogleFonts.poppins(fontWeight: FontWeight.w600)),
        
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppDimensions.paddingLG),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildSectionTitle('Field Details'),
              const SizedBox(height: 16),
              KMTextField(
                controller: _nameController,
                label: 'Field Name',
                hint: 'e.g. North Farm',
                prefixIcon: Icons.drive_file_rename_outline_rounded,
                validator: (v) => v == null || v.isEmpty ? 'Field Name is required' : null,
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: KMTextField(
                      controller: _villageController,
                      label: 'Village',
                      hint: 'Village name',
                      validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: KMTextField(
                      controller: _districtController,
                      label: 'District',
                      hint: 'District name',
                      validator: (v) => v == null || v.isEmpty ? 'Required' : null,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              KMTextField(
                controller: _stateController,
                label: 'State',
                hint: 'Enter state',
                prefixIcon: Icons.location_on_outlined,
                validator: (v) => v == null || v.isEmpty ? 'State is required' : null,
              ),
              const SizedBox(height: 16),
              KMTextField(
                controller: _landAreaController,
                label: 'Land Area (Acres)',
                hint: 'e.g. 5.5',
                prefixIcon: Icons.landscape_outlined,
                keyboardType: TextInputType.number,
                validator: (v) => v == null || v.isEmpty ? 'Land Area is required' : null,
              ),
              const SizedBox(height: 16),
              _buildDropdown('Soil Type', _soilTypes, _selectedSoilType, (v) => setState(() => _selectedSoilType = v)),
              const SizedBox(height: 16),
              _buildDropdown('Water Availability', _waterLevels, _selectedWater, (v) => setState(() => _selectedWater = v)),
              const SizedBox(height: 40),
              KMButton(
                label: 'Save Field',
                onPressed: _saveFarm,
                isLoading: _isLoading,
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.primary),
    );
  }

  Widget _buildDropdown(String label, List<String> items, String? value, Function(String?) onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: GoogleFonts.poppins(fontSize: 14, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.divider),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: value,
              hint: Text('Select $label', style: GoogleFonts.poppins(color: AppColors.textHint)),
              isExpanded: true,
              items: items.map((t) => DropdownMenuItem(value: t, child: Text(t, style: GoogleFonts.poppins()))).toList(),
              onChanged: onChanged,
            ),
          ),
        ),
      ],
    );
  }
}
