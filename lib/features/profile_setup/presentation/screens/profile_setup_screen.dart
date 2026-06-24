import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/widgets/km_button.dart';
import '../../../../core/widgets/km_text_field.dart';
import '../../../../config/routes/app_router.dart';
import '../../../../core/services/auth_service.dart';
import '../../../../core/services/firestore_service.dart';
import '../../../../core/services/location_service.dart';
import '../../data/profile_setup_data.dart';

import '../../../../core/models/user_model.dart';
import '../../../../core/models/farm_model.dart';

class ProfileSetupScreen extends StatefulWidget {
  const ProfileSetupScreen({super.key});

  @override
  State<ProfileSetupScreen> createState() => _ProfileSetupScreenState();
}

class _ProfileSetupScreenState extends State<ProfileSetupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _villageController = TextEditingController();
  final _landController = TextEditingController();
  final _fieldNameController = TextEditingController();

  String? _selectedState;
  String? _selectedDistrict;
  String? _selectedSoil;
  String? _selectedWater;

  final List<FarmModel> _farms = [];
  int _currentStep = 0; // 0: Basic Info, 1: Number of Fields, 2: Field Details
  int _totalFieldsTarget = 1;
  int _currentFieldAdding = 1;

  @override
  void initState() {
    super.initState();
    _checkExistingProfile();
  }

  Future<void> _checkExistingProfile() async {
    final user = _authService.currentUser;
    if (user != null) {
      final docSnap = await _firestoreService.getDocument('users/${user.uid}');
      if (docSnap.exists) {
        final userData = docSnap.data() as Map<String, dynamic>?;
        if (userData != null && userData['setupCompleted'] == true) {
          if (mounted) {
            setState(() {
              _nameController.text = userData['name'] ?? '';
              _phoneController.text = userData['phone'] ?? '';
              _currentStep = 2; // Skip straight to field details
              _totalFieldsTarget = 1; // Just add 1 field
            });
          }
        }
      }
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _villageController.dispose();
    _landController.dispose();
    super.dispose();
  }

  bool _isLoading = false;
  final _authService = AuthService();
  final _firestoreService = FirestoreService();
  final _locationService = LocationService();
  bool _isLocating = false;

  Future<void> _detectLocation() async {
    setState(() => _isLocating = true);
    try {
      final position = await _locationService.getCurrentPosition();
      if (position != null) {
        final address = await _locationService.getAddressFromLatLng(position);
        if (address['state']?.isEmpty ?? true) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Coordinates found, but address details could not be resolved (common on Desktop).'.tr(context))),
            );
          }
          return;
        }

        setState(() {
          String addressState = (address['state'] ?? '').toLowerCase();
          String detectedState = '';
          for (var s in ProfileSetupData.states) {
            if (s.toLowerCase() == addressState || addressState.contains(s.toLowerCase())) {
              detectedState = s;
              break;
            }
          }
          
          if (detectedState.isNotEmpty) {
            _selectedState = detectedState;
            
            String addressDistrict = (address['district'] ?? '').toLowerCase();
            final districts = ProfileSetupData.getDistricts(detectedState);
            String detectedDistrict = '';
            for (var d in districts) {
              if (d.toLowerCase() == addressDistrict || addressDistrict.contains(d.toLowerCase())) {
                detectedDistrict = d;
                break;
              }
            }
            if (detectedDistrict.isNotEmpty) {
              _selectedDistrict = detectedDistrict;
            }
          }

          String village = address['village'] ?? '';
          if (village.isNotEmpty) {
            _villageController.text = village;
          }
        });
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Location detected successfully!'.tr(context))),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not auto-detect location. Please select manually from the dropdown.'.tr(context))),
        );
      }
    } finally {
      if (mounted) setState(() => _isLocating = false);
    }
  }

  void _addFarmToList() {
    if (_formKey.currentState!.validate()) {
      if (_selectedState == null || _selectedDistrict == null || _selectedSoil == null || _selectedWater == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Please complete all selections for this field'.tr(context))),
        );
        return;
      }

      setState(() {
        _farms.add(FarmModel(
          ownerId: _authService.currentUser?.uid ?? '',
          name: _fieldNameController.text.trim().isEmpty 
              ? 'Field ${_farms.length + 1}' 
              : _fieldNameController.text.trim(),
          state: _selectedState!,
          district: _selectedDistrict!,
          village: _villageController.text.trim(),
          soilType: _selectedSoil!,
          landArea: double.tryParse(_landController.text) ?? 0.0,
          waterAvailability: _selectedWater!,
          preferredCrops: [],
          updatedAt: DateTime.now(),
        ));
        
        if (_farms.length < _totalFieldsTarget) {
          // Reset for next field
          _fieldNameController.clear();
          _villageController.clear();
          _landController.clear();
          _selectedState = null;
          _selectedDistrict = null;
          _selectedSoil = null;
          _selectedWater = null;
          _currentFieldAdding++;
        } else {
          // Done adding all fields
          _currentStep = 3; // Review/Final Step
        }
      });
    }
  }

  void _removeFarm(int index) {
    setState(() => _farms.removeAt(index));
  }

  Future<void> _handleContinue() async {

    if (_currentStep == 0) {
      if (_nameController.text.trim().isEmpty || _phoneController.text.length != 10) {
        _formKey.currentState!.validate();
        return;
      }
      setState(() => _currentStep = 1);
      return;
    }

    if (_currentStep == 1) {
      setState(() => _currentStep = 2);
      return;
    }

    if (_currentStep == 2) {
      if (_farms.length < _totalFieldsTarget) {
        _addFarmToList();
        return;
      }
      setState(() => _currentStep = 3);
      return;
    }

    setState(() => _isLoading = true);
    
    try {
      final user = _authService.currentUser;
      if (user != null) {
        final userModel = UserModel(
          uid: user.uid,
          name: _nameController.text.trim(),
          phone: _phoneController.text.trim(),
          email: user.email,
          location: _farms.isNotEmpty ? "${_farms.first.district}, ${_farms.first.state}" : 'Local Farm',
          setupCompleted: true,
          updatedAt: DateTime.now(),
        );
        
        // 1. Save User
        await _firestoreService.setData(
          path: 'users/${user.uid}', 
          data: userModel.toMap()
        );
        
        // 2. Save All Farms
        for (var farm in _farms) {
          final farmRef = await _firestoreService.addData(
            collectionPath: 'farms',
            data: farm.toMap(),
          );

          // 3. Initial Recommendations for each farm
          await _firestoreService.addData(
            collectionPath: 'crop_recommendations',
            data: {
              'uid': user.uid,
              'farmId': farmRef.id,
              'recommendations': [], // Will be populated by recommendation engine
              'timestamp': DateTime.now().toIso8601String(),
              'reason': 'Initial setup for ${farm.name}',
            },
          );
        }
        
        if (mounted) {
          context.go(AppRouter.home);
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error saving profile: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      
      body: CustomScrollView(
        slivers: [
          _buildAppBar(),
          SliverPadding(
            padding: const EdgeInsets.all(AppDimensions.paddingLG),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                _buildHeader(),
                const SizedBox(height: 32),
                Form(
                  key: _formKey,
                  child: AnimatedSwitcher(
                    duration: const Duration(milliseconds: 400),
                    child: _currentStep == 0 
                        ? _buildBasicInfoStep() 
                        : _currentStep == 1 
                            ? _buildFieldCountStep()
                            : _currentStep == 2
                                ? _buildFieldDetailsStep()
                                : _buildReviewStep(),
                  ),
                ),
                const SizedBox(height: 48),
                KMButton(
                  label: _currentStep == 0 
                      ? 'Continue to Field Count' 
                      : _currentStep == 1
                          ? 'Start Adding Fields'
                          : _currentStep == 2
                              ? 'Save Field $_currentFieldAdding'
                              : 'Complete Registration',
                  onPressed: _handleContinue,
                  isLoading: _isLoading,
                ),
                if (_currentStep > 0) ...[
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: () {
                      setState(() {
                        if (_currentStep == 2 && _currentFieldAdding > 1) {
                          _currentFieldAdding--;
                          // In a real app we'd pop the last farm if we wanted to go back
                        } else {
                          _currentStep--;
                        }
                      });
                    },
                    child: Text(
                      _currentStep == 3 ? 'Back to Field Details' : 'Back to Previous Step', 
                      style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))
                    ),
                  ),
                ],
                const SizedBox(height: 40),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBasicInfoStep() {
    return Column(
      key: const ValueKey('basic_info'),
      children: [
        KMTextField(
          label: 'Farmer Name',
          hint: 'Enter your full name',
          controller: _nameController,
          prefixIcon: Icons.person_outline_rounded,
          validator: (val) => (val == null || val.isEmpty) ? 'Name is required' : null,
        ),
        const SizedBox(height: 20),
        KMTextField(
          label: 'Phone Number',
          hint: '10-digit mobile number',
          controller: _phoneController,
          prefixIcon: Icons.phone_outlined,
          keyboardType: TextInputType.phone,
          inputFormatters: [
            FilteringTextInputFormatter.digitsOnly,
            LengthLimitingTextInputFormatter(10),
          ],
          validator: (val) => (val == null || val.length != 10) ? 'Valid 10-digit phone number required' : null,
        ),
      ],
    );
  }

  Widget _buildFieldCountStep() {
    return Column(
      key: const ValueKey('field_count'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionTitle('How many different fields do you manage?'),
        const SizedBox(height: 8),
        Text(
          'We will ask for details (soil, location, area) for each field separately to provide precise recommendations.',
          style: GoogleFonts.poppins(fontSize: 13, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
        ),
        const SizedBox(height: 24),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _buildCountButton(Icons.remove, () {
              if (_totalFieldsTarget > 1) setState(() => _totalFieldsTarget--);
            }),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
              margin: const EdgeInsets.symmetric(horizontal: 20),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Theme.of(context).colorScheme.onSurface, width: 2),
              ),
              child: Text(
                '$_totalFieldsTarget',
                style: GoogleFonts.poppins(fontSize: 24, fontWeight: FontWeight.bold, color: Theme.of(context).colorScheme.onSurface),
              ),
            ),
            _buildCountButton(Icons.add, () {
              if (_totalFieldsTarget < 10) setState(() => _totalFieldsTarget++);
            }),
          ],
        ),
      ],
    );
  }

  Widget _buildCountButton(IconData icon, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          shape: BoxShape.circle,
        ),
        child: Icon(icon, color: Theme.of(context).colorScheme.onSurface),
      ),
    );
  }

  Widget _buildFieldDetailsStep() {
    return Column(
      key: const ValueKey('field_details'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor.withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.1)),
          ),
          child: Row(
            children: [
              Icon(Icons.info_outline_rounded, color: Theme.of(context).colorScheme.onSurface, size: 20),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Configuring Field $_currentFieldAdding of $_totalFieldsTarget',
                  style: GoogleFonts.poppins(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Theme.of(context).colorScheme.onSurface,
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        KMTextField(
          label: 'Field Name',
          hint: 'e.g. North Field / Home Farm',
          controller: _fieldNameController,
          prefixIcon: Icons.drive_file_rename_outline_rounded,
        ),
        const SizedBox(height: 20),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            _buildDropdownLabel('State'),
            TextButton.icon(
              onPressed: _isLocating ? null : _detectLocation,
              icon: _isLocating 
                  ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.my_location_rounded, size: 16),
              label: Text(
                _isLocating ? 'Locating...' : 'Detect Location',
                style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w600),
              ),
              style: TextButton.styleFrom(
                foregroundColor: AppColors.primary,
                padding: EdgeInsets.zero,
                minimumSize: Size.zero,
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
            ),
          ],
        ),
        _buildDropdown(
          value: _selectedState,
          hint: 'Select State',
          items: ProfileSetupData.states,
          onChanged: (val) {
            setState(() {
              _selectedState = val;
              _selectedDistrict = null;
            });
          },
        ),
        const SizedBox(height: 20),
        _buildDropdownLabel('District'),
        _buildDropdown(
          value: _selectedDistrict,
          hint: 'Select District',
          items: _selectedState == null 
              ? [] 
              : ProfileSetupData.getDistricts(_selectedState!),
          onChanged: (val) => setState(() => _selectedDistrict = val),
        ),
        const SizedBox(height: 20),
        KMTextField(
          label: 'Village Name',
          hint: 'Enter village for this field',
          controller: _villageController,
          prefixIcon: Icons.home_work_outlined,
          validator: (val) => (_currentStep == 2 && (val == null || val.isEmpty)) ? 'Village is required' : null,
        ),
        const SizedBox(height: 20),
        _buildDropdownLabel('Soil Type'),
        _buildDropdown(
          value: _selectedSoil,
          hint: 'Select Soil Type',
          items: ProfileSetupData.soilTypes.map((e) => e['name'] as String).toList(),
          onChanged: (val) => setState(() => _selectedSoil = val),
        ),
        const SizedBox(height: 20),
        _buildDropdownLabel('Water Availability'),
        _buildDropdown(
          value: _selectedWater,
          hint: 'Select Water Level',
          items: ProfileSetupData.waterAvailabilityOptions,
          onChanged: (val) => setState(() => _selectedWater = val),
        ),
        const SizedBox(height: 20),
        KMTextField(
          label: 'Land Area (Acres)',
          hint: 'e.g. 5.5',
          controller: _landController,
          prefixIcon: Icons.landscape_outlined,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          inputFormatters: [
            FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*')),
          ],
          validator: (val) => (_currentStep == 2 && (val == null || val.isEmpty)) ? 'Area is required' : null,
        ),
      ],
    );
  }

  Widget _buildReviewStep() {
    return Column(
      key: const ValueKey('review'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionTitle('Review Your Fields'),
        const SizedBox(height: 12),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _farms.length,
          itemBuilder: (context, index) {
            final farm = _farms[index];
            return Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.05),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Theme.of(context).cardColor.withValues(alpha: 0.1),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(Icons.landscape_rounded, color: Theme.of(context).colorScheme.onSurface, size: 24),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          farm.name,
                          style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700),
                        ),
                        Text(
                          '${farm.landArea} Acres • ${farm.soilType}',
                          style: GoogleFonts.poppins(fontSize: 13, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                        ),
                        Text(
                          '${farm.village}, ${farm.district}',
                          style: GoogleFonts.poppins(fontSize: 12, color: AppColors.textHint),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.edit_note_rounded, color: Theme.of(context).colorScheme.onSurface),
                    onPressed: () {
                      setState(() {
                        _currentStep = 2;
                        _currentFieldAdding = index + 1;
                        // Populate controllers for editing
                        _fieldNameController.text = farm.name;
                        _landController.text = farm.landArea.toString();
                        _villageController.text = farm.village;
                        _selectedState = farm.state;
                        _selectedDistrict = farm.district;
                        _selectedSoil = farm.soilType;
                        _selectedWater = farm.waterAvailability;
                        _farms.removeAt(index);
                      });
                    },
                  ),
                ],
              ),
            );
          },
        ),
        const SizedBox(height: 24),
        KMButton(
          label: 'Add More Fields',
          onPressed: () {
            setState(() {
              _totalFieldsTarget++;
              _currentFieldAdding = _farms.length + 1;
              _currentStep = 2;
              _fieldNameController.clear();
              _landController.clear();
              _villageController.clear();
              _selectedState = null;
              _selectedDistrict = null;
              _selectedSoil = null;
              _selectedWater = null;
            });
          },
          variant: KMButtonVariant.outline,
        ),
      ],
    );
  }

  Widget _buildAppBar() {
    return SliverAppBar(
      expandedHeight: 0,
      floating: true,
      
      elevation: 0,
      leading: context.canPop() 
          ? IconButton(
              icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white, size: 20),
              onPressed: () => context.pop(),
            )
          : null,
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          _currentStep == 0 ? 'Farmer Profile' : 'Manage Fields',
          style: GoogleFonts.poppins(
            fontSize: 32,
            fontWeight: FontWeight.w700,
            color: Theme.of(context).colorScheme.onSurface,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          _currentStep == 0 
              ? 'Tell us about yourself to get started.' 
              : 'Add each of your fields, even if they are in different locations.',
          style: GoogleFonts.poppins(
            fontSize: 15,
            color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
          ),
        ),
      ],
    );
  }

  Widget _buildDropdownLabel(String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        label,
        style: GoogleFonts.poppins(
          fontSize: 13,
          fontWeight: FontWeight.w600,
          color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
        ),
      ),
    );
  }

  Widget _buildDropdown({
    required String? value,
    required String hint,
    required List<String> items,
    required ValueChanged<String?> onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: AppDimensions.paddingMD),
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(AppDimensions.textFieldRadius),
        border: Border.all(color: AppColors.divider, width: 1),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: value,
          hint: Text(hint, style: GoogleFonts.poppins(fontSize: 14, color: AppColors.textHint)),
          isExpanded: true,
          icon: Icon(Icons.keyboard_arrow_down_rounded, color: Theme.of(context).colorScheme.onSurface),
          borderRadius: BorderRadius.circular(AppDimensions.radiusMD),
          items: items.map((String item) {
            return DropdownMenuItem<String>(
              value: item,
              child: Text(item, style: GoogleFonts.poppins(fontSize: 15, color: Theme.of(context).colorScheme.onSurface)),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: GoogleFonts.poppins(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: Theme.of(context).colorScheme.onSurface,
      ),
    );
  }

}
