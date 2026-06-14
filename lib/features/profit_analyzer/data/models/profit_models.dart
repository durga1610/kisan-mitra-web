import 'package:cloud_firestore/cloud_firestore.dart';

class CropProfit {
  final String id;
  final String cropName;
  final String season;
  final double landArea;
  final ExpenseModel expenses;
  final double yieldAmount; // in Quintals
  final double pricePerQuintal;
  final DateTime createdAt;

  CropProfit({
    required this.id,
    required this.cropName,
    required this.season,
    required this.landArea,
    required this.expenses,
    required this.yieldAmount,
    required this.pricePerQuintal,
    required this.createdAt,
  });

  double get totalInvestment => expenses.total;
  double get totalRevenue => yieldAmount * pricePerQuintal;
  double get netProfit => totalRevenue - totalInvestment;
  double get profitMargin => totalRevenue > 0 ? (netProfit / totalRevenue) * 100 : 0;
  double get costPerAcre => landArea > 0 ? totalInvestment / landArea : 0;
  double get revenuePerAcre => landArea > 0 ? totalRevenue / landArea : 0;
  double get breakEvenPrice => yieldAmount > 0 ? totalInvestment / yieldAmount : 0;

  Map<String, dynamic> toMap() {
    return {
      'cropName': cropName,
      'season': season,
      'landArea': landArea,
      'expenses': expenses.toMap(),
      'yieldAmount': yieldAmount,
      'pricePerQuintal': pricePerQuintal,
      'createdAt': createdAt,
    };
  }

  factory CropProfit.fromMap(String id, Map<String, dynamic> map) {
    return CropProfit(
      id: id,
      cropName: map['cropName'] ?? '',
      season: map['season'] ?? '',
      landArea: (map['landArea'] ?? 0).toDouble(),
      expenses: ExpenseModel.fromMap(map['expenses'] ?? {}),
      yieldAmount: (map['yieldAmount'] ?? 0).toDouble(),
      pricePerQuintal: (map['pricePerQuintal'] ?? 0).toDouble(),
      createdAt: (map['createdAt'] as Timestamp).toDate(),
    );
  }
}

class ExpenseModel {
  final double seed;
  final double fertilizer;
  final double pesticide;
  final double irrigation;
  final double labor;
  final double machinery;
  final double transport;
  final double other;

  ExpenseModel({
    this.seed = 0,
    this.fertilizer = 0,
    this.pesticide = 0,
    this.irrigation = 0,
    this.labor = 0,
    this.machinery = 0,
    this.transport = 0,
    this.other = 0,
  });

  double get total => seed + fertilizer + pesticide + irrigation + labor + machinery + transport + other;

  Map<String, dynamic> toMap() {
    return {
      'seed': seed,
      'fertilizer': fertilizer,
      'pesticide': pesticide,
      'irrigation': irrigation,
      'labor': labor,
      'machinery': machinery,
      'transport': transport,
      'other': other,
    };
  }

  factory ExpenseModel.fromMap(Map<String, dynamic> map) {
    return ExpenseModel(
      seed: (map['seed'] ?? 0).toDouble(),
      fertilizer: (map['fertilizer'] ?? 0).toDouble(),
      pesticide: (map['pesticide'] ?? 0).toDouble(),
      irrigation: (map['irrigation'] ?? 0).toDouble(),
      labor: (map['labor'] ?? 0).toDouble(),
      machinery: (map['machinery'] ?? 0).toDouble(),
      transport: (map['transport'] ?? 0).toDouble(),
      other: (map['other'] ?? 0).toDouble(),
    );
  }
}
