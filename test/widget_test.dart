import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kisan_mitra/main.dart';

void main() {
  testWidgets('KisanMitra app smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const KisanMitraApp());
    await tester.pump();
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
