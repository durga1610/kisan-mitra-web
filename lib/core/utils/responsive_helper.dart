import 'package:flutter/material.dart';

class ResponsiveHelper {
  static late MediaQueryData _mediaQueryData;
  static late double screenWidth;
  static late double screenHeight;
  static late double blockSizeHorizontal;
  static late double blockSizeVertical;
  static late double safeAreaHorizontal;
  static late double safeAreaVertical;
  static late double safeBlockHorizontal;
  static late double safeBlockVertical;
  static late double textScaleFactor;
  static late bool isTablet;
  static late bool isPhone;

  static void init(BuildContext context) {
    _mediaQueryData = MediaQuery.of(context);
    screenWidth = _mediaQueryData.size.width;
    screenHeight = _mediaQueryData.size.height;
    blockSizeHorizontal = screenWidth / 100;
    blockSizeVertical = screenHeight / 100;
    safeAreaHorizontal =
        _mediaQueryData.padding.left + _mediaQueryData.padding.right;
    safeAreaVertical =
        _mediaQueryData.padding.top + _mediaQueryData.padding.bottom;
    safeBlockHorizontal = (screenWidth - safeAreaHorizontal) / 100;
    safeBlockVertical = (screenHeight - safeAreaVertical) / 100;
    textScaleFactor = _mediaQueryData.textScaler.scale(1.0);
    isTablet = screenWidth > 600;
    isPhone = screenWidth <= 600;
  }

  static double wp(double percent) => blockSizeHorizontal * percent;
  static double hp(double percent) => blockSizeVertical * percent;
  static double sp(double size) => isTablet ? size * 1.2 : size;

  static EdgeInsets get screenPadding =>
      isTablet ? const EdgeInsets.all(32) : const EdgeInsets.all(20);

  static int get gridCrossAxisCount => isTablet ? 3 : 2;
}
