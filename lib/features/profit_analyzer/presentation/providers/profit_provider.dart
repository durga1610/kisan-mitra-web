import 'package:flutter/material.dart';
import '../../data/models/profit_models.dart';
import '../../data/services/profit_service.dart';

class ProfitProvider extends ChangeNotifier {
  final ProfitService _service = ProfitService();
  
  List<CropProfit> _records = [];
  bool _isLoading = false;
  String _filterSeason = 'All';
  String _filterCrop = 'All';

  List<CropProfit> get records => _records.where((r) {
    final matchesSeason = _filterSeason == 'All' || r.season == _filterSeason;
    final matchesCrop = _filterCrop == 'All' || r.cropName == _filterCrop;
    return matchesSeason && matchesCrop;
  }).toList();

  bool get isLoading => _isLoading;
  String get filterSeason => _filterSeason;
  String get filterCrop => _filterCrop;

  List<String> get availableCrops => ['All', ..._records.map((e) => e.cropName).toSet()];

  ProfitProvider() {
    _init();
  }

  void _init() {
    _service.streamProfitRecords().listen((data) {
      _records = data;
      notifyListeners();
    });
  }

  void setSeasonFilter(String season) {
    _filterSeason = season;
    notifyListeners();
  }

  void setCropFilter(String crop) {
    _filterCrop = crop;
    notifyListeners();
  }

  Future<void> addRecord(CropProfit record) async {
    await _service.saveProfitRecord(record);
  }

  Future<void> deleteRecord(String id) async {
    await _service.deleteRecord(id);
  }

  // Analytics Helpers
  double get totalYearlyProfit => _records.fold(0, (sum, r) => sum + r.netProfit);
  
  Map<String, double> get expenseDistribution {
    double seed = 0, fert = 0, pest = 0, irr = 0, lab = 0, mach = 0, trans = 0, other = 0;
    for (var r in _records) {
      seed += r.expenses.seed;
      fert += r.expenses.fertilizer;
      pest += r.expenses.pesticide;
      irr += r.expenses.irrigation;
      lab += r.expenses.labor;
      mach += r.expenses.machinery;
      trans += r.expenses.transport;
      other += r.expenses.other;
    }
    return {
      'Seeds': seed,
      'Fertilizer': fert,
      'Pesticide': pest,
      'Irrigation': irr,
      'Labor': lab,
      'Machinery': mach,
      'Transport': trans,
      'Other': other,
    };
  }
}
