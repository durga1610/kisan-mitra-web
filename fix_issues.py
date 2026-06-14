import os
import re

# 1. Update NotificationModel and NotificationService
model_path = 'lib/features/notifications/data/models/notification_model.dart'
with open(model_path, 'r', encoding='utf-8') as f:
    model_content = f.read()

model_content = model_content.replace('this.isRead = false,', 'this.isRead = false,') # it already has it

service_path = 'lib/features/notifications/data/services/notification_service.dart'
with open(service_path, 'r', encoding='utf-8') as f:
    ns_content = f.read()

if 'void markAsRead' not in ns_content:
    ns_content = ns_content.replace(
        '  List<NotificationModel> getHistory() {',
        '''  void markAsRead(String id) {
    final index = _history.indexWhere((n) => n.id == id);
    if (index != -1) {
      final old = _history[index];
      _history[index] = NotificationModel(
        id: old.id,
        title: old.title,
        body: old.body,
        type: old.type,
        timestamp: old.timestamp,
        priority: old.priority,
        isRead: true,
      );
      _notificationsController.add(_history[index]);
    }
  }

  void markAllAsRead() {
    for (int i = 0; i < _history.length; i++) {
      final old = _history[i];
      _history[i] = NotificationModel(
        id: old.id,
        title: old.title,
        body: old.body,
        type: old.type,
        timestamp: old.timestamp,
        priority: old.priority,
        isRead: true,
      );
    }
    if (_history.isNotEmpty) {
      _notificationsController.add(_history.first);
    }
  }

  List<NotificationModel> getHistory() {'''
    )
    with open(service_path, 'w', encoding='utf-8') as f:
        f.write(ns_content)

# Update NotificationHistoryScreen
screen_path = 'lib/features/notifications/presentation/screens/notification_history_screen.dart'
with open(screen_path, 'r', encoding='utf-8') as f:
    screen_content = f.read()

screen_content = screen_content.replace(
    'onPressed: () {}, // Mark all as read',
    '''onPressed: () {
              NotificationService().markAllAsRead();
              setState(() {
                _notifications = NotificationService().history;
              });
            },'''
)

screen_content = screen_content.replace(
    '          onTap: () {}, // Mark as read and navigate',
    '''          onTap: () {
            NotificationService().markAsRead(notification.id);
            setState(() {
              _notifications = NotificationService().history;
            });
          },'''
)

with open(screen_path, 'w', encoding='utf-8') as f:
    f.write(screen_content)


# 2. Update GeminiService to strictly enforce crop list
gemini_path = 'lib/core/services/gemini_service.dart'
with open(gemini_path, 'r', encoding='utf-8') as f:
    gs_content = f.read()

gs_content = gs_content.replace(
    'Prioritize crops from the trending market list if they match the soil/weather perfectly.',
    'YOU MUST ONLY SUGGEST CROPS THAT EXACTLY MATCH ONE OF THE CROPS IN THE TRENDING MARKET LIST. DO NOT INVENT OR SUGGEST ANY OTHER CROP.'
)

with open(gemini_path, 'w', encoding='utf-8') as f:
    f.write(gs_content)

# 3. Update RecommendationService to use languageCode in cache and save to SharedPreferences (or just use languageCode in memory cache for now, which fixes the changing during session)
rec_path = 'lib/core/services/recommendation_service.dart'
with open(rec_path, 'r', encoding='utf-8') as f:
    rec_content = f.read()

rec_content = rec_content.replace(
    'final cacheKey = farm.id ?? farm.name;',
    "final cacheKey = '${farm.id ?? farm.name}_$languageCode';"
)

with open(rec_path, 'w', encoding='utf-8') as f:
    f.write(rec_content)


# 4 & 5. Update FarmModel and CropsScreen for Land Area
farm_model_path = 'lib/core/models/farm_model.dart'
with open(farm_model_path, 'r', encoding='utf-8') as f:
    fm_content = f.read()

fm_content = fm_content.replace(
    '  final DateTime plantedDate;',
    '  final DateTime plantedDate;\n  final double? landArea;'
)

fm_content = fm_content.replace(
    '    required this.plantedDate,',
    '    required this.plantedDate,\n    this.landArea,'
)

fm_content = fm_content.replace(
    "      'plantedDate': plantedDate.toIso8601String(),",
    "      'plantedDate': plantedDate.toIso8601String(),\n      'landArea': landArea,"
)

fm_content = fm_content.replace(
    "      plantedDate: DateTime.parse(map['plantedDate'] ?? DateTime.now().toIso8601String()),",
    "      plantedDate: DateTime.parse(map['plantedDate'] ?? DateTime.now().toIso8601String()),\n      landArea: (map['landArea'] as num?)?.toDouble(),"
)

with open(farm_model_path, 'w', encoding='utf-8') as f:
    f.write(fm_content)


# CropsScreen
crops_screen_path = 'lib/features/crops/presentation/screens/crops_screen.dart'
with open(crops_screen_path, 'r', encoding='utf-8') as f:
    cs_content = f.read()

cs_content = cs_content.replace(
    'import \'../../../../core/localization/app_translations.dart\';',
    '''import '../../../../core/localization/app_translations.dart';
import '../../../../core/services/firestore_service.dart';
import '../../../../features/profile_setup/presentation/screens/profile_setup_screen.dart';'''
)

add_crop_logic = '''
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ProfileSetupScreen(),
                ),
              );
            },'''

cs_content = cs_content.replace('            onPressed: () {},', add_crop_logic, 1)

# Modify landPerCrop logic to use specific landArea if available
cs_content = cs_content.replace(
    'final landPerCrop = cropsCount > 0 ? totalLand / cropsCount : 0.0; // Distribute evenly for now',
    '// Deprecated'
)

# in _buildCropProgressCard definition:
cs_content = cs_content.replace(
    'Widget _buildCropProgressCard(BuildContext context, PlantedCropModel crop, double landArea) {',
    '''Widget _buildCropProgressCard(BuildContext context, PlantedCropModel crop, double totalLand, int cropsCount, FarmModel farm) {
    final landArea = crop.landArea ?? (cropsCount > 0 ? totalLand / cropsCount : 0.0);
'''
)

# in map
cs_content = cs_content.replace(
    '...farm.plantedCrops.map((crop) => _buildCropProgressCard(context, crop, landPerCrop)),',
    '...farm.plantedCrops.map((crop) => _buildCropProgressCard(context, crop, totalLand, cropsCount, farm)),'
)

# edit button in _buildCropProgressCard
edit_button_logic = '''
              _buildHealthBadge(context, 'Good'.tr(context)),
              IconButton(
                icon: const Icon(Icons.edit, size: 18),
                onPressed: () => _editLandArea(context, crop, farm),
              ),
'''
cs_content = cs_content.replace("              _buildHealthBadge(context, 'Good'.tr(context)),", edit_button_logic)

edit_dialog_logic = '''
  Future<void> _editLandArea(BuildContext context, PlantedCropModel crop, FarmModel farm) async {
    final TextEditingController _controller = TextEditingController(text: crop.landArea?.toString() ?? '');
    
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Edit Land Area'.tr(context)),
        content: TextField(
          controller: _controller,
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            labelText: 'Land Area (Acres)'.tr(context),
            border: const OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'.tr(context)),
          ),
          ElevatedButton(
            onPressed: () async {
              final val = double.tryParse(_controller.text);
              if (val != null && val > 0 && farm.id != null) {
                // Update in Firestore
                final index = farm.plantedCrops.indexOf(crop);
                if (index != -1) {
                  final newCrops = List<PlantedCropModel>.from(farm.plantedCrops);
                  newCrops[index] = PlantedCropModel(
                    cropName: crop.cropName,
                    plantedDate: crop.plantedDate,
                    landArea: val,
                  );
                  await FirestoreService().updateFarm(farm.id!, {'plantedCrops': newCrops.map((c) => c.toMap()).toList()});
                }
              }
              if (context.mounted) Navigator.pop(context);
            },
            child: Text('Save'.tr(context)),
          ),
        ],
      ),
    );
  }
}
'''
cs_content = cs_content.replace('\n}\n', '\n' + edit_dialog_logic, 1)

# Fix _buildLandDistributionChart
cs_content = cs_content.replace(
    'Widget _buildLandDistributionChart(BuildContext context, FarmModel farm, double landPerCrop) {',
    'Widget _buildLandDistributionChart(BuildContext context, FarmModel farm) {'
)

cs_content = cs_content.replace(
    '              _buildLandDistributionChart(context, farm, landPerCrop),',
    '              _buildLandDistributionChart(context, farm),'
)

cs_content = cs_content.replace(
    '            final percentage = farm.landArea > 0 ? landPerCrop / farm.landArea : 0.0;',
    '''            final landArea = crop.landArea ?? (farm.plantedCrops.isNotEmpty ? farm.landArea / farm.plantedCrops.length : 0.0);
            final percentage = farm.landArea > 0 ? landArea / farm.landArea : 0.0;'''
)

cs_content = cs_content.replace(
    "                      Text('${landPerCrop.toStringAsFixed(1)} Ac (${(percentage * 100).toInt()}%)',",
    "                      Text('${landArea.toStringAsFixed(1)} Ac (${(percentage * 100).toInt()}%)',"
)

with open(crops_screen_path, 'w', encoding='utf-8') as f:
    f.write(cs_content)

print("Done")
