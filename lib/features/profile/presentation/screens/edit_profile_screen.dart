import 'dart:io';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:image_picker/image_picker.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import 'package:provider/provider.dart';
import '../../../../core/models/user_model.dart';
import '../../../../core/providers/user_provider.dart';
import '../../../../core/models/farm_model.dart';
import '../../../../core/widgets/km_text_field.dart';
import '../../../../core/widgets/km_button.dart';

class EditProfileScreen extends StatefulWidget {
  final UserModel user;
  final FarmModel? farm; // Kept for backwards compatibility if called elsewhere, but ignored

  const EditProfileScreen({super.key, required this.user, this.farm});

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _picker = ImagePicker();
  
  late TextEditingController _nameController;
  late TextEditingController _phoneController;
  late TextEditingController _emailController;
  late TextEditingController _locationController;
  
  XFile? _imageFile;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.user.name);
    _phoneController = TextEditingController(text: widget.user.phone);
    _emailController = TextEditingController(text: widget.user.email ?? '');
    _locationController = TextEditingController(text: widget.user.location ?? '');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _locationController.dispose();
    super.dispose();
  }

  Future<void> _pickImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery, imageQuality: 70);
    if (image != null) {
      setState(() => _imageFile = image);
    }
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);
    try {
      final uid = widget.user.uid;
      String? imageUrl = widget.user.profileImageUrl;

      // 1. Upload Image if changed
      if (_imageFile != null) {
        final storageRef = FirebaseStorage.instance.ref().child('profile_images/$uid.jpg');
        if (kIsWeb) {
          final bytes = await _imageFile!.readAsBytes();
          await storageRef.putData(bytes, SettableMetadata(contentType: 'image/jpeg'));
        } else {
          await storageRef.putFile(File(_imageFile!.path));
        }
        imageUrl = await storageRef.getDownloadURL();
      }

      await FirebaseFirestore.instance.collection('users').doc(uid).set({
        'name': _nameController.text.trim(),
        'phone': _phoneController.text.trim(),
        'email': _emailController.text.trim(),
        'location': _locationController.text.trim(),
        'profileImageUrl': imageUrl,
        'updatedAt': DateTime.now().toIso8601String(),
      }, SetOptions(merge: true));

      if (mounted) {
        final updatedUser = UserModel(
          uid: widget.user.uid,
          name: _nameController.text.trim(),
          phone: _phoneController.text.trim(),
          email: _emailController.text.trim(),
          location: _locationController.text.trim(),
          setupCompleted: widget.user.setupCompleted,
          profileImageUrl: imageUrl,
          updatedAt: DateTime.now(),
        );
        Provider.of<UserProvider>(context, listen: false).updateUserProfile(updatedUser);

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Profile updated successfully!'.tr(context)), backgroundColor: AppColors.success),
        );
        Navigator.pop(context, true);
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
    return Scaffold(
      
      appBar: AppBar(
        title: Text('Edit Profile'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w600)),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppDimensions.paddingLG),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildImagePicker(),
              const SizedBox(height: 32),
              _buildSectionTitle('Personal Information'),
              const SizedBox(height: 16),
              KMTextField(
                controller: _nameController,
                label: 'Full Name',
                hint: 'Enter your name',
                prefixIcon: Icons.person_outline_rounded,
                validator: (v) => v == null || v.isEmpty ? 'Name is required' : null,
              ),
              const SizedBox(height: 16),
              KMTextField(
                controller: _emailController,
                label: 'Email Address',
                hint: 'Enter your email',
                prefixIcon: Icons.email_outlined,
                keyboardType: TextInputType.emailAddress,
                validator: (v) {
                  if (v != null && v.isNotEmpty && !v.contains('@')) {
                    return 'Valid email address required';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              KMTextField(
                controller: _phoneController,
                label: 'Phone Number',
                hint: '10-digit mobile number',
                prefixIcon: Icons.phone_outlined,
                keyboardType: TextInputType.phone,
                validator: (v) => v == null || v.length != 10 ? 'Valid 10-digit phone number required' : null,
              ),
              const SizedBox(height: 16),
              KMTextField(
                controller: _locationController,
                label: 'Location',
                hint: 'City, State',
                prefixIcon: Icons.location_on_outlined,
                validator: (v) => v == null || v.isEmpty ? 'Location is required' : null,
              ),
              const SizedBox(height: 40),
              KMButton(
                label: 'Save Changes',
                onPressed: _saveProfile,
                isLoading: _isLoading,
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImagePicker() {
    return Center(
      child: Stack(
        children: [
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 10, offset: const Offset(0, 4)),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(60),
              child: _imageFile != null
                  ? (kIsWeb ? Image.network(_imageFile!.path, fit: BoxFit.cover) : Image.file(File(_imageFile!.path), fit: BoxFit.cover))
                  : (widget.user.profileImageUrl != null
                      ? Image.network(widget.user.profileImageUrl!, fit: BoxFit.cover)
                      : const Icon(Icons.person_rounded, size: 60, color: AppColors.textHint)),
            ),
          ),
          Positioned(
            bottom: 0,
            right: 0,
            child: GestureDetector(
              onTap: _pickImage,
              child: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(color: Theme.of(context).cardColor, shape: BoxShape.circle),
                child: const Icon(Icons.camera_alt_rounded, color: AppColors.primary, size: 20),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface),
    );
  }
}
