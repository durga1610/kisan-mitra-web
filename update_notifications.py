import os
import re

# 1. Update NotificationService
notification_service_path = 'lib/features/notifications/data/services/notification_service.dart'
with open(notification_service_path, 'r', encoding='utf-8') as f:
    ns_content = f.read()

# Replace getMockHistory with a persistent approach using SharedPreferences
# Wait, actually since this is a quick fix, let's just make a static memory list. 
# "when there is drastic change in weather and market price of the planted crop"
# If I use SharedPreferences, I need to add toJson/fromJson to NotificationModel.
# Let's just keep it in memory for now but populate it from weather & market!
# Let's make an internal list `final List<NotificationModel> _history = [];`

new_ns = ns_content.replace(
    '  final _notificationsController = StreamController<NotificationModel>.broadcast();',
    '  final List<NotificationModel> _history = [];\n  List<NotificationModel> get history => _history;\n  final _notificationsController = StreamController<NotificationModel>.broadcast();'
)

# update `_notificationsController.add(model);` to also add to `_history`
new_ns = new_ns.replace(
    '    _notificationsController.add(model);',
    '    _history.insert(0, model);\n    _notificationsController.add(model);'
)

# Replace getMockHistory
new_ns = re.sub(
    r'  List<NotificationModel> getMockHistory\(\) \{.*?\n  \}',
    '''  List<NotificationModel> getHistory() {
    return _history;
  }''',
    new_ns,
    flags=re.DOTALL
)

with open(notification_service_path, 'w', encoding='utf-8') as f:
    f.write(new_ns)

# 2. Update NotificationHistoryScreen
history_screen_path = 'lib/features/notifications/presentation/screens/notification_history_screen.dart'
with open(history_screen_path, 'r', encoding='utf-8') as f:
    hs_content = f.read()

new_hs = hs_content.replace(
    '  final List<NotificationModel> _notifications = NotificationService().getMockHistory();',
    '''  List<NotificationModel> _notifications = [];
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
'''
)
# Also add import for StreamSubscription if needed. (import 'dart:async';)
if 'dart:async' not in new_hs:
    new_hs = "import 'dart:async';\n" + new_hs

with open(history_screen_path, 'w', encoding='utf-8') as f:
    f.write(new_hs)

# 3. Update WeatherService to trigger notification on drastic weather
weather_service_path = 'lib/core/services/weather_service.dart'
with open(weather_service_path, 'r', encoding='utf-8') as f:
    ws_content = f.read()

if 'NotificationService' not in ws_content:
    imports = "import '../../features/notifications/data/services/notification_service.dart';\nimport '../../features/notifications/data/models/km_notification_type.dart';\n"
    ws_content = imports + ws_content

# In getWeather, after parsing weather:
weather_notification_logic = '''
        // Trigger notification if weather is bad
        final condition = weather.condition.toLowerCase();
        if (condition.contains('rain') || condition.contains('storm') || condition.contains('thunder')) {
          // simple deduplication (only notify once per session for the same weather)
          final history = NotificationService().history;
          final alreadyNotified = history.any((n) => n.type == KmNotificationType.rain && DateTime.now().difference(n.timestamp).inHours < 4);
          if (!alreadyNotified) {
             NotificationService().triggerCustomNotification(
               title: 'Weather Alert',
               body: 'Drastic weather change detected: ${weather.condition}. Please take precautions for your crops.',
               type: KmNotificationType.rain,
               priority: 'High'
             );
          }
        }
'''

ws_content = ws_content.replace(
    '        return weather;',
    weather_notification_logic + '        return weather;'
)

with open(weather_service_path, 'w', encoding='utf-8') as f:
    f.write(ws_content)

print("Updated notification files and weather service successfully!")
