class PlantedCropModel {
  final String cropName;
  final DateTime plantedDate;
  final double? landArea;

  PlantedCropModel({
    required this.cropName,
    required this.plantedDate,
    this.landArea,
  });

  Map<String, dynamic> toMap() {
    return {
      'cropName': cropName,
      'plantedDate': plantedDate.toIso8601String(),
      'landArea': landArea,
    };
  }

  factory PlantedCropModel.fromMap(Map<String, dynamic> map) {
    return PlantedCropModel(
      cropName: map['cropName'] ?? '',
      plantedDate: DateTime.parse(map['plantedDate'] ?? DateTime.now().toIso8601String()),
      landArea: (map['landArea'] as num?)?.toDouble(),
    );
  }
}

class FarmModel {
  final String? id;
  final String ownerId;
  final String name;
  final String state;
  final String district;
  final String village;
  final String soilType;
  final double landArea;
  final String waterAvailability; // e.g., 'Low', 'Medium', 'High'
  final List<String> preferredCrops;
  final List<PlantedCropModel> plantedCrops;
  final DateTime updatedAt;

  FarmModel({
    this.id,
    required this.ownerId,
    required this.name,
    required this.state,
    required this.district,
    required this.village,
    required this.soilType,
    required this.landArea,
    required this.waterAvailability,
    required this.preferredCrops,
    this.plantedCrops = const [],
    required this.updatedAt,
  });

  Map<String, dynamic> toMap() {
    return {
      'ownerId': ownerId,
      'name': name,
      'state': state,
      'district': district,
      'village': village,
      'soilType': soilType,
      'landArea': landArea,
      'waterAvailability': waterAvailability,
      'preferredCrops': preferredCrops,
      'plantedCrops': plantedCrops.map((c) => c.toMap()).toList(),
      'updatedAt': updatedAt.toIso8601String(),
    };
  }

  factory FarmModel.fromMap(Map<String, dynamic> map, {String? docId}) {
    final rawPlanted = map['plantedCrops'] as List?;
    final planted = rawPlanted != null
        ? rawPlanted.map((item) => PlantedCropModel.fromMap(Map<String, dynamic>.from(item))).toList()
        : <PlantedCropModel>[];

    final preferredCrops = List<String>.from(map['preferredCrops'] ?? []);

    // Auto-heal: Ensure all preferred crops exist in planted crops in-memory
    for (var preferredCrop in preferredCrops) {
      final exists = planted.any((c) => c.cropName.toLowerCase() == preferredCrop.toLowerCase());
      if (!exists) {
        planted.add(PlantedCropModel(
          cropName: preferredCrop,
          plantedDate: DateTime.now().subtract(const Duration(days: 1)), // default to yesterday
        ));
      }
    }

    return FarmModel(
      id: docId,
      ownerId: map['ownerId'] ?? '',
      name: map['name'] ?? 'My Field',
      state: map['state'] ?? '',
      district: map['district'] ?? '',
      village: map['village'] ?? '',
      soilType: map['soilType'] ?? '',
      landArea: (map['landArea'] ?? 0.0).toDouble(),
      waterAvailability: map['waterAvailability'] ?? 'Medium',
      preferredCrops: preferredCrops,
      plantedCrops: planted,
      updatedAt: DateTime.parse(map['updatedAt'] ?? DateTime.now().toIso8601String()),
    );
  }
}
