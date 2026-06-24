class RecommendationModel {
  final String cropName;
  final String imageUrl;
  final String marketDemand; // High, Medium
  final double demandScore; // 0.0 to 1.0
  final String expectedProfit;
  final List<String> suitableSoil;
  final List<String> suitableRegions;
  final String growthPeriod;
  final String matchReason;
  final double suitabilityScore; // 0.0 to 1.0
  final bool isLocallyCultivated;
  final String? source;

  RecommendationModel({
    required this.cropName,
    required this.imageUrl,
    required this.marketDemand,
    required this.demandScore,
    required this.expectedProfit,
    required this.suitableSoil,
    required this.suitableRegions,
    required this.growthPeriod,
    required this.matchReason,
    this.suitabilityScore = 0.0,
    this.isLocallyCultivated = false,
    this.source,
  });

  Map<String, dynamic> toMap() {
    return {
      'cropName': cropName,
      'imageUrl': imageUrl,
      'marketDemand': marketDemand,
      'demandScore': demandScore,
      'expectedProfit': expectedProfit,
      'suitableSoil': suitableSoil,
      'suitableRegions': suitableRegions,
      'growthPeriod': growthPeriod,
      'matchReason': matchReason,
      'suitabilityScore': suitabilityScore,
      'isLocallyCultivated': isLocallyCultivated,
      'source': source,
    };
  }

  factory RecommendationModel.fromMap(Map<String, dynamic> map) {
    return RecommendationModel(
      cropName: map['cropName'] ?? '',
      imageUrl: map['imageUrl'] ?? '',
      marketDemand: map['marketDemand'] ?? 'Medium',
      demandScore: (map['demandScore'] ?? 0.0).toDouble(),
      expectedProfit: map['expectedProfit'] ?? 'N/A',
      suitableSoil: List<String>.from(map['suitableSoil'] ?? []),
      suitableRegions: List<String>.from(map['suitableRegions'] ?? []),
      growthPeriod: map['growthPeriod'] ?? 'N/A',
      matchReason: map['matchReason'] ?? '',
      suitabilityScore: (map['suitabilityScore'] ?? 0.0).toDouble(),
      isLocallyCultivated: map['isLocallyCultivated'] ?? false,
      source: map['source'],
    );
  }
}

class CustomCropAnalysisModel {
  final String cropName;
  final double score;
  final List<String> warnings;
  final List<String> positives;
  final String verdict;

  CustomCropAnalysisModel({
    required this.cropName,
    required this.score,
    required this.warnings,
    required this.positives,
    required this.verdict,
  });
}

