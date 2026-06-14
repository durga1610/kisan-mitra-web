import 'dart:io';
import 'package:google_generative_ai/google_generative_ai.dart';

void main() async {
  final apiKey = 'AIzaSyDmktbHbZnqqP7WqCAW3VxngR1Ag29XkjA';
  final models = [
    'gemini-3.5-flash',
    'gemini-flash-latest',
    'gemini-2.5-flash'
  ];
  
  for (final m in models) {
    try {
      print('Trying $m...');
      final model = GenerativeModel(model: m, apiKey: apiKey);
      final response = await model.generateContent([Content.text('Hello. Please respond with exactly "Hi".')]);
      print('Success with $m: ${response.text}');
      exit(0);
    } catch (e) {
      print('Failed with $m: $e');
    }
  }
}
