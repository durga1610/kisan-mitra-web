import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../constants/app_colors.dart';
import '../constants/app_dimensions.dart';

enum KMButtonVariant { primary, secondary, outline, ghost }
enum KMButtonSize { small, medium, large }

class KMButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final KMButtonVariant variant;
  final KMButtonSize size;
  final IconData? leadingIcon;
  final IconData? trailingIcon;
  final bool isLoading;
  final bool fullWidth;
  final Gradient? gradient;

  const KMButton({
    super.key,
    required this.label,
    this.onPressed,
    this.variant = KMButtonVariant.primary,
    this.size = KMButtonSize.medium,
    this.leadingIcon,
    this.trailingIcon,
    this.isLoading = false,
    this.fullWidth = true,
    this.gradient,
  });

  @override
  Widget build(BuildContext context) {
    final isDisabled = onPressed == null || isLoading;

    double height;
    double fontSize;
    EdgeInsets padding;
    switch (size) {
      case KMButtonSize.small:
        height = AppDimensions.buttonHeightSM;
        fontSize = 13;
        padding = const EdgeInsets.symmetric(horizontal: 16);
        break;
      case KMButtonSize.large:
        height = 60;
        fontSize = 17;
        padding = const EdgeInsets.symmetric(horizontal: 32);
        break;
      case KMButtonSize.medium:
        height = AppDimensions.buttonHeight;
        fontSize = 15;
        padding = const EdgeInsets.symmetric(horizontal: 24);
        break;
    }

    final textStyle = GoogleFonts.poppins(
      fontSize: fontSize,
      fontWeight: FontWeight.w600,
    );

    if (variant == KMButtonVariant.primary) {
      return SizedBox(
        width: fullWidth ? double.infinity : null,
        height: height,
        child: DecoratedBox(
          decoration: BoxDecoration(
            gradient: isDisabled
                ? null
                : (gradient ?? AppColors.primaryGradient),
            color: isDisabled ? AppColors.textHint : null,
            borderRadius: BorderRadius.circular(AppDimensions.buttonRadius),
            boxShadow: isDisabled
                ? null
                : [
                    BoxShadow(
                      color: AppColors.primary.withValues(alpha: 0.35),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ],
          ),
          child: ElevatedButton(
            onPressed: isDisabled ? null : onPressed,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.transparent,
              shadowColor: Colors.transparent,
              foregroundColor: AppColors.white,
              minimumSize: Size(fullWidth ? double.infinity : 0, height),
              padding: padding,
              shape: RoundedRectangleBorder(
                borderRadius:
                    BorderRadius.circular(AppDimensions.buttonRadius),
              ),
            ),
            child: _buildChild(AppColors.white, textStyle),
          ),
        ),
      );
    }

    if (variant == KMButtonVariant.outline) {
      return SizedBox(
        width: fullWidth ? double.infinity : null,
        height: height,
        child: OutlinedButton(
          onPressed: isDisabled ? null : onPressed,
          style: OutlinedButton.styleFrom(
            minimumSize: Size(fullWidth ? double.infinity : 0, height),
            padding: padding,
          ),
          child: _buildChild(AppColors.primary, textStyle),
        ),
      );
    }

    if (variant == KMButtonVariant.ghost) {
      return SizedBox(
        width: fullWidth ? double.infinity : null,
        height: height,
        child: TextButton(
          onPressed: isDisabled ? null : onPressed,
          style: TextButton.styleFrom(
            minimumSize: Size(fullWidth ? double.infinity : 0, height),
            padding: padding,
          ),
          child: _buildChild(AppColors.primary, textStyle),
        ),
      );
    }

    // Secondary
    return SizedBox(
      width: fullWidth ? double.infinity : null,
      height: height,
      child: ElevatedButton(
        onPressed: isDisabled ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.secondary,
          foregroundColor: AppColors.white,
          minimumSize: Size(fullWidth ? double.infinity : 0, height),
          padding: padding,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppDimensions.buttonRadius),
          ),
        ),
        child: _buildChild(AppColors.white, textStyle),
      ),
    );
  }

  Widget _buildChild(Color color, TextStyle textStyle) {
    if (isLoading) {
      return SizedBox(
        width: 22,
        height: 22,
        child: CircularProgressIndicator(
          strokeWidth: 2.5,
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
      );
    }
    return Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (leadingIcon != null) ...[
          Icon(leadingIcon, size: 18, color: color),
          const SizedBox(width: 8),
        ],
        Text(label, style: textStyle.copyWith(color: color)),
        if (trailingIcon != null) ...[
          const SizedBox(width: 8),
          Icon(trailingIcon, size: 18, color: color),
        ],
      ],
    );
  }
}
