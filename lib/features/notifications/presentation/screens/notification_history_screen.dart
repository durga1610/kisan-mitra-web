import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:intl/intl.dart';
import 'package:kisan_mitra/core/constants/app_colors.dart';
import 'package:kisan_mitra/core/constants/app_dimensions.dart';
import 'package:kisan_mitra/features/notifications/data/models/notification_model.dart';
import 'package:kisan_mitra/features/notifications/data/models/km_notification_type.dart';
import 'package:kisan_mitra/features/notifications/data/services/notification_service.dart';

class NotificationHistoryScreen extends StatefulWidget {
  const NotificationHistoryScreen({super.key});

  @override
  State<NotificationHistoryScreen> createState() => _NotificationHistoryScreenState();
}

class _NotificationHistoryScreenState extends State<NotificationHistoryScreen> {
  List<NotificationModel> _notifications = [];
  late StreamSubscription _sub;

  @override
  void initState() {
    super.initState();
    _notifications = NotificationService().history;
    _sub = NotificationService().notificationsStream.listen((_) {
      if (mounted) {
        setState(() {
          _notifications = NotificationService().history;
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
    return Scaffold(
      
      appBar: AppBar(
        title: Text(
          'Notifications',
          style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18),
        ),
        
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.done_all_rounded, color: Colors.white),
            onPressed: () {
              NotificationService().markAllAsRead();
              setState(() {
                _notifications = NotificationService().history;
              });
            },
          ),
        ],
      ),
      body: _notifications.isEmpty
          ? _buildEmptyState()
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _notifications.length,
              itemBuilder: (context, index) {
                return _buildNotificationCard(_notifications[index]);
              },
            ),
    );
  }

  Widget _buildNotificationCard(NotificationModel notification) {
    final color = _getTypeColor(notification.type);
    final icon = _getTypeIcon(notification.type);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
        border: notification.isRead ? null : Border.all(color: color.withValues(alpha: 0.2), width: 1.5),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () {
            NotificationService().markAsRead(notification.id);
            setState(() {
              _notifications = NotificationService().history;
            });
          },
          borderRadius: BorderRadius.circular(20),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(icon, color: color, size: 22),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildPriorityBadge(notification.priority),
                          Text(
                            _formatTimestamp(notification.timestamp),
                            style: GoogleFonts.poppins(fontSize: 11, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        notification.title,
                        style: GoogleFonts.poppins(
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        notification.body,
                        style: GoogleFonts.poppins(
                          fontSize: 13,
                          color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                          height: 1.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    ).animate().fadeIn(duration: 400.ms).slideX(begin: 0.05, end: 0);
  }

  Widget _buildPriorityBadge(String priority) {
    Color color;
    switch (priority.toLowerCase()) {
      case 'high': color = AppColors.error; break;
      case 'medium': color = AppColors.secondary; break;
      default: color = AppColors.success;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        priority.toUpperCase(),
        style: GoogleFonts.poppins(
          fontSize: 9,
          fontWeight: FontWeight.w700,
          color: color,
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  Color _getTypeColor(KmNotificationType type) {
    if (type == KmNotificationType.rain) return AppColors.sky;
    if (type == KmNotificationType.disease) return AppColors.error;
    if (type == KmNotificationType.irrigation) return AppColors.primary;
    if (type == KmNotificationType.market) return Colors.orange;
    return Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7);
  }

  IconData _getTypeIcon(KmNotificationType type) {
    if (type == KmNotificationType.rain) return Icons.umbrella_rounded;
    if (type == KmNotificationType.disease) return Icons.bug_report_rounded;
    if (type == KmNotificationType.irrigation) return Icons.water_drop_rounded;
    if (type == KmNotificationType.market) return Icons.trending_up_rounded;
    return Icons.notifications_rounded;
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else {
      return DateFormat('dd MMM').format(timestamp);
    }
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.notifications_none_rounded, size: 64, color: AppColors.textHint),
          const SizedBox(height: 16),
          Text(
            'All caught up!',
            style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.w700),
          ),
          Text(
            'No new alerts for your farm.',
            style: GoogleFonts.poppins(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
          ),
        ],
      ),
    );
  }
}
