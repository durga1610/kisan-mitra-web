import 'package:cloud_firestore/cloud_firestore.dart';

class MarketCropPrice {
  final String cropName;
  final String emoji;
  final double currentPrice; // per Quintal
  final double previousPrice;
  final String trend; // 'up', 'down', 'stable'

  MarketCropPrice({
    required this.cropName,
    required this.emoji,
    required this.currentPrice,
    required this.previousPrice,
    required this.trend,
  });

  double get priceChange => currentPrice - previousPrice;
  double get percentageChange => (priceChange / previousPrice) * 100;

  factory MarketCropPrice.fromJson(Map<String, dynamic> json) {
    return MarketCropPrice(
      cropName: json['cropName'] ?? '',
      emoji: json['emoji'] ?? '',
      currentPrice: (json['currentPrice'] ?? 0).toDouble(),
      previousPrice: (json['previousPrice'] ?? 0).toDouble(),
      trend: json['trend'] ?? 'stable',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'cropName': cropName,
      'emoji': emoji,
      'currentPrice': currentPrice,
      'previousPrice': previousPrice,
      'trend': trend,
    };
  }
}

class MarketModel {
  final String? id;
  final String name;
  final String address;
  final double distance; // in km
  final List<MarketCropPrice> cropPrices;
  final bool isBestPrice;

  MarketModel({
    this.id,
    required this.name,
    required this.address,
    required this.distance,
    required this.cropPrices,
    this.isBestPrice = false,
  });

  factory MarketModel.fromJson(Map<String, dynamic> json, [String? id]) {
    return MarketModel(
      id: id,
      name: json['name'] ?? '',
      address: json['address'] ?? '',
      distance: (json['distance'] ?? 0).toDouble(),
      isBestPrice: json['isBestPrice'] ?? false,
      cropPrices: (json['cropPrices'] as List<dynamic>?)
              ?.map((e) => MarketCropPrice.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'address': address,
      'distance': distance,
      'isBestPrice': isBestPrice,
      'cropPrices': cropPrices.map((e) => e.toJson()).toList(),
    };
  }
}

class MarketData {
  static List<MarketModel> getMockMarkets() {
    return [
      MarketModel(
        name: 'APMC Pune (Gultekdi)',
        address: 'Market Yard, Gultekdi, Pune, Maharashtra 411037',
        distance: 4.2,
        isBestPrice: true,
        cropPrices: [
          MarketCropPrice(cropName: 'Wheat', emoji: '🌾', currentPrice: 2450, previousPrice: 2380, trend: 'up'),
          MarketCropPrice(cropName: 'Onion', emoji: '🧅', currentPrice: 1800, previousPrice: 1950, trend: 'down'),
          MarketCropPrice(cropName: 'Potato', emoji: '🥔', currentPrice: 1200, previousPrice: 1200, trend: 'stable'),
        ],
      ),
      MarketModel(
        name: 'Hadapsar Vegetable Market',
        address: 'Hadapsar, Pune, Maharashtra 411028',
        distance: 8.5,
        cropPrices: [
          MarketCropPrice(cropName: 'Tomato', emoji: '🍅', currentPrice: 2200, previousPrice: 2100, trend: 'up'),
          MarketCropPrice(cropName: 'Wheat', emoji: '🌾', currentPrice: 2420, previousPrice: 2400, trend: 'up'),
          MarketCropPrice(cropName: 'Soybean', emoji: '🫘', currentPrice: 4800, previousPrice: 4900, trend: 'down'),
        ],
      ),
      MarketModel(
        name: 'Pimpri Mandi',
        address: 'Pimpri Colony, Pimpri-Chinchwad, Maharashtra 411017',
        distance: 12.1,
        cropPrices: [
          MarketCropPrice(cropName: 'Wheat', emoji: '🌾', currentPrice: 2400, previousPrice: 2410, trend: 'down'),
          MarketCropPrice(cropName: 'Onion', emoji: '🧅', currentPrice: 1750, previousPrice: 1750, trend: 'stable'),
          MarketCropPrice(cropName: 'Turmeric', emoji: '🟡', currentPrice: 7200, previousPrice: 6800, trend: 'up'),
        ],
      ),
    ];
  }

  /// Helper to seed Firestore if empty
  static Future<void> seedFirestoreIfEmpty() async {
    final snapshot = await FirebaseFirestore.instance.collection('markets').limit(1).get();
    if (snapshot.docs.isEmpty) {
      final mockData = getMockMarkets();
      for (var market in mockData) {
        await FirebaseFirestore.instance.collection('markets').add(market.toJson());
      }
    }
  }
}
