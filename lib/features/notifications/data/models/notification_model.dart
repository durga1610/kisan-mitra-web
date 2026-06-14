import 'km_notification_type.dart';

class NotificationModel {
  final String id;
  final String title;
  final String body;
  final KmNotificationType type;
  final DateTime timestamp;
  final bool isRead;
  final String? deepLink;
  final String priority; // 'High', 'Medium', 'Low'

  NotificationModel({
    required this.id,
    required this.title,
    required this.body,
    required this.type,
    required this.timestamp,
    this.isRead = false,
    this.deepLink,
    this.priority = 'Medium',
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'body': body,
      'type': type.name,
      'timestamp': timestamp.toIso8601String(),
      'isRead': isRead,
      'deepLink': deepLink,
      'priority': priority,
    };
  }

  factory NotificationModel.fromMap(Map<String, dynamic> map) {
    return NotificationModel(
      id: map['id'] ?? '',
      title: map['title'] ?? '',
      body: map['body'] ?? '',
      type: KmNotificationType.values.firstWhere(
        (e) => e.name == map['type'],
        orElse: () => KmNotificationType.system,
      ),
      timestamp: DateTime.parse(map['timestamp'] ?? DateTime.now().toIso8601String()),
      isRead: map['isRead'] ?? false,
      deepLink: map['deepLink'],
      priority: map['priority'] ?? 'Medium',
    );
  }
}
