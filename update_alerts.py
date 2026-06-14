import os
import re

# 1. Update AlertsCard
alerts_card_path = 'lib/features/home/presentation/widgets/alerts_card.dart'
with open(alerts_card_path, 'r', encoding='utf-8') as f:
    ac_content = f.read()

# We need to change AlertsCard from StatelessWidget to StatefulWidget
# and subscribe to NotificationService.

new_ac_content = """import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/localization/app_translations.dart';
import '../../../../features/notifications/data/services/notification_service.dart';
import '../../../../features/notifications/data/models/notification_model.dart';
import '../../../../features/notifications/data/models/km_notification_type.dart';

class AlertsCard extends StatefulWidget {
  const AlertsCard({super.key});

  @override
  State<AlertsCard> createState() => _AlertsCardState();
}

class _AlertsCardState extends State<AlertsCard> {
  List<NotificationModel> _alerts = [];
  late StreamSubscription _sub;

  @override
  void initState() {
    super.initState();
    _alerts = NotificationService().history;
    _sub = NotificationService().notificationsStream.listen((_) {
      if (mounted) {
        setState(() {
          _alerts = NotificationService().history;
        });
      }
    });
  }

  @override
  void dispose() {
    _sub.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_alerts.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 20),
          child: Text(
            "No active alerts".tr(context),
            style: GoogleFonts.poppins(color: AppColors.textHint),
          ),
        ),
      );
    }
    
    // Show only the 3 most recent
    final displayAlerts = _alerts.take(3).toList();

    return Column(
      children: displayAlerts
          .map(
            (alert) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: _AlertTile(alert: alert),
            ),
          )
          .toList(),
    );
  }
}

class _AlertTile extends StatelessWidget {
  final NotificationModel alert;
  const _AlertTile({required this.alert});

  Color _getBgColor(KmNotificationType type) {
    if (type == KmNotificationType.rain) return AppColors.skyContainer;
    if (type == KmNotificationType.disease) return const Color(0xFFFFEBEE);
    if (type == KmNotificationType.market) return const Color(0xFFFFF3E0);
    if (type == KmNotificationType.irrigation) return const Color(0xFFE3F2FD);
    return const Color(0xFFFFF8E1);
  }
  
  Color _getColor(KmNotificationType type) {
    if (type == KmNotificationType.rain) return AppColors.sky;
    if (type == KmNotificationType.disease) return AppColors.error;
    if (type == KmNotificationType.market) return Colors.orange;
    if (type == KmNotificationType.irrigation) return AppColors.primary;
    return AppColors.warning;
  }

  IconData _getIcon(KmNotificationType type) {
    if (type == KmNotificationType.rain) return Icons.water_drop_outlined;
    if (type == KmNotificationType.disease) return Icons.bug_report_outlined;
    if (type == KmNotificationType.market) return Icons.trending_up_rounded;
    if (type == KmNotificationType.irrigation) return Icons.opacity_rounded;
    return Icons.notifications_active_outlined;
  }

  String _formatTime(DateTime time) {
    final diff = DateTime.now().difference(time);
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: _getBgColor(alert.type),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(_getIcon(alert.type), color: _getColor(alert.type), size: 22),
        ),
        title: Text(
          alert.title.tr(context),
          style: GoogleFonts.poppins(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: Theme.of(context).colorScheme.onSurface,
          ),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 2),
          child: Text(
            alert.body.tr(context),
            style: GoogleFonts.poppins(
              fontSize: 11,
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ),
        trailing: Text(
          _formatTime(alert.timestamp).tr(context),
          style: GoogleFonts.poppins(
            fontSize: 10,
            color: AppColors.textHint,
          ),
        ),
      ),
    );
  }
}
"""

with open(alerts_card_path, 'w', encoding='utf-8') as f:
    f.write(new_ac_content)


# 2. Add daily schedule notification trigger in home_screen.dart
home_screen_path = 'lib/features/home/presentation/screens/home_screen.dart'
with open(home_screen_path, 'r', encoding='utf-8') as f:
    hs_content = f.read()

# Add a function to check daily schedule
daily_schedule_func = """
  void _checkDailySchedule(FarmProvider farmProvider) {
    if (farmProvider.plantedCrops.isNotEmpty) {
      final history = NotificationService().history;
      final alreadyNotified = history.any((n) => n.type == KmNotificationType.system && n.title == 'Daily Schedule' && DateTime.now().difference(n.timestamp).inHours < 24);
      
      if (!alreadyNotified) {
        final crop = farmProvider.plantedCrops.first;
        NotificationService().triggerCustomNotification(
          title: 'Daily Schedule',
          body: 'You have scheduled tasks for your ${crop.cropName} crop today. Check the AI Assistant tab for details.',
          type: KmNotificationType.system,
          priority: 'Medium'
        );
      }
    }
  }
"""

# inject this inside _HomeScreenState
hs_content = hs_content.replace('  void _startAutoRefresh() {', daily_schedule_func + '\n  void _startAutoRefresh() {')

# Call _checkDailySchedule inside _loadInitialData after crops are loaded
# wait, _loadInitialData looks like:
#     await farmProvider.loadFarms();
#     if (farmProvider.farms.isNotEmpty && farmProvider.selectedFarm == null) {
#       farmProvider.selectFarmIndex(0);
#     }
#     if (mounted) {
#       setState(() => _isLoading = false);
#     }
replace_target = """    if (mounted) {
      setState(() => _isLoading = false);
    }"""
    
replace_with = """    _checkDailySchedule(farmProvider);
    if (mounted) {
      setState(() => _isLoading = false);
    }"""

hs_content = hs_content.replace(replace_target, replace_with)

with open(home_screen_path, 'w', encoding='utf-8') as f:
    f.write(hs_content)

print("Updated alerts_card.dart and home_screen.dart successfully!")
