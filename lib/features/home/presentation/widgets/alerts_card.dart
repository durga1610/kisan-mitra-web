import 'dart:async';
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
