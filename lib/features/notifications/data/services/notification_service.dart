import 'dart:async';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:kisan_mitra/features/notifications/data/models/notification_model.dart';
import 'package:kisan_mitra/features/notifications/data/models/km_notification_type.dart';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FirebaseMessaging _fcm = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();
  
  final List<NotificationModel> _history = [];
  List<NotificationModel> get history => _history;
  final _notificationsController = StreamController<NotificationModel>.broadcast();
  Stream<NotificationModel> get notificationsStream => _notificationsController.stream;

  Future<void> init() async {
    // 1. Request Permissions
    await _fcm.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    // 2. Initialize Local Notifications
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings();
    final initSettings = const InitializationSettings(android: androidSettings, iOS: iosSettings);
    
    await _localNotifications.initialize(
      settings: initSettings,
      onDidReceiveNotificationResponse: (NotificationResponse details) {
        // Handle notification tap
      },
    );

    // 3. Handle Foreground Messages
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      _handleRemoteMessage(message);
    });

    // 4. Handle Background/Terminated Messages
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      // Navigate to specific screen based on data
    });
  }

  void _handleRemoteMessage(RemoteMessage message) {
    final notification = message.notification;
    if (notification == null) return;

    // Show local notification for foreground
    if (!kIsWeb) {
      _showLocalNotification(
        id: notification.hashCode,
        title: notification.title ?? 'Kisan Mitra Alert',
        body: notification.body ?? '',
      );
    }

    // Add to stream for UI updates
    final model = NotificationModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: notification.title ?? '',
      body: notification.body ?? '',
      type: _parseType(message.data['type']),
      timestamp: DateTime.now(),
      priority: message.data['priority'] ?? 'Medium',
    );
    
    _history.insert(0, model);
    _notificationsController.add(model);
  }

  Future<void> _showLocalNotification({
    required int id,
    required String title,
    required String body,
  }) async {
    const androidDetails = AndroidNotificationDetails(
      'kisan_mitra_alerts',
      'Farming Alerts',
      channelDescription: 'Important alerts for irrigation, weather, and diseases',
      importance: Importance.max,
      priority: Priority.high,
      color: Color(0xFF2E7D32),
    );
    const notificationDetails = NotificationDetails(android: androidDetails);
    
    await _localNotifications.show(
      id: id,
      title: title,
      body: body,
      notificationDetails: notificationDetails,
    );
  }

  // Helper method to trigger custom local notifications from the app
  Future<void> triggerCustomNotification({
    required String title,
    required String body,
    required KmNotificationType type,
    String priority = 'Medium',
  }) async {
    final id = DateTime.now().millisecondsSinceEpoch.remainder(100000);
    
    // Add to stream for UI history
    final model = NotificationModel(
      id: id.toString(),
      title: title,
      body: body,
      type: type,
      timestamp: DateTime.now(),
      priority: priority,
    );
    _history.insert(0, model);
    _notificationsController.add(model);

    // Show system notification
    if (!kIsWeb) {
      await _showLocalNotification(id: id, title: title, body: body);
    }
  }

  KmNotificationType _parseType(String? type) {
    switch (type) {
      case 'rain': return KmNotificationType.rain;
      case 'disease': return KmNotificationType.disease;
      case 'irrigation': return KmNotificationType.irrigation;
      case 'market': return KmNotificationType.market;
      default: return KmNotificationType.system;
    }
  }

  // Mock data for history
  void markAsRead(String id) {
    _history.removeWhere((n) => n.id == id);
    if (_history.isNotEmpty) {
      _notificationsController.add(_history.first);
    } else {
      _notificationsController.add(NotificationModel(id: '', title: '', body: '', type: KmNotificationType.system, timestamp: DateTime.now(), isRead: true));
    }
  }

  void markAllAsRead() {
    _history.clear();
    _notificationsController.add(NotificationModel(id: '', title: '', body: '', type: KmNotificationType.system, timestamp: DateTime.now(), isRead: true));
  }

  List<NotificationModel> getHistory() {
    return _history;
  }
}
