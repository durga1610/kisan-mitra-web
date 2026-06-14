class RecommendationModel {
  final String recommendedCrop;
  final String expectedYield;
  final String expectedProfit;
  final String waterRequirement;
  final String fertilizerAdvice;
  final double confidenceScore;

  RecommendationModel({
    required this.recommendedCrop,
    required this.expectedYield,
    required this.expectedProfit,
    required this.waterRequirement,
    required this.fertilizerAdvice,
    required this.confidenceScore,
  });

  Map<String, dynamic> toMap() {
    return {
      'recommendedCrop': recommendedCrop,
      'expectedYield': expectedYield,
      'expectedProfit': expectedProfit,
      'waterRequirement': waterRequirement,
      'fertilizerAdvice': fertilizerAdvice,
      'confidenceScore': confidenceScore,
    };
  }

  factory RecommendationModel.fromMap(Map<String, dynamic> map) {
    return RecommendationModel(
      recommendedCrop: map['recommendedCrop'] ?? '',
      expectedYield: map['expectedYield'] ?? '',
      expectedProfit: map['expectedProfit'] ?? '',
      waterRequirement: map['waterRequirement'] ?? '',
      fertilizerAdvice: map['fertilizerAdvice'] ?? '',
      confidenceScore: (map['confidenceScore'] ?? 0.0).toDouble(),
    );
  }
}
