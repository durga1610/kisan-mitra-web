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

class CropRecommendationData {
  static List<RecommendationModel> getMockRecommendations() {
    return [
      RecommendationModel(
        cropName: 'Organic Wheat',
        imageUrl: 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.95,
        expectedProfit: '₹45,000 - ₹55,000 / Acre',
        suitableSoil: ['Alluvial', 'Loamy'],
        suitableRegions: ['Punjab', 'Haryana', 'Uttar Pradesh', 'Madhya Pradesh'],
        growthPeriod: '120-150 Days',
        matchReason: 'Perfect temperature and soil moisture levels for Rabi season.',
      ),
      RecommendationModel(
        cropName: 'Basmati Rice',
        imageUrl: 'https://images.unsplash.com/photo-1536679545597-c2e5e1946495?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.92,
        expectedProfit: '₹60,000 - ₹75,000 / Acre',
        suitableSoil: ['Clayey', 'Alluvial'],
        suitableRegions: ['Andhra Pradesh', 'Telangana', 'West Bengal', 'Punjab', 'Odisha'],
        growthPeriod: '130-145 Days',
        matchReason: 'High rainfall forecast aligns with irrigation needs.',
      ),
      RecommendationModel(
        cropName: 'Yellow Mustard',
        imageUrl: 'https://images.unsplash.com/photo-1599423956327-02422502697d?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'Medium',
        demandScore: 0.75,
        expectedProfit: '₹30,000 - ₹38,000 / Acre',
        suitableSoil: ['Loamy', 'Sandy'],
        suitableRegions: ['Rajasthan', 'Madhya Pradesh', 'Haryana', 'Uttar Pradesh'],
        growthPeriod: '110-120 Days',
        matchReason: 'Low water requirement makes it suitable for current groundwater levels.',
      ),
      RecommendationModel(
        cropName: 'Sweet Corn',
        imageUrl: 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?q=80&w=500&auto=format&fit=crop',
        marketDemand: 'High',
        demandScore: 0.88,
        expectedProfit: '₹40,000 - ₹50,000 / Acre',
        suitableSoil: ['Alluvial', 'Black'],
        suitableRegions: ['Karnataka', 'Maharashtra', 'Andhra Pradesh', 'Tamil Nadu'],
        growthPeriod: '80-90 Days',
        matchReason: 'Short duration crop with high urban market demand.',
      ),
    ];
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

