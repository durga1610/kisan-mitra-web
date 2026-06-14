import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../../core/constants/app_colors.dart';
import '../../data/models/market_price.dart';

class PriceTrendChart extends StatelessWidget {
  final MarketPrice price;

  const PriceTrendChart({super.key, required this.price});

  @override
  Widget build(BuildContext context) {
    if (price.historicalPrices.isEmpty) return const SizedBox.shrink();

    final prices = price.historicalPrices;
    final minY = prices.reduce((a, b) => a < b ? a : b) * 0.97;
    final maxY = prices.reduce((a, b) => a > b ? a : b) * 1.03;

    final spots = prices
        .asMap()
        .entries
        .map((e) => FlSpot(e.key.toDouble(), e.value))
        .toList();

    final isUpTrend = prices.last >= prices.first;
    final trendColor = isUpTrend ? AppColors.success : Colors.red;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              '7-Day Price Trend',
              style: GoogleFonts.poppins(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7),
              ),
            ),
            const Spacer(),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: trendColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(
                    isUpTrend ? Icons.trending_up_rounded : Icons.trending_down_rounded,
                    size: 12,
                    color: trendColor,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    isUpTrend ? 'Rising' : 'Falling',
                    style: GoogleFonts.poppins(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: trendColor,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 120,
          child: LineChart(
            LineChartData(
              gridData: FlGridData(
                show: true,
                drawVerticalLine: false,
                horizontalInterval: (maxY - minY) / 3,
                getDrawingHorizontalLine: (value) => FlLine(
                  color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5).withValues(alpha: 0.15),
                  strokeWidth: 1,
                ),
              ),
              titlesData: FlTitlesData(
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 52,
                    getTitlesWidget: (value, meta) => Text(
                      '₹${value.toInt()}',
                      style: GoogleFonts.poppins(fontSize: 9, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                    ),
                  ),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    getTitlesWidget: (value, meta) {
                      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                      final idx = value.toInt();
                      if (idx < 0 || idx >= days.length) return const SizedBox.shrink();
                      return Text(
                        days[idx],
                        style: GoogleFonts.poppins(fontSize: 9, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.7)),
                      );
                    },
                  ),
                ),
                topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              ),
              borderData: FlBorderData(show: false),
              minX: 0,
              maxX: (prices.length - 1).toDouble(),
              minY: minY,
              maxY: maxY,
              lineBarsData: [
                LineChartBarData(
                  spots: spots,
                  isCurved: true,
                  color: trendColor,
                  barWidth: 2.5,
                  isStrokeCapRound: true,
                  dotData: FlDotData(
                    show: true,
                    getDotPainter: (spot, percent, barData, index) {
                      if (index == prices.length - 1) {
                        // Highlight last (most recent) dot
                        return FlDotCirclePainter(
                          radius: 5,
                          color: trendColor,
                          strokeWidth: 2,
                          strokeColor: Colors.white,
                        );
                      }
                      return FlDotCirclePainter(
                        radius: 2,
                        color: trendColor.withValues(alpha: 0.5),
                        strokeWidth: 0,
                        strokeColor: Colors.transparent,
                      );
                    },
                  ),
                  belowBarData: BarAreaData(
                    show: true,
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        trendColor.withValues(alpha: 0.25),
                        trendColor.withValues(alpha: 0.0),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            duration: const Duration(milliseconds: 600),
          ),
        ),
      ],
    );
  }
}
