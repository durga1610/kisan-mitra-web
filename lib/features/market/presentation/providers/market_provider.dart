import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import '../../data/models/market_price.dart';
import '../../data/services/market_service.dart';
import '../../../notifications/data/models/km_notification_type.dart';
import '../../../notifications/data/services/notification_service.dart';
enum MarketSortBy { priceHigh, priceLow, distance, trend, state }

class MarketProvider extends ChangeNotifier {
  final MarketService _service = MarketService();
  
  List<MarketPrice> _allPrices = [];
  List<MarketPrice> _myCropPrices = [];
  List<MarketPrice> _otherPrices = [];
  
  bool _isLoading = false;
  bool _isServerDown = false;
  String _searchQuery = '';
  String _selectedCategory = 'All';
  MarketSortBy _sortBy = MarketSortBy.priceHigh;
  
  List<String> _plantedCrops = [];
  String _farmState = '';
  Timer? _livePriceTimer;
  final Random _random = Random();

  List<MarketPrice> get myCropPrices => _myCropPrices;
  List<MarketPrice> get otherPrices => _otherPrices;
  bool get isLoading => _isLoading;
  bool get isServerDown => _isServerDown;
  String get searchQuery => _searchQuery;
  String get selectedCategory => _selectedCategory;
  MarketSortBy get sortBy => _sortBy;
  bool get hasPlantedCrops => _plantedCrops.isNotEmpty;
  List<String> get plantedCrops => _plantedCrops;
  String get farmState => _farmState;

  MarketProvider() {
    fetchPrices();
    _startLivePriceSimulation();
  }

  @override
  void dispose() {
    _livePriceTimer?.cancel();
    super.dispose();
  }

  void updateFarmContext(List<String> plantedCrops, String farmState) {
    debugPrint('Farm Context Updated! Crops: $plantedCrops, State: "$farmState"');
    if (_plantedCrops.join(',') != plantedCrops.join(',') || _farmState != farmState) {
      _plantedCrops = plantedCrops;
      _farmState = farmState;
      // Re-fetch prices to guarantee we query the API for the specific crops and state
      fetchPrices();
    } else {
      _applyFilters();
      notifyListeners();
    }
  }

  void _startLivePriceSimulation() {
    // Simulate live market fluctuation every 30 seconds instead of 3 to reduce UI lag
    _livePriceTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (_allPrices.isEmpty) return;

      bool hasChanges = false;
      // Randomly update 1 or 2 prices to simulate live ticker
      int numUpdates = _random.nextInt(3) + 1; // 1 to 3 updates
      
      for (int i = 0; i < numUpdates; i++) {
        int index = _random.nextInt(_allPrices.length);
        MarketPrice p = _allPrices[index];
        
        // Fluctuate price by -2% to +2%
        double changePercent = (_random.nextDouble() * 4) - 2;
        double newModalPrice = p.modalPrice * (1 + changePercent / 100);
        
        // Update trend based on latest tick
        double newTrend = p.trendPercentage + (changePercent * 0.1);

        // Update historical prices (keep last 7)
        List<double> newHistory = List.from(p.historicalPrices);
        if (newHistory.isNotEmpty) {
          newHistory.removeAt(0); // remove oldest
          newHistory.add(newModalPrice); // add newest
        }
        
        _allPrices[index] = p.copyWith(
          modalPrice: newModalPrice,
          trendPercentage: newTrend,
          updatedTime: DateTime.now(),
          historicalPrices: newHistory,
        );
        hasChanges = true;
      }

      if (hasChanges) {
        _applyFilters();
        notifyListeners();
        
        // Simulate a notification if the random change is significant
        // Pick one of the changed prices to notify if it's a planted crop
        final largeChanges = _myCropPrices.where((p) => p.updatedTime.difference(DateTime.now()).inSeconds.abs() < 5 && p.trendPercentage.abs() > 1.5).toList();
        if (largeChanges.isNotEmpty) {
           final changedCrop = largeChanges.first;
           final direction = changedCrop.trendPercentage > 0 ? "Up" : "Down";
           try {
             NotificationService().triggerCustomNotification(
               title: 'Market Price Alert',
               body: '${changedCrop.cropName} price is $direction by ${changedCrop.trendPercentage.toStringAsFixed(1)}% in ${changedCrop.marketName}!',
               type: KmNotificationType.market,
             );
           } catch (e) {
             debugPrint('Error triggering notification: $e');
           }
        }
      }
    });
  }

  int _activeFetchId = 0;

  Future<void> fetchPrices({bool forceRefresh = false}) async {
    final currentFetchId = ++_activeFetchId;
    _isLoading = true;
    notifyListeners();

    try {
      final newPrices = await _service.getMarketPrices(preferredCrops: _plantedCrops, preferredState: _farmState, forceRefresh: forceRefresh);
      
      // Prevent race condition: only apply if this is the most recent fetch
      if (currentFetchId == _activeFetchId) {
        if (newPrices == null) {
          _isServerDown = true;
          _allPrices = [];
          _myCropPrices = [];
          _otherPrices = [];
        } else {
          _isServerDown = false;
          _allPrices = newPrices;
          _applyFilters();
        }
      }
    } catch (e) {
      debugPrint('Error fetching market prices: $e');
      if (currentFetchId == _activeFetchId) {
        _isServerDown = true;
        _allPrices = [];
        _myCropPrices = [];
        _otherPrices = [];
      }
    } finally {
      if (currentFetchId == _activeFetchId) {
        _isLoading = false;
        notifyListeners();
      }
    }
  }

  void setSearchQuery(String query) {
    _searchQuery = query;
    _applyFilters();
    notifyListeners();
  }

  void setCategory(String category) {
    _selectedCategory = category;
    _applyFilters();
    notifyListeners();
  }

  void setSortBy(MarketSortBy sortBy) {
    _sortBy = sortBy;
    _applyFilters();
    notifyListeners();
  }

  void _applyFilters() {
    List<MarketPrice> filtered = _allPrices.where((price) {
      final matchesSearch = price.cropName.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          price.marketName.toLowerCase().contains(_searchQuery.toLowerCase());
      
      final matchesCategory = _selectedCategory == 'All' || 
          price.category.toLowerCase().contains(_selectedCategory.toLowerCase().replaceAll(' ', '_'));

      return matchesSearch && matchesCategory;
    }).toList();

    // Apply Sorting
    switch (_sortBy) {
      case MarketSortBy.priceHigh:
        filtered.sort((a, b) => b.modalPrice.compareTo(a.modalPrice));
        break;
      case MarketSortBy.priceLow:
        filtered.sort((a, b) => a.modalPrice.compareTo(b.modalPrice));
        break;
      case MarketSortBy.distance:
        filtered.sort((a, b) => a.distance.compareTo(b.distance));
        break;
      case MarketSortBy.trend:
        filtered.sort((a, b) => b.trendPercentage.compareTo(a.trendPercentage));
        break;
      case MarketSortBy.state:
        filtered.sort((a, b) {
           bool aInState = _farmState.isNotEmpty && a.location.toLowerCase().contains(_farmState.toLowerCase());
           bool bInState = _farmState.isNotEmpty && b.location.toLowerCase().contains(_farmState.toLowerCase());
           if (aInState && !bInState) return -1;
           if (!aInState && bInState) return 1;
           return a.location.compareTo(b.location);
        });
        break;
    }

    // Split into My Crops and Other Crops
    _myCropPrices = [];
    _otherPrices = [];
    
    for (var price in filtered) {
      // Check if price matches any planted crop
      bool isMyCrop = _plantedCrops.any((c) {
        String cLower = c.toLowerCase();
        String pLower = price.cropName.toLowerCase();
        return pLower.contains(cLower) || pLower.contains(MarketService.normalizeCrop(c).toLowerCase());
      });
      if (isMyCrop) {
        _myCropPrices.add(price);
      } else {
        _otherPrices.add(price);
      }
    }
  }
}
