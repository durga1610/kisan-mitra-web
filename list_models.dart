import 'dart:convert';
import 'package:http/http.dart' as http;

void main() async {
  final apiKey = 'AIzaSyDmktbHbZnqqP7WqCAW3VxngR1Ag29XkjA';
  final url = Uri.parse('https://generativelanguage.googleapis.com/v1beta/models?key=$apiKey');

  print('Fetching available models for this API key...');
  try {
    final response = await http.get(url);
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final models = data['models'] as List;
      print('\nSUCCESS! Supported Models for this key:');
      for (var model in models) {
        if (model['supportedGenerationMethods']?.contains('generateContent') == true) {
          final name = model['name'];
          print('- $name');
        }
      }
    } else {
      print('FAILED! Status Code: ${response.statusCode}');
      print('Response: ${response.body}');
    }
  } catch (e) {
    print('Error: $e');
  }
}
