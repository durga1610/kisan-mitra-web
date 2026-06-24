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

