class MarketPrice {
  final String id;
  final String marketName;
  final String location;
  final String cropName;
  
  // Advanced Pricing
  final double modalPrice;
  final double minPrice;
  final double maxPrice;
  
  final double trendPercentage;
  final double distance;
  final bool isBestPrice;
  final DateTime updatedTime;
  final String category; // vegetables, grains, fruits, cash_crops
  final String cropIcon; // Emoji or asset path

  // AI & Advanced Features
  final String aiAdvice;
  final String bestTimeToSell;
  final String weatherImpact; // 'Positive', 'Negative', 'Neutral'
  final List<double> historicalPrices; // 7-day trend
  final bool isAiEstimate; // Mark AI estimate separately

  MarketPrice({
    required this.id,
    required this.marketName,
    required this.location,
    required this.cropName,
    required this.modalPrice,
    required this.minPrice,
    required this.maxPrice,
    required this.trendPercentage,
    required this.distance,
    this.isBestPrice = false,
    required this.updatedTime,
    required this.category,
    required this.cropIcon,
    this.aiAdvice = '',
    this.bestTimeToSell = 'Now',
    this.weatherImpact = 'Neutral',
    this.historicalPrices = const [],
    this.isAiEstimate = false,
  });

  MarketPrice copyWith({
    String? id,
    String? marketName,
    String? location,
    String? cropName,
    double? modalPrice,
    double? minPrice,
    double? maxPrice,
    double? trendPercentage,
    double? distance,
    bool? isBestPrice,
    DateTime? updatedTime,
    String? category,
    String? cropIcon,
    String? aiAdvice,
    String? bestTimeToSell,
    String? weatherImpact,
    List<double>? historicalPrices,
    bool? isAiEstimate,
  }) {
    return MarketPrice(
      id: id ?? this.id,
      marketName: marketName ?? this.marketName,
      location: location ?? this.location,
      cropName: cropName ?? this.cropName,
      modalPrice: modalPrice ?? this.modalPrice,
      minPrice: minPrice ?? this.minPrice,
      maxPrice: maxPrice ?? this.maxPrice,
      trendPercentage: trendPercentage ?? this.trendPercentage,
      distance: distance ?? this.distance,
      isBestPrice: isBestPrice ?? this.isBestPrice,
      updatedTime: updatedTime ?? this.updatedTime,
      category: category ?? this.category,
      cropIcon: cropIcon ?? this.cropIcon,
      aiAdvice: aiAdvice ?? this.aiAdvice,
      bestTimeToSell: bestTimeToSell ?? this.bestTimeToSell,
      weatherImpact: weatherImpact ?? this.weatherImpact,
      historicalPrices: historicalPrices ?? this.historicalPrices,
      isAiEstimate: isAiEstimate ?? this.isAiEstimate,
    );
  }

  factory MarketPrice.fromJson(Map<String, dynamic> json, [String? docId]) {
    return MarketPrice(
      id: docId ?? json['id'] ?? '',
      marketName: json['marketName'] ?? '',
      location: json['location'] ?? '',
      cropName: json['cropName'] ?? '',
      modalPrice: (json['modalPrice'] ?? 0).toDouble(),
      minPrice: (json['minPrice'] ?? 0).toDouble(),
      maxPrice: (json['maxPrice'] ?? 0).toDouble(),
      trendPercentage: (json['trendPercentage'] ?? 0).toDouble(),
      distance: (json['distance'] ?? 0).toDouble(),
      isBestPrice: json['isBestPrice'] ?? false,
      updatedTime: json['updatedTime'] != null ? DateTime.parse(json['updatedTime'].toString()) : DateTime.now(),
      category: json['category'] ?? '',
      cropIcon: json['cropIcon'] ?? '',
      aiAdvice: json['aiAdvice'] ?? '',
      bestTimeToSell: json['bestTimeToSell'] ?? '',
      weatherImpact: json['weatherImpact'] ?? '',
      historicalPrices: (json['historicalPrices'] as List<dynamic>?)?.map((e) => (e as num).toDouble()).toList() ?? [],
      isAiEstimate: json['isAiEstimate'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'marketName': marketName,
      'location': location,
      'cropName': cropName,
      'modalPrice': modalPrice,
      'minPrice': minPrice,
      'maxPrice': maxPrice,
      'trendPercentage': trendPercentage,
      'distance': distance,
      'isBestPrice': isBestPrice,
      'updatedTime': updatedTime.toIso8601String(),
      'category': category,
      'cropIcon': cropIcon,
      'aiAdvice': aiAdvice,
      'bestTimeToSell': bestTimeToSell,
      'weatherImpact': weatherImpact,
      'historicalPrices': historicalPrices,
      'isAiEstimate': isAiEstimate,
    };
  }
}
