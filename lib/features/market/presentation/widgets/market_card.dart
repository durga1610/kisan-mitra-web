import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../../core/constants/app_colors.dart';
import '../../data/models/market_price.dart';
import 'price_trend_chart.dart';
import '../../../../core/localization/app_translations.dart';

class MarketCard extends StatefulWidget {
  final MarketPrice price;

  const MarketCard({super.key, required this.price});

  @override
  State<MarketCard> createState() => _MarketCardState();
}

class _MarketCardState extends State<MarketCard> with SingleTickerProviderStateMixin {
  bool _expanded = false;
  late AnimationController _controller;
  late Animation<double> _expandAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 350),
    );
    _expandAnimation = CurvedAnimation(parent: _controller, curve: Curves.easeInOutCubic);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _toggleExpand() {
    setState(() => _expanded = !_expanded);
    if (_expanded) {
      _controller.forward();
    } else {
      _controller.reverse();
    }
  }

  Color get _weatherColor {
    switch (widget.price.weatherImpact) {
      case 'Positive':
        return AppColors.success;
      case 'Negative':
        return Colors.red;
      default:
        return Colors.orange;
    }
  }

  IconData get _weatherIcon {
    switch (widget.price.weatherImpact) {
      case 'Positive':
        return Icons.wb_sunny_rounded;
      case 'Negative':
        return Icons.cloud_outlined;
      default:
        return Icons.wb_cloudy_outlined;
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool isUp = widget.price.trendPercentage >= 0;
    final trendColor = isUp ? AppColors.success : Colors.red;

    return GestureDetector(
      onTap: _toggleExpand,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        margin: const EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(24),
          border: widget.price.isBestPrice
              ? Border.all(color: AppColors.primary, width: 2)
              : Border.all(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5).withValues(alpha: 0.08)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.06),
              blurRadius: 16,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          children: [
            // ── Header Row ──────────────────────────────────────────────────
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    children: [
                      // Crop Icon
                      Container(
                        width: 52,
                        height: 52,
                        decoration: BoxDecoration(
                          color: AppColors.primary.withValues(alpha: 0.08),
                          shape: BoxShape.circle,
                        ),
                        alignment: Alignment.center,
                        child: Text(widget.price.cropIcon, style: const TextStyle(fontSize: 26)),
                      ),
                      const SizedBox(width: 14),

                      // Crop & Market Info
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Flexible(
                                  child: Text(
                                    widget.price.cropName.tr(context),
                                    style: GoogleFonts.poppins(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w700,
                                      color: Theme.of(context).colorScheme.onSurface,
                                    ),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                if (widget.price.isBestPrice) ...[
                                  const SizedBox(width: 6),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: AppColors.primary,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Text(
                                      'BEST PRICE',
                                      style: GoogleFonts.poppins(
                                        fontSize: 8,
                                        fontWeight: FontWeight.w800,
                                        color: Colors.white,
                                      ),
                                    ),
                                  ),
                                ],
                              ],
                            ),
                            Text(
                              widget.price.marketName.tr(context),
                              style: GoogleFonts.poppins(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
                              ),
                            ),
                            Row(
                              children: [
                                Icon(Icons.location_on_outlined, size: 11, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                                const SizedBox(width: 3),
                                Expanded(
                                  child: Text(
                                    '${widget.price.location} • ${widget.price.distance} km',
                                    style: GoogleFonts.poppins(fontSize: 10, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),

                      // Price Info
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          AnimatedSwitcher(
                            duration: const Duration(milliseconds: 400),
                            transitionBuilder: (child, anim) => ScaleTransition(scale: anim, child: child),
                            child: Text(
                              '₹${widget.price.modalPrice.toInt()}',
                              key: ValueKey<double>(widget.price.modalPrice),
                              style: GoogleFonts.poppins(
                                fontSize: 22,
                                fontWeight: FontWeight.w800,
                                color: AppColors.primary,
                              ),
                            ),
                          ),
                          Text('Modal Price'.tr(context), style: GoogleFonts.poppins(fontSize: 9, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
                          const SizedBox(height: 4),
                          AnimatedSwitcher(
                            duration: const Duration(milliseconds: 300),
                            child: Row(
                              key: ValueKey<double>(widget.price.trendPercentage),
                              children: [
                                Icon(
                                  isUp ? Icons.trending_up_rounded : Icons.trending_down_rounded,
                                  size: 14,
                                  color: trendColor,
                                ),
                                const SizedBox(width: 3),
                                Text(
                                  '${widget.price.trendPercentage.abs().toStringAsFixed(1)}%',
                                  style: GoogleFonts.poppins(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w700,
                                    color: trendColor,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),

                  // ── Min / Max / Modal Row ──────────────────────────────────
                  Row(
                    children: [
                      Expanded(child: _priceTag('Min', '₹${widget.price.minPrice.toInt()}', Colors.red.shade400)),
                      Expanded(child: _priceTag('Modal', '₹${widget.price.modalPrice.toInt()}', AppColors.primary)),
                      Expanded(child: _priceTag('Max', '₹${widget.price.maxPrice.toInt()}', AppColors.success)),
                      const SizedBox(width: 4),
                      // Weather Impact Badge
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: _weatherColor.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Row(
                          children: [
                            Icon(_weatherIcon, size: 12, color: _weatherColor),
                            const SizedBox(width: 4),
                            Text(
                              widget.price.weatherImpact,
                              style: GoogleFonts.poppins(fontSize: 10, fontWeight: FontWeight.w600, color: _weatherColor),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      AnimatedRotation(
                        turns: _expanded ? 0.5 : 0,
                        duration: const Duration(milliseconds: 300),
                        child: Icon(Icons.keyboard_arrow_down_rounded, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // ── Expandable Section ───────────────────────────────────────────
            SizeTransition(
              sizeFactor: _expandAnimation,
              child: Container(
                decoration: BoxDecoration(
                  color: AppColors.background,
                  borderRadius: const BorderRadius.vertical(bottom: Radius.circular(24)),
                ),
                padding: const EdgeInsets.fromLTRB(16, 4, 16, 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Divider(height: 24),

                    // Price Trend Chart
                    PriceTrendChart(price: widget.price),
                    const SizedBox(height: 20),

                    // AI Insight
                    _buildInsightSection(
                      icon: Icons.auto_awesome_rounded,
                      color: Colors.deepPurple,
                      label: 'AI Insight',
                      content: widget.price.aiAdvice,
                    ),
                    const SizedBox(height: 12),

                    // Best Time To Sell
                    _buildInsightSection(
                      icon: Icons.schedule_rounded,
                      color: Colors.teal,
                      label: 'Best Time to Sell',
                      content: widget.price.bestTimeToSell,
                    ),
                    const SizedBox(height: 20),

                    // Updated Time
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _liveTag(),
                        Text(
                          'Updated just now',
                          style: GoogleFonts.poppins(fontSize: 10, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _priceTag(String label, String value, Color color) {
    return Column(
      children: [
        Text(label, style: GoogleFonts.poppins(fontSize: 9, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7))),
        Text(
          value,
          style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.w700, color: color),
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }

  Widget _buildInsightSection({
    required IconData icon,
    required Color color,
    required String label,
    required String content,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, size: 16, color: color),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: GoogleFonts.poppins(fontSize: 10, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                ),
                Text(
                  content,
                  style: GoogleFonts.poppins(fontSize: 13, fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.onSurface),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _liveTag() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: Colors.red.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 5,
            height: 5,
            decoration: const BoxDecoration(color: Colors.red, shape: BoxShape.circle),
          ),
          const SizedBox(width: 4),
          Text(
            'LIVE',
            style: GoogleFonts.poppins(fontSize: 9, fontWeight: FontWeight.w800, color: Colors.red),
          ),
        ],
      ),
    );
  }
}
