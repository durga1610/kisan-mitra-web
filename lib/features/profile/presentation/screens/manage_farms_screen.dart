import 'package:flutter/material.dart';
import 'package:kisan_mitra/core/localization/app_translations.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:provider/provider.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/models/farm_model.dart';
import 'edit_farm_screen.dart';

class ManageFarmsScreen extends StatelessWidget {
  const ManageFarmsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = Provider.of<AuthProvider>(context).user;

    if (user == null) {
      return Scaffold(
        body: Center(child: Text('Please log in'.tr(context))),
      );
    }

    return Scaffold(
      
      appBar: AppBar(
        title: Text('Manage Fields'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w600)),
        
        elevation: 0,
      ),
      body: StreamBuilder<QuerySnapshot>(
        stream: FirebaseFirestore.instance
            .collection('farms')
            .where('ownerId', isEqualTo: user.uid)
            .snapshots(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator(color: Colors.white));
          }

          if (snapshot.hasError) {
            return Center(child: Text('Error loading fields'.tr(context), style: GoogleFonts.poppins()));
          }

          final docs = snapshot.data?.docs ?? [];

          if (docs.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.landscape_rounded, size: 64, color: AppColors.textHint.withValues(alpha: 0.5)),
                  const SizedBox(height: 16),
                  Text('No fields added yet.'.tr(context), style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: docs.length,
            itemBuilder: (context, index) {
              final doc = docs[index];
              final farm = FarmModel.fromMap(doc.data() as Map<String, dynamic>, docId: doc.id);

              return _buildFarmCard(context, farm);
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.primary,
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const EditFarmScreen(),
            ),
          );
        },
        icon: const Icon(Icons.add_rounded, color: Colors.white),
        label: Text('Add Field'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: Colors.white)),
      ),
    );
  }

  Widget _buildFarmCard(BuildContext context, FarmModel farm) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withValues(alpha: 0.1),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.landscape_rounded, color: AppColors.primary, size: 24),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            farm.name.isNotEmpty ? farm.name : 'Unnamed Field',
                            style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          Text(
                            '${farm.village}, ${farm.district}',
                            style: GoogleFonts.poppins(fontSize: 13, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              PopupMenuButton<String>(
                icon: Icon(Icons.more_vert_rounded, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                onSelected: (value) {
                  if (value == 'edit') {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => EditFarmScreen(farm: farm),
                      ),
                    );
                  } else if (value == 'delete') {
                    _showDeleteConfirmation(context, farm);
                  }
                },
                itemBuilder: (context) => [
                  PopupMenuItem(
                    value: 'edit',
                    child: Row(
                      children: [
                        Icon(Icons.edit_rounded, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7), size: 20),
                        const SizedBox(width: 8),
                        Text('Edit'.tr(context), style: GoogleFonts.poppins()),
                      ],
                    ),
                  ),
                  PopupMenuItem(
                    value: 'delete',
                    child: Row(
                      children: [
                        const Icon(Icons.delete_rounded, color: AppColors.error, size: 20),
                        const SizedBox(width: 8),
                        Text('Delete'.tr(context), style: GoogleFonts.poppins(color: AppColors.error)),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 12),
            child: Divider(height: 1),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStat(context, Icons.square_foot_rounded, '${farm.landArea} Acres'),
              _buildStat(context, Icons.layers_rounded, farm.soilType),
              _buildStat(context, Icons.water_drop_rounded, farm.waterAvailability),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStat(BuildContext context, IconData icon, String value) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
        const SizedBox(width: 6),
        Text(
          value,
          style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w500, color: Theme.of(context).colorScheme.onSurface),
        ),
      ],
    );
  }

  void _showDeleteConfirmation(BuildContext context, FarmModel farm) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Delete Field?'.tr(context), style: GoogleFonts.poppins(fontWeight: FontWeight.w600)),
        content: Text('Are you sure you want to delete ${farm.name}? This action cannot be undone.', style: GoogleFonts.poppins()),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'.tr(context), style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              if (farm.id != null) {
                FirebaseFirestore.instance.collection('farms').doc(farm.id).delete();
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Field deleted'.tr(context))),
                );
              }
            },
            child: Text('Delete'.tr(context), style: GoogleFonts.poppins(color: AppColors.error, fontWeight: FontWeight.w600)),
          ),
        ],
      ),
    );
  }
}
