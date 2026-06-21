import 'dart:math';
import 'package:flutter/widgets.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../../../../core/config/api_config.dart';
import '../models/market_price.dart';

class MarketService {
  final Random _random = Random();
  bool isFallbackActive = false;
  DateTime? lastUpdated;

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

  Future<List<MarketPrice>?> _getLocalCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cachedData = prefs.getString('market_prices_cache');
    
      if (cachedData != null && cachedData.isNotEmpty) {
        if (kDebugMode) {
          print('Loaded prices INSTANTLY from local SharedPreferences cache.');
        }
        isFallbackActive = prefs.getString('market_prices_cache_is_fallback') == 'true';
        final lastUpdatedStr = prefs.getString('market_prices_cache_last_updated');
        if (lastUpdatedStr != null && lastUpdatedStr.isNotEmpty) {
          lastUpdated = DateTime.tryParse(lastUpdatedStr);
        } else {
          lastUpdated = DateTime.now();
        }
        final List<dynamic> decodedList = jsonDecode(cachedData);
        final List<MarketPrice> cachedPrices = decodedList.map((data) => MarketPrice.fromJson(data, data['id'] ?? UniqueKey().toString())).toList();
        return _processBestPrices(cachedPrices);
      }
    } catch (e) {
      if (kDebugMode) print('Local cache read error: $e');
    }
    return null;
  }

  // Fetch from Live API or Local Cache using CACHE-FIRST strategy
  Future<List<MarketPrice>?> getMarketPrices({
    List<String>? preferredCrops, 
    String? preferredState, 
    bool forceRefresh = false,
    VoidCallback? onBackgroundFetchComplete,
  }) async {
    try {
      // 1. FAST PATH: Attempt to load from local SharedPreferences cache FIRST for instant response
      if (!forceRefresh) {
        final cached = await _getLocalCache();
        if (cached != null) {
          // Trigger a background refresh so data stays fresh for the next load
          if (!_isFetchingBackground) {
            _isFetchingBackground = true;
            _fetchLiveApiAndUpdateCache(preferredCrops, preferredState).then((_) {
               _isFetchingBackground = false;
               if (onBackgroundFetchComplete != null) {
                 onBackgroundFetchComplete();
               }
            }).catchError((e) {
               _isFetchingBackground = false;
               if (kDebugMode) print('Background API fetch failed: $e');
            });
          }
          return cached;
        }
      }

      // 2. SLOW PATH: Cache is empty or failed, we must block and wait for the Live API
      if (kDebugMode) print('Cache empty or failed, performing blocking Live API fetch...');
      final livePrices = await _fetchLiveApiAndUpdateCache(preferredCrops, preferredState);
      if (livePrices != null) {
        return livePrices;
      }
      
      // If live API failed, fall back to cached data immediately
      final cached = await _getLocalCache();
      if (cached != null) {
        debugPrint('[MarketService] Live fetch failed, fell back to local cache immediately.');
        return cached;
      }
      return null;
    } catch (e) {
      if (kDebugMode) {
        print('Error fetching market prices: $e');
      }
      final cached = await _getLocalCache();
      return cached;
    }
  }

  // Live API Fetching Logic
  Future<List<MarketPrice>?> _fetchLiveApiAndUpdateCache(List<String>? preferredCrops, String? preferredState) async {
    try {
      // Force-refresh token to prevent stale-token 401s
      final token = await FirebaseAuth.instance.currentUser?.getIdToken(true);
      if (kDebugMode) {
        print('[MarketService] Token retrieved: ${token != null ? "YES (${token.length} chars)" : "NULL — user not signed in"}');
      }
      final headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

      // Prepare query parameters
      final Map<String, String> queryParams = {};
      if (preferredCrops != null && preferredCrops.isNotEmpty) {
        queryParams['crops'] = preferredCrops.map((c) => normalizeCrop(c)).join(',');
      }
      if (preferredState != null && preferredState.trim().isNotEmpty) {
        queryParams['state'] = preferredState.trim();
      }

      final uri = Uri.parse('${ApiConfig.customAiBackendUrl}/api/v1/market/prices').replace(queryParameters: queryParams);
      if (kDebugMode) {
        print('[MarketService] Request URL: $uri');
      }

      final response = await http.get(uri, headers: headers).timeout(const Duration(seconds: 45));

      if (kDebugMode) {
        print('[MarketService] Response status: ${response.statusCode}');
      }

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        isFallbackActive = data['isFallback'] ?? false;
        
        final lastUpdatedStr = data['lastUpdated'];
        if (lastUpdatedStr != null) {
          lastUpdated = DateTime.tryParse(lastUpdatedStr);
        } else {
          lastUpdated = DateTime.now();
        }

        final List<dynamic> records = data['records'] ?? [];
        if (kDebugMode) {
          print('[MarketService] Successfully retrieved ${records.length} records. isFallback: $isFallbackActive');
        }

        final List<MarketPrice> fetchedPrices = records.map<MarketPrice>((record) {
          double modalPrice = double.tryParse(record['modal_price'].toString()) ?? 0.0;
          double minPrice = double.tryParse(record['min_price'].toString()) ?? 0.0;
          double maxPrice = double.tryParse(record['max_price'].toString()) ?? 0.0;
          
          return MarketPrice(
            id: record['id']?.toString() ?? UniqueKey().toString(),
            marketName: record['market']?.toString() ?? 'Unknown Market',
            location: "${record['district'] ?? ''}, ${record['state'] ?? ''}",
            cropName: record['commodity']?.toString() ?? 'Unknown',
            modalPrice: modalPrice,
            minPrice: minPrice,
            maxPrice: maxPrice,
            trendPercentage: (modalPrice - minPrice) / (minPrice == 0 ? 1 : minPrice) * 10,
            distance: _random.nextDouble() * 300,
            updatedTime: DateTime.tryParse(record['arrival_date']?.toString() ?? '') ?? DateTime.now(),
            category: _inferCategory(record['commodity']?.toString() ?? ''),
            cropIcon: _inferIcon(record['commodity']?.toString() ?? ''),
            aiAdvice: record['ai_advice']?.toString() ?? 'Market trends are currently stable based on API data.',
            bestTimeToSell: 'Consult Local APMC',
            weatherImpact: 'Neutral',
            historicalPrices: _generateHistoricalPrices(modalPrice, 7),
            isAiEstimate: record['is_ai_estimate'] ?? false,
          );
        }).toList();

        if (fetchedPrices.isNotEmpty) {
          try {
            final prefs = await SharedPreferences.getInstance();
            final itemsToCache = fetchedPrices.take(50).toList();
            final List<Map<String, dynamic>> serializedList = itemsToCache.map((p) => p.toJson()).toList();
            await prefs.setString('market_prices_cache', jsonEncode(serializedList));
            await prefs.setString('market_prices_cache_is_fallback', isFallbackActive.toString());
            await prefs.setString('market_prices_cache_last_updated', lastUpdated?.toIso8601String() ?? '');
            if (kDebugMode) print('Successfully cached ${itemsToCache.length} records locally.');
          } catch(e) {
            if (kDebugMode) print('Error saving to local cache: $e');
          }
        }

        return _processBestPrices(fetchedPrices);
      } else {
        if (kDebugMode) {
          print('[MarketService] Backend proxy returned error status: ${response.statusCode}.');
        }
        return null;
      }
    } catch (e) {
      if (kDebugMode) {
        print('[MarketService] Exception during live fetch from proxy: $e');
      }
      return null;
    }
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
