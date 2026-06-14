class CultivatedCrop {
  final String name;
  final String emoji;
  final double landArea; // in Acres
  final double progress; // 0.0 to 1.0
  final String stage; // Sowing, Vegetative, Flowering, Maturity
  final DateTime startDate;
  final DateTime estimatedHarvest;
  final String healthStatus; // Good, Warning, Critical

  CultivatedCrop({
    required this.name,
    required this.emoji,
    required this.landArea,
    required this.progress,
    required this.stage,
    required this.startDate,
    required this.estimatedHarvest,
    required this.healthStatus,
  });
}

class FarmManagementData {
  static const double totalLand = 12.5;

  static List<CultivatedCrop> getActiveCrops() {
    return [
      CultivatedCrop(
        name: 'Wheat',
        emoji: '🌾',
        landArea: 5.0,
        progress: 0.75,
        stage: 'Flowering',
        startDate: DateTime.now().subtract(const Duration(days: 90)),
        estimatedHarvest: DateTime.now().add(const Duration(days: 30)),
        healthStatus: 'Good',
      ),
      CultivatedCrop(
        name: 'Mustard',
        emoji: '🟡',
        landArea: 3.5,
        progress: 0.40,
        stage: 'Vegetative',
        startDate: DateTime.now().subtract(const Duration(days: 45)),
        estimatedHarvest: DateTime.now().add(const Duration(days: 75)),
        healthStatus: 'Warning',
      ),
      CultivatedCrop(
        name: 'Sugarcane',
        emoji: '🎋',
        landArea: 4.0,
        progress: 0.90,
        stage: 'Maturity',
        startDate: DateTime.now().subtract(const Duration(days: 300)),
        estimatedHarvest: DateTime.now().add(const Duration(days: 15)),
        healthStatus: 'Good',
      ),
    ];
  }
}
