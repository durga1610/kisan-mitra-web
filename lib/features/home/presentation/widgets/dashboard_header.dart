import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/localization/app_translations.dart';

class DashboardHeader extends StatelessWidget {
  final String greeting;
  final String farmerName;
  final String date;
  final String farmArea;
  final String location;
  final String fieldName;
  final List<String> allFarmNames;
  final int selectedFarmIndex;
  final Function(int) onFarmSelected;
  final VoidCallback onLogoutTap;
  final String? profileImageUrl;

  const DashboardHeader({
    super.key,
    required this.greeting,
    required this.farmerName,
    required this.date,
    required this.farmArea,
    required this.location,
    required this.fieldName,
    required this.allFarmNames,
    required this.selectedFarmIndex,
    required this.onFarmSelected,
    required this.onLogoutTap,
    this.profileImageUrl,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: AppColors.primaryGradient,
        borderRadius: BorderRadius.vertical(bottom: Radius.circular(28)),
      ),
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 28),
      child: SafeArea(
        bottom: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top row
            Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Avatar
                Container(
                  width: 46,
                  height: 46,
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardColor.withValues(alpha: 0.2),
                    shape: BoxShape.circle,
                    border: Border.all(
                        color: Colors.white.withValues(alpha: 0.5), width: 2),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(23),
                    child: profileImageUrl != null && profileImageUrl!.isNotEmpty
                        ? Image.network(profileImageUrl!, fit: BoxFit.cover)
                        : const Icon(Icons.person_rounded,
                            color: Colors.white, size: 24),
                  ),
                ),
                const SizedBox(width: 12),

                // Greeting & Name
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        greeting,
                        style: GoogleFonts.poppins(
                          fontSize: 13,
                          color: Colors.white.withValues(alpha: 0.85),
                          fontWeight: FontWeight.w400,
                        ),
                      ),
                      Row(
                        children: [
                          Flexible(
                            child: Text(
                              farmerName,
                              style: GoogleFonts.poppins(
                                fontSize: 18,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          if (allFarmNames.isNotEmpty) ...[
                            const SizedBox(width: 8),
                            _buildFieldSelector(context),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),

                // Logout
                GestureDetector(
                  onTap: onLogoutTap,
                  child: Container(
                    width: 42,
                    height: 42,
                    decoration: BoxDecoration(
                      color: Theme.of(context).cardColor.withValues(alpha: 0.15),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.logout_rounded,
                      color: Colors.white,
                      size: 20,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),

            // Date & Farm info
            Row(
              children: [
                Icon(Icons.calendar_today_rounded,
                    size: 13, color: Colors.white.withValues(alpha: 0.7)),
                const SizedBox(width: 6),
                Text(
                  date,
                  style: GoogleFonts.poppins(
                    fontSize: 12,
                    color: Colors.white.withValues(alpha: 0.75),
                  ),
                ),
                Icon(Icons.location_on_rounded,
                    size: 13, color: Colors.white.withValues(alpha: 0.8)),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    (location == null || location.isEmpty || location == ', ') ? 'Unknown Location' : location,
                    style: GoogleFonts.poppins(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: Colors.white,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 12),
                Container(
                  width: 1,
                  height: 12,
                  color: Colors.white.withValues(alpha: 0.3),
                ),
                const SizedBox(width: 12),
                Icon(Icons.landscape_rounded,
                    size: 13, color: Colors.white.withValues(alpha: 0.8)),
                const SizedBox(width: 4),
                Text(
                  '$farmArea ${'Acres'.tr(context)}',
                  style: GoogleFonts.poppins(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  Widget _buildFieldSelector(BuildContext context) {
    return GestureDetector(
      onTap: () => _showFieldPicker(context),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor.withValues(alpha: 0.2),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white.withValues(alpha: 0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.swap_horiz_rounded, color: Colors.white, size: 14),
            const SizedBox(width: 4),
            Text(
              'Switch'.tr(context),
              style: GoogleFonts.poppins(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showFieldPicker(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Row(
                    children: [
                      const Icon(Icons.landscape_rounded, color: AppColors.primary),
                      const SizedBox(width: 12),
                      Text(
                        'Select Field'.tr(context),
                        style: GoogleFonts.poppins(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: Theme.of(context).colorScheme.onSurface,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                Flexible(
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: allFarmNames.length + 1,
                    itemBuilder: (context, index) {
                      if (index == allFarmNames.length) {
                        // Add New Farm Button
                        return ListTile(
                          onTap: () {
                            Navigator.pop(context);
                            context.go('/profile-setup');
                          },
                          leading: Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: AppColors.primary.withValues(alpha: 0.1),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(
                              Icons.add_location_alt_rounded, 
                              color: AppColors.primary,
                              size: 20,
                            ),
                          ),
                          title: Text(
                            'Add New Field'.tr(context),
                            style: GoogleFonts.poppins(
                              fontWeight: FontWeight.w600,
                              color: AppColors.primary,
                            ),
                          ),
                        );
                      }

                      final isSelected = selectedFarmIndex == index;
                      return ListTile(
                        onTap: () {
                          onFarmSelected(index);
                          Navigator.pop(context);
                        },
                        leading: Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: isSelected 
                                ? AppColors.primary.withValues(alpha: 0.1)
                                : AppColors.background,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            Icons.park_rounded, 
                            color: isSelected ? AppColors.primary : AppColors.textHint,
                            size: 20,
                          ),
                        ),
                        title: Text(
                          allFarmNames[index],
                          style: GoogleFonts.poppins(
                            fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                            color: isSelected ? AppColors.primary : Theme.of(context).colorScheme.onSurface,
                          ),
                        ),
                        trailing: isSelected 
                            ? const Icon(Icons.check_circle_rounded, color: AppColors.primary)
                            : null,
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
