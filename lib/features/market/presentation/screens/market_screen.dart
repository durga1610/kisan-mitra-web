import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:shimmer/shimmer.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/providers/farm_provider.dart';
import '../providers/market_provider.dart';
import '../widgets/market_card.dart';

class MarketScreen extends StatelessWidget {
  const MarketScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const _MarketScreenContent();
  }
}

class _MarketScreenContent extends StatefulWidget {
  const _MarketScreenContent();

  @override
  State<_MarketScreenContent> createState() => _MarketScreenContentState();
}

class _MarketScreenContentState extends State<_MarketScreenContent> with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MarketProvider>();

    return Scaffold(
      
      appBar: AppBar(
        title: Row(
          children: [
            Text(
              'Market Prices',
              style: GoogleFonts.poppins(fontWeight: FontWeight.w700, fontSize: 18, color: Colors.white),
            ),
            const SizedBox(width: 8),
            FadeTransition(
              opacity: _pulseController,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.withValues(alpha: 0.5)),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 6,
                      height: 6,
                      decoration: const BoxDecoration(
                        color: Colors.red,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'LIVE',
                      style: GoogleFonts.poppins(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.red),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.sort_rounded, color: Colors.white),
            onPressed: () => _showSortBottomSheet(context, provider),
          ),
        ],
      ),
      body: Column(
        children: [
          _buildSearchAndFilter(context, provider),
          Expanded(
            child: RefreshIndicator(
              onRefresh: () => provider.fetchPrices(forceRefresh: true),
              color: AppColors.primary,
              child: _buildMainContent(provider),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchAndFilter(BuildContext context, MarketProvider provider) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
      child: Column(
        children: [
          // Search Bar
          TextField(
            onChanged: provider.setSearchQuery,
            decoration: InputDecoration(
              hintText: 'Search any crop or market price...',
              prefixIcon: const Icon(Icons.search_rounded, color: AppColors.primary),
              filled: true,
              fillColor: AppColors.surfaceVariant,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(16),
                borderSide: BorderSide.none,
              ),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            ),
          ),
          const SizedBox(height: 16),
          
          // Category Filters
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _filterChip(provider, 'All'),
                _filterChip(provider, 'Vegetables'),
                _filterChip(provider, 'Grains'),
                _filterChip(provider, 'Fruits'),
                _filterChip(provider, 'Cash Crops'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _filterChip(MarketProvider provider, String label) {
    final isSelected = provider.selectedCategory == label;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ChoiceChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (selected) {
          if (selected) provider.setCategory(label);
        },
        selectedColor: AppColors.primary,
        labelStyle: GoogleFonts.poppins(
          fontSize: 12,
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
          color: isSelected ? Colors.white : Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
        ),
        backgroundColor: AppColors.surfaceVariant,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        showCheckmark: false,
      ),
    );
  }

  Widget _buildMainContent(MarketProvider provider) {
    if (provider.isLoading) {
      return _buildShimmerLoading();
    }

    if (provider.isServerDown) {
      return _buildServerDownState(provider);
    }

    if (provider.myCropPrices.isEmpty && provider.otherPrices.isEmpty) {
      return _buildEmptyState();
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (provider.hasPlantedCrops) ...[
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Text(
              'Live Prices for Your Crops',
              style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface),
            ),
          ),
          if (provider.myCropPrices.isNotEmpty)
            ...provider.myCropPrices.map((p) => MarketCard(price: p))
          else
            Container(
              padding: const EdgeInsets.all(16),
              margin: const EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: AppColors.surfaceVariant,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline_rounded, color: AppColors.primary, size: 24),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'No live market data is currently available for your specific crops in your state today. Try checking back tomorrow!',
                      style: GoogleFonts.poppins(fontSize: 13, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                    ),
                  ),
                ],
              ),
            ),
          const SizedBox(height: 16),
        ],
        if (provider.otherPrices.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Text(
              'Other Nearby Markets',
              style: GoogleFonts.poppins(fontSize: 16, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface),
            ),
          ),
          ...provider.otherPrices.map((p) => MarketCard(price: p)),
        ],
      ],
    );
  }

  Widget _buildShimmerLoading() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 5,
      itemBuilder: (context, index) {
        return Shimmer.fromColors(
          baseColor: Colors.grey[300]!,
          highlightColor: Colors.grey[100]!,
          child: Container(
            margin: const EdgeInsets.only(bottom: 16),
            height: 120,
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              borderRadius: BorderRadius.circular(24),
            ),
          ),
        );
      },
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.search_off_rounded, size: 80, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5)),
          const SizedBox(height: 16),
          Text(
            'No markets found',
            style: GoogleFonts.poppins(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Try searching for another crop or market',
            style: GoogleFonts.poppins(fontSize: 14, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
          ),
        ],
      ),
    );
  }

  Widget _buildServerDownState(MarketProvider provider) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.cloud_off_rounded, size: 80, color: Colors.red.shade400),
            const SizedBox(height: 16),
            Text(
              'Server is down',
              style: GoogleFonts.poppins(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.8),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'The government Mandi API server is currently unreachable. Please try again later.',
              textAlign: TextAlign.center,
              style: GoogleFonts.poppins(
                fontSize: 14,
                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => provider.fetchPrices(forceRefresh: true),
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showSortBottomSheet(BuildContext context, MarketProvider provider) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Container(
          padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Sort By',
                style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 16),
              _sortTile(context, provider, 'Highest Price', MarketSortBy.priceHigh, Icons.arrow_upward_rounded),
              _sortTile(context, provider, 'Lowest Price', MarketSortBy.priceLow, Icons.arrow_downward_rounded),
              _sortTile(context, provider, 'Nearest Market', MarketSortBy.distance, Icons.near_me_rounded),
              _sortTile(context, provider, 'Best Trending', MarketSortBy.trend, Icons.trending_up_rounded),
              _sortTile(context, provider, 'My State First', MarketSortBy.state, Icons.map_rounded),
            ],
          ),
        );
      },
    );
  }

  Widget _sortTile(BuildContext context, MarketProvider provider, String label, MarketSortBy value, IconData icon) {
    final isSelected = provider.sortBy == value;
    return ListPadding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: ListTile(
        leading: Icon(icon, color: isSelected ? AppColors.primary : Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
        title: Text(
          label,
          style: GoogleFonts.poppins(
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
            color: isSelected ? AppColors.primary : Theme.of(context).colorScheme.onSurface,
          ),
        ),
        trailing: isSelected ? const Icon(Icons.check_circle_rounded, color: AppColors.primary) : null,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        tileColor: isSelected ? AppColors.primary.withValues(alpha: 0.1) : null,
        onTap: () {
          provider.setSortBy(value);
          Navigator.pop(context);
        },
      ),
    );
  }
}

class ListPadding extends StatelessWidget {
  final Widget child;
  final EdgeInsets padding;
  const ListPadding({super.key, required this.child, required this.padding});
  @override
  Widget build(BuildContext context) => Padding(padding: padding, child: child);
}
