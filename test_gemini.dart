import 'package:google_generative_ai/google_generative_ai.dart';

void main() async {
  const apiKey = 'AIzaSyDmktbHbZnqqP7WqCAW3VxngR1Ag29XkjA';
  for (final name in ['gemini-2.5-flash', 'gemini-3.5-flash', 'gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-2.0-flash']) {
    try {
      print('Testing $name...');
      final model = GenerativeModel(model: name, apiKey: apiKey);
      final response = await model.generateContent([Content.text('Say hi')]);
      print('  SUCCESS: ${response.text}\n');
    } catch (e) {
      final msg = e.toString().split('\n').first;
      print('  FAILED: $msg\n');
    }
  }
}
