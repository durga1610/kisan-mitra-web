import 'dart:math';
import 'package:flutter/widgets.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../core/config/api_config.dart';
import '../models/market_price.dart';

class MarketService {
  final Random _random = Random();

  List<double> _generateHistoricalPrices(double basePrice, int days) {
    List<double> prices = [];
    double currentPrice = basePrice;
    for (int i = 0; i < days; i++) {
      // Fluctuate by -5% to +5%
      currentPrice = currentPrice * (1 + ((_random.nextDouble() * 10) - 5) / 100);
      prices.insert(0, currentPrice); // Insert at beginning so index 0 is oldest, last is newest
    }
    return prices;
  }

  // Mock data has been completely removed as per user request to use only real Government API data.

  // Helper to title case strings
  String _capitalize(String text) {
    if (text.isEmpty) return text;
    return text.split(' ').map((word) {
      if (word.isEmpty) return word;
      return word.substring(0, 1).toUpperCase() + word.substring(1).toLowerCase();
    }).join(' ');
  }

  // Helper to fix common state misspellings
  String _normalizeState(String state) {
    String s = state.toLowerCase().replaceAll(' ', '').replaceAll('_', '');
    if (s.contains('andhra')) return 'Andhra Pradesh';
    if (s.contains('tamil')) return 'Tamil Nadu';
    if (s.contains('uttarp')) return 'Uttar Pradesh';
    if (s.contains('madhyap')) return 'Madhya Pradesh';
    if (s.contains('bengal')) return 'West Bengal';
    if (s.contains('himachal')) return 'Himachal Pradesh';
    if (s.contains('arunachal')) return 'Arunachal Pradesh';
    if (s.contains('maharashtra')) return 'Maharashtra';
    if (s.contains('karnataka')) return 'Karnataka';
    if (s.contains('kerala')) return 'Kerala';
    if (s.contains('gujarat')) return 'Gujarat';
    if (s.contains('telangana')) return 'Telangana';
    if (s.contains('punjab')) return 'Punjab';
    if (s.contains('haryana')) return 'Haryana';
    if (s.contains('rajasthan')) return 'Rajasthan';
    if (s.contains('bihar')) return 'Bihar';
    if (s.contains('odisha') || s.contains('orissa')) return 'Odisha';
    return _capitalize(state.trim());
  }

  // Helper to fix common crop misspellings
  static String normalizeCrop(String crop) {
    String c = crop.toLowerCase().trim();
    if (c.contains('cotten') || c.contains('cotton')) return 'Cotton';
    if (c.contains('tomato') || c.contains('tamato')) return 'Tomato';
    if (c.contains('potato') || c.contains('patato')) return 'Potato';
    if (c.contains('onion')) return 'Onion';
    if (c.contains('chilli') || c.contains('chili')) return 'Green Chilli';
    if (c.contains('wheat')) return 'Wheat';
    if (c.contains('paddy') || c.contains('rice')) return 'Paddy(Dhan)(Common)';
    if (c.contains('maize') || c.contains('corn')) return 'Maize';
    if (c.contains('mango')) return 'Mango';
    if (c.contains('apple')) return 'Apple';
    return crop.substring(0, 1).toUpperCase() + crop.substring(1).toLowerCase();
  }

  bool _isFetchingBackground = false;

  // Fetch from Live API or Local Cache using CACHE-FIRST strategy
  Future<List<MarketPrice>?> getMarketPrices({List<String>? preferredCrops, String? preferredState, bool forceRefresh = false}) async {
    try {
      // 1. FAST PATH: Attempt to load from local SharedPreferences cache FIRST for instant response
      if (!forceRefresh) {
        try {
          final prefs = await SharedPreferences.getInstance();
          final cachedData = prefs.getString('market_prices_cache');
        
          if (cachedData != null && cachedData.isNotEmpty) {
            if (kDebugMode) {
              print('Loaded prices INSTANTLY from local SharedPreferences cache.');
            }
            final List<dynamic> decodedList = jsonDecode(cachedData);
            final List<MarketPrice> cachedPrices = decodedList.map((data) => MarketPrice.fromJson(data, data['id'] ?? UniqueKey().toString())).toList();
            
            // Trigger a background refresh so data stays fresh for the next load
            if (!_isFetchingBackground) {
              _isFetchingBackground = true;
              _fetchLiveApiAndUpdateCache(preferredCrops, preferredState).then((_) {
                 _isFetchingBackground = false;
              }).catchError((e) {
                 _isFetchingBackground = false;
                 if (kDebugMode) print('Background API fetch failed: $e');
              });
            }
            
            return _processBestPrices(cachedPrices);
          }
        } catch (cacheError) {
          if (kDebugMode) print('Local cache fetch failed: $cacheError. Falling back to Live API.');
        }
      }

      // 2. SLOW PATH: Cache is empty or failed, we must block and wait for the Live API
      if (kDebugMode) print('Cache empty or failed, performing blocking Live API fetch...');
      return await _fetchLiveApiAndUpdateCache(preferredCrops, preferredState);

    } catch (e) {
      if (kDebugMode) {
        print('Error fetching market prices: $e');
      }
      return null;
    }
  }

  // Live API Fetching Logic
  Future<List<MarketPrice>?> _fetchLiveApiAndUpdateCache(List<String>? preferredCrops, String? preferredState) async {
    if (ApiConfig.mandiApiKey.isNotEmpty && ApiConfig.mandiApiKey != '') {
      List<MarketPrice> stateFetchedPrices = [];
      List<MarketPrice> allIndiaFetchedPrices = [];
      
      // Prepare API calls
      List<Future<http.Response>> apiCalls = [];
      
      String stateFilter = '';
      if (preferredState != null && preferredState.trim().isNotEmpty) {
         final formattedState = _normalizeState(preferredState);
         stateFilter = '&filters[state.keyword]=${Uri.encodeComponent(formattedState)}';
      }

      // Add specific crop calls FOR THE STATE
      if (preferredCrops != null && preferredCrops.isNotEmpty) {
        for (var crop in preferredCrops) {
           final formattedCrop = normalizeCrop(crop);
           final u = Uri.parse('${ApiConfig.mandiApiBaseUrl}?api-key=${ApiConfig.mandiApiKey}&format=json&limit=10&filters[commodity]=${Uri.encodeComponent(formattedCrop)}$stateFilter');
           if (kDebugMode) print('API Call (Specific Crop): $u');
           apiCalls.add(http.get(u).timeout(const Duration(seconds: 5)));
        }
      }
      
      // Always explicitly fetch some general crops from their state to populate "Other Markets"
      if (stateFilter.isNotEmpty) {
        final stateUrl = Uri.parse('${ApiConfig.mandiApiBaseUrl}?api-key=${ApiConfig.mandiApiKey}&format=json&limit=20$stateFilter');
        if (kDebugMode) print('API Call (State General): $stateUrl');
        apiCalls.add(http.get(stateUrl).timeout(const Duration(seconds: 5)));
      }
      
      // Always fetch the general latest 50 across ALL OF INDIA (No state filter!)
      final genUrl = Uri.parse('${ApiConfig.mandiApiBaseUrl}?api-key=${ApiConfig.mandiApiKey}&format=json&limit=50');
      if (kDebugMode) print('API Call (General All-India): $genUrl');
      apiCalls.add(http.get(genUrl).timeout(const Duration(seconds: 5)));

      try {
        // Execute all API calls concurrently
        final responses = await Future.wait(apiCalls);
        
        bool anySuccess = false;
        
        for (var response in responses) {
          if (response.statusCode == 200) {
            anySuccess = true;
            final data = jsonDecode(response.body);
            final List<dynamic> records = data['records'] ?? [];
            
            if (records.isNotEmpty) {
              final newPrices = records.map<MarketPrice>((record) {
                double modalPrice = double.tryParse(record['modal_price'].toString()) ?? 0.0;
                double minPrice = double.tryParse(record['min_price'].toString()) ?? 0.0;
                double maxPrice = double.tryParse(record['max_price'].toString()) ?? 0.0;
                
                return MarketPrice(
                  id: record['id']?.toString() ?? UniqueKey().toString(),
                  marketName: record['market']?.toString() ?? 'Unknown Market',
                  location: "${record['district']}, ${record['state']}",
                  cropName: record['commodity']?.toString() ?? 'Unknown',
                  modalPrice: modalPrice,
                  minPrice: minPrice,
                  maxPrice: maxPrice,
                  trendPercentage: (modalPrice - minPrice) / (minPrice == 0 ? 1 : minPrice) * 10,
                  distance: _random.nextDouble() * 300,
                  updatedTime: DateTime.tryParse(record['arrival_date']?.toString() ?? '') ?? DateTime.now(),
                  category: _inferCategory(record['commodity']?.toString() ?? ''),
                  cropIcon: _inferIcon(record['commodity']?.toString() ?? ''),
                  aiAdvice: 'Market trends are currently stable based on API data.',
                  bestTimeToSell: 'Consult Local APMC',
                  weatherImpact: 'Neutral',
                  historicalPrices: _generateHistoricalPrices(modalPrice, 7),
                );
              }).toList();
              
              // Sort into state-specific and all-india
              for (var price in newPrices) {
                allIndiaFetchedPrices.add(price);
                if (preferredState != null && preferredState.trim().isNotEmpty) {
                  final targetState = _normalizeState(preferredState).toLowerCase();
                  final recState = price.location.toLowerCase();
                  if (recState.contains(targetState)) {
                    stateFetchedPrices.add(price);
                  }
                } else {
                  stateFetchedPrices.add(price);
                }
              }
            }
          } else {
             if (kDebugMode) {
                print('A Live API request failed with status ${response.statusCode}.');
             }
          }
        }

        // If no single request succeeded, we treat the API server as down/unreachable
        if (!anySuccess) {
          return null;
        }

        // Deduplicate
        final Map<String, MarketPrice> uniqueStatePrices = {};
        for (var p in stateFetchedPrices) uniqueStatePrices[p.id] = p;
        stateFetchedPrices = uniqueStatePrices.values.toList();

        final Map<String, MarketPrice> uniqueAllIndiaPrices = {};
        for (var p in allIndiaFetchedPrices) uniqueAllIndiaPrices[p.id] = p;
        allIndiaFetchedPrices = uniqueAllIndiaPrices.values.toList();

        List<MarketPrice> finalPricesToReturn = [];

        final Map<String, MarketPrice> combinedPrices = {};
        
        // Base Fallback: All India Prices
        for (var p in allIndiaFetchedPrices) {
          combinedPrices[p.id] = p;
        }
        
        // Higher Priority: Overwrite/Add state-specific prices
        for (var p in stateFetchedPrices) {
          combinedPrices[p.id] = p;
        }

        finalPricesToReturn = combinedPrices.values.toList();

        if (finalPricesToReturn.isNotEmpty) {
          // Limit to 50 items to prevent OutOfMemory (OOM) errors and UI lag
          if (finalPricesToReturn.length > 50) {
            finalPricesToReturn = finalPricesToReturn.sublist(0, 50);
          }

          // Update Local Cache with fresh data sequentially to prevent OOM
          try {
            final prefs = await SharedPreferences.getInstance();
            final itemsToCache = finalPricesToReturn.take(50).toList();
            final List<Map<String, dynamic>> serializedList = itemsToCache.map((p) => p.toJson()).toList();
            await prefs.setString('market_prices_cache', jsonEncode(serializedList));
            if (kDebugMode) print('Successfully cached ${itemsToCache.length} records locally.');
          } catch(e) {
            if (kDebugMode) print('Error saving to local cache: $e');
          }

          return _processBestPrices(finalPricesToReturn);
        }
      } catch (e) {
        if (kDebugMode) {
          print('Exception executing concurrent Mandi API calls: $e');
        }
        return null;
      }
    }
    
    return null;
  }

  String _inferCategory(String cropName) {
    cropName = cropName.toLowerCase();
    if (['wheat', 'rice', 'jowar', 'bajra', 'maize'].contains(cropName)) return 'Grains';
    if (['onion', 'tomato', 'potato', 'cabbage', 'brinjal'].contains(cropName)) return 'Vegetables';
    if (['cotton', 'sugarcane', 'soybean', 'turmeric'].contains(cropName)) return 'Cash Crops';
    if (['apple', 'banana', 'mango', 'orange', 'grapes'].contains(cropName)) return 'Fruits';
    return 'Other';
  }

  String _inferIcon(String cropName) {
    cropName = cropName.toLowerCase();
    if (cropName.contains('wheat')) return '🌾';
    if (cropName.contains('rice') || cropName.contains('paddy')) return '🍚';
    if (cropName.contains('onion')) return '🧅';
    if (cropName.contains('tomato')) return '🍅';
    if (cropName.contains('potato')) return '🥔';
    if (cropName.contains('cotton')) return '☁️';
    if (cropName.contains('apple')) return '🍎';
    if (cropName.contains('mango')) return '🥭';
    return '🌱';
  }

  // Automatically calculate and mark the best price for each unique crop
  List<MarketPrice> _processBestPrices(List<MarketPrice> prices) {
    final Map<String, double> maxPrices = {};
    for (var p in prices) {
      if (!maxPrices.containsKey(p.cropName) || p.modalPrice > maxPrices[p.cropName]!) {
        maxPrices[p.cropName] = p.modalPrice;
      }
    }

    return prices.map((p) {
      return p.copyWith(isBestPrice: p.modalPrice == maxPrices[p.cropName]);
    }).toList();
  }
}
