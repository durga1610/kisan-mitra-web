import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/localization/app_translations.dart';

class _CropItem {
  final String name;
  final double health;
  final String status;
  final Color statusColor;
  final IconData icon;

  const _CropItem({
    required this.name,
    required this.health,
    required this.status,
    required this.statusColor,
    required this.icon,
  });
}

class CropHealthCard extends StatelessWidget {
  const CropHealthCard({super.key});

  static const _crops = [
    _CropItem(
      name: 'Wheat',
      health: 0.85,
      status: 'Healthy',
      statusColor: AppColors.success,
      icon: Icons.grass_rounded,
    ),
    _CropItem(
      name: 'Tomato',
      health: 0.62,
      status: 'Moderate',
      statusColor: AppColors.warning,
      icon: Icons.spa_rounded,
    ),
    _CropItem(
      name: 'Onion',
      health: 0.91,
      status: 'Excellent',
      statusColor: AppColors.success,
      icon: Icons.eco_rounded,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        children: _crops
            .map((crop) => Padding(
                  padding: const EdgeInsets.only(bottom: 14),
                  child: _CropHealthTile(crop: crop),
                ))
            .toList(),
      ),
    );
  }
}

class _CropHealthTile extends StatelessWidget {
  final _CropItem crop;
  const _CropHealthTile({required this.crop});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: AppColors.primaryContainer,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(crop.icon, color: AppColors.primary, size: 20),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                Text(
                  crop.name.tr(context),
                  style: GoogleFonts.poppins(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Theme.of(context).colorScheme.onSurface,
                  ),
                ),
                Row(
                  children: [
                    Container(
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(
                        color: crop.statusColor,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      crop.status.tr(context),
                      style: GoogleFonts.poppins(
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                        color: crop.statusColor,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 6),
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: crop.health,
                minHeight: 6,
                backgroundColor: AppColors.surfaceVariant,
                valueColor: AlwaysStoppedAnimation<Color>(
                  crop.health > 0.8
                      ? AppColors.success
                      : crop.health > 0.5
                          ? AppColors.warning
                          : AppColors.error,
                ),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              '${(crop.health * 100).toInt()}% ${'health'.tr(context)}',
              style: GoogleFonts.poppins(
                fontSize: 10,
                color: AppColors.textHint,
              ),
            ),
          ],
        ),
        ),
      ],
    );
  }
}
