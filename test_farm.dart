import 'package:kisan_mitra/core/models/farm_model.dart';

void main() {
  final map = {
    'ownerId': '123',
    'name': 'Test Farm',
    'state': 'AP',
    'district': 'Ongole',
    'village': 'nagulapadu',
    'soilType': 'Red',
    'landArea': 1.0,
    'waterAvailability': 'High',
    'preferredCrops': ['Basmati Rice', 'Hybrid Cotton'],
    'plantedCrops': [
      {
        'cropName': 'Basmati Rice',
        'plantedDate': DateTime.now().toIso8601String(),
      }
    ]
  };

  final farm = FarmModel.fromMap(map);
  print('preferredCrops: ${farm.preferredCrops}');
  print('plantedCrops: ${farm.plantedCrops.map((c) => c.cropName).toList()}');
}
