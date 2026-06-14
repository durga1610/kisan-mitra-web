import 'dart:io';

void main() {
  final file = File(r'c:\Users\durga\kisan_mitra\lib\core\services\recommendation_service.dart');
  final content = file.readAsStringSync();

  final regex = RegExp(
    r'static Future<List<RecommendationModel>> getRecommendations\(\{.*?\n\s+await Future\.wait\(futures\);\n\s+return recommendations;\n  \}',
    dotAll: true,
  );

  final newFunction = '''static Future<List<RecommendationModel>> getRecommendations({
    required FarmModel farm,
    required WeatherModel weather,
  }) async {
    // Fetch market prices for matching state
    List<MarketPrice> marketPrices = [];
    try {
      marketPrices = await MarketService().getMarketPrices(preferredState: farm.state);
    } catch (e) {
      if (kDebugMode) print('Market fetch failed in recommendation service: \$e');
    }

    final uniqueMarketCrops = marketPrices.map((p) => p.cropName).toSet().toList();
    
    // Leverage Gemini AI to dynamically analyze all factors and suggest crops
    final geminiService = GeminiService(selectedFarm: farm);
    final jsonResponse = await geminiService.generateDynamicRecommendations(
      farm: farm,
      weather: weather,
      availableMarketCrops: uniqueMarketCrops,
    );

    List<RecommendationModel> recommendations = [];
    
    try {
      // Clean up markdown in case the model ignored instructions
      var cleanJson = jsonResponse.replaceAll('```json', '').replaceAll('```', '').trim();
      final List<dynamic> parsedList = json.decode(cleanJson);
      
      for (var item in parsedList) {
        final cropName = item['cropName']?.toString() ?? 'Unknown Crop';
        
        // Pick an image dynamically or fallback to generic
        String imageUrl = 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?q=80&w=500&auto=format&fit=crop';
        try {
          final extended = _getExtendedCropList().firstWhere(
             (c) => c.cropName.toLowerCase().contains(cropName.toLowerCase()) || cropName.toLowerCase().contains(c.cropName.toLowerCase())
          );
          imageUrl = extended.imageUrl;
        } catch (_) {}

        recommendations.add(
          RecommendationModel(
            cropName: cropName,
            imageUrl: imageUrl,
            marketDemand: item['marketDemand']?.toString() ?? 'Medium',
            demandScore: (item['suitabilityScore'] is num) ? (item['suitabilityScore'] as num).toDouble() : 0.8,
            expectedProfit: item['expectedProfit']?.toString() ?? 'Variable',
            suitableSoil: [farm.soilType],
            suitableRegions: [farm.state],
            growthPeriod: item['growthPeriod']?.toString() ?? '90-120 Days',
            matchReason: '🤖 AI: \${item['matchReason']?.toString() ?? 'Highly suitable based on live data.'}',
            suitabilityScore: (item['suitabilityScore'] is num) ? (item['suitabilityScore'] as num).toDouble() : 0.8,
            isLocallyCultivated: uniqueMarketCrops.any((c) => c.toLowerCase().contains(cropName.toLowerCase())),
          )
        );
      }
    } catch (e) {
      if (kDebugMode) print('Failed to parse dynamic recommendations: \$e. Falling back to local algorithm.');
      return _getExtendedCropList().take(3).toList();
    }

    return recommendations;
  }''';

  final newContent = content.replaceFirst(regex, newFunction);
  
  // also add import 'dart:convert'; if not present
  String finalContent = newContent;
  if (!finalContent.contains("import 'dart:convert';")) {
    finalContent = "import 'dart:convert';\n" + finalContent;
  }

  file.writeAsStringSync(finalContent);
  print('Replaced getRecommendations function successfully.');
}
