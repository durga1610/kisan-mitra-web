import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:go_router/go_router.dart';
import '../../../../config/routes/app_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/localization/app_translations.dart';

class _QuickAction {
  final String label;
  final IconData icon;
  final Color color;
  final Color bgColor;
  final String? route;

  const _QuickAction({
    required this.label,
    required this.icon,
    required this.color,
    required this.bgColor,
    this.route,
  });
}

class QuickActionsGrid extends StatelessWidget {
  const QuickActionsGrid({super.key});

  static const _actions = [
    _QuickAction(
      label: 'AI Assistant',
      icon: Icons.auto_awesome_outlined,
      color: Color(0xFF2E7D32),
      bgColor: Color(0xFFE8F5E9),
      route: AppRouter.aiAssistant,
    ),
    _QuickAction(
      label: 'Scan Disease',
      icon: Icons.document_scanner_outlined,
      color: Color(0xFF7B1FA2),
      bgColor: Color(0xFFF3E5F5),
      route: AppRouter.diseaseDetection,
    ),

    _QuickAction(
      label: 'Fertilizer',
      icon: Icons.grass_rounded,
      color: AppColors.secondary,
      bgColor: AppColors.secondaryContainer,
      route: AppRouter.fertilizer, // Dedicated fertilizer screen
    ),
    _QuickAction(
      label: 'Weather',
      icon: Icons.cloud_outlined,
      color: AppColors.sky,
      bgColor: AppColors.skyContainer,
      route: AppRouter.weatherDashboard,
    ),
    _QuickAction(
      label: 'Market',
      icon: Icons.storefront_outlined,
      color: Color(0xFFC2185B),
      bgColor: Color(0xFFFCE4EC),
      route: AppRouter.market,
    ),
    _QuickAction(
      label: 'AI Advisory',
      icon: Icons.support_agent_rounded,
      color: Color(0xFF1976D2),
      bgColor: Color(0xFFE3F2FD),
      route: AppRouter.aiAdvisory,
    ),
    _QuickAction(
      label: 'Profit',
      icon: Icons.account_balance_wallet_outlined,
      color: Color(0xFFE65100),
      bgColor: Color(0xFFFFF3E0),
      route: AppRouter.profitAnalyzer,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    final crossAxisCount = width > 900 ? 6 : (width > 600 ? 4 : 3);
    final childAspectRatio = width > 900 ? 2.2 : (width > 600 ? 1.8 : 1.75);

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: childAspectRatio,
      ),
      itemCount: _actions.length,
      itemBuilder: (context, index) {
        final action = _actions[index];
        return _QuickActionTile(action: action);
      },
    );
  }
}

class _QuickActionTile extends StatefulWidget {
  final _QuickAction action;
  const _QuickActionTile({required this.action});

  @override
  State<_QuickActionTile> createState() => _QuickActionTileState();
}

class _QuickActionTileState extends State<_QuickActionTile>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 120),
      lowerBound: 0.92,
      upperBound: 1.0,
      value: 1.0,
    );
    _scale = _controller;
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) => _controller.reverse(),
      onTapUp: (_) => _controller.forward(),
      onTapCancel: () => _controller.forward(),
      onTap: () {
        if (widget.action.route != null) {
          context.push(widget.action.route!);
        }
      },
      child: ScaleTransition(
        scale: _scale,
        child: Container(
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.05),
                blurRadius: 10,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: widget.action.bgColor,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  widget.action.icon,
                  color: widget.action.color,
                  size: 18,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                widget.action.label.tr(context),
                style: GoogleFonts.poppins(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).colorScheme.onSurface,
                ),
                textAlign: TextAlign.center,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
