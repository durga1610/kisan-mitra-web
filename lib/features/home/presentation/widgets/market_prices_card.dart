import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../market/presentation/providers/market_provider.dart';
import '../../../market/data/models/market_price.dart';
import '../../../../core/repositories/market_repository.dart';
import '../../../../core/localization/app_translations.dart';

class MarketPricesCard extends StatelessWidget {
  const MarketPricesCard({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MarketProvider>();

    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: provider.isLoading 
        ? const SizedBox(
            height: 200,
            child: Center(child: CircularProgressIndicator(color: AppColors.primary)),
          )
        : _buildContent(context, provider),
    );
  }

  Widget _buildContent(BuildContext context, MarketProvider provider) {
    if (!provider.hasPlantedCrops && provider.otherPrices.isEmpty) {
      return const SizedBox.shrink();
    }

    final List<Widget> myCropTiles = [];
    final uniqueMyCrops = <String>{};

    if (provider.hasPlantedCrops) {
      for (var cropName in provider.plantedCrops.take(3)) {
        final matches = provider.myCropPrices.where((p) {
          String pLower = p.cropName.toLowerCase();
          String cLower = cropName.toLowerCase();
          return pLower.contains(cLower) || pLower.contains(MarketRepository.normalizeCrop(cropName).toLowerCase());
        }).toList();

        if (matches.isNotEmpty) {
          // Prioritize matches that are in the user's state
          matches.sort((a, b) {
             bool aInState = provider.farmState.isNotEmpty && a.location.toLowerCase().contains(provider.farmState.toLowerCase());
             bool bInState = provider.farmState.isNotEmpty && b.location.toLowerCase().contains(provider.farmState.toLowerCase());
             if (aInState && !bInState) return -1;
             if (!aInState && bInState) return 1;
             return 0;
          });

          final bestMatch = matches.first;
          bool isOutOfState = provider.farmState.isNotEmpty && !bestMatch.location.toLowerCase().contains(provider.farmState.toLowerCase());

          if (isOutOfState) {
            myCropTiles.add(_EmptyMarketTile(cropName: cropName, farmState: provider.farmState));
          } else {
            if (uniqueMyCrops.add(bestMatch.cropName)) {
              myCropTiles.add(_MarketTile(item: bestMatch));
            }
          }
        } else {
          myCropTiles.add(_EmptyMarketTile(cropName: cropName, farmState: provider.farmState));
        }
      }
    }

    // Take remaining to make 5 from other crops
    final uniqueOtherCrops = <String>{};
    final otherDisplayPrices = provider.otherPrices
        .where((p) => uniqueOtherCrops.add(p.cropName) && !uniqueMyCrops.contains(p.cropName))
        .take(5 - myCropTiles.length)
        .toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (provider.hasPlantedCrops) ...[
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
            child: Text(
              'Your Crops'.tr(context),
              style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.primary),
            ),
          ),
          ...List.generate(myCropTiles.length, (index) {
            return Column(
              children: [
                myCropTiles[index],
                if (index < myCropTiles.length - 1 || otherDisplayPrices.isNotEmpty)
                  const Divider(height: 1, color: AppColors.divider, indent: 68),
              ],
            );
          }),
        ],
        if (otherDisplayPrices.isNotEmpty)
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
            child: Text(
              'Other Markets'.tr(context),
              style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.bold, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
            ),
          ),
        ...List.generate(otherDisplayPrices.length, (index) {
          final isLast = index == otherDisplayPrices.length - 1;
          return Column(
            children: [
              _MarketTile(item: otherDisplayPrices[index]),
              if (!isLast)
                const Divider(height: 1, color: AppColors.divider, indent: 68),
            ],
          );
        }),
      ],
    );
  }
}

class _MarketTile extends StatelessWidget {
  final MarketPrice item;
  const _MarketTile({required this.item});

  @override
  Widget build(BuildContext context) {
    final isPositive = item.trendPercentage >= 0;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          // Icon
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Center(
              child: Text(item.cropIcon, style: const TextStyle(fontSize: 22)),
            ),
          ),
          const SizedBox(width: 12),

          // Name & Market
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.cropName.tr(context),
                  style: GoogleFonts.poppins(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Theme.of(context).colorScheme.onSurface,
                  ),
                ),
                Text(
                  item.marketName.tr(context),
                  style: GoogleFonts.poppins(
                    fontSize: 11,
                    color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),

          // Price & Change
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '₹${item.modalPrice.toInt()}/q',
                style: GoogleFonts.poppins(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: Theme.of(context).colorScheme.onSurface,
                ),
              ),
              Row(
                children: [
                  Icon(
                    isPositive ? Icons.trending_up_rounded : Icons.trending_down_rounded,
                    size: 14,
                    color: isPositive ? AppColors.success : Colors.red,
                  ),
                  const SizedBox(width: 2),
                  Text(
                    '${item.trendPercentage.abs().toStringAsFixed(1)}%',
                    style: GoogleFonts.poppins(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: isPositive ? AppColors.success : Colors.red,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _EmptyMarketTile extends StatelessWidget {
  final String cropName;
  final String? farmState;
  const _EmptyMarketTile({required this.cropName, this.farmState});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          // Icon
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: Colors.grey.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Center(
              child: Icon(Icons.grass_rounded, color: Colors.grey),
            ),
          ),
          const SizedBox(width: 12),

          // Name & Market
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  cropName.substring(0, 1).toUpperCase() + cropName.substring(1).toLowerCase(),
                  style: GoogleFonts.poppins(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Theme.of(context).colorScheme.onSurface,
                  ),
                ),
                Text(
                  farmState != null && farmState!.isNotEmpty 
                      ? 'No data in $farmState'.tr(context)
                      : 'Govt API data currently unavailable'.tr(context),
                  style: GoogleFonts.poppins(
                    fontSize: 11,
                    color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5),
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),
          
          // Price placeholder
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '--',
                style: GoogleFonts.poppins(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.3),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
