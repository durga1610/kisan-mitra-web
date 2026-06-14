import 'dart:io';
import 'package:google_generative_ai/google_generative_ai.dart';

void main() async {
  final apiKey = 'AIzaSyDmktbHbZnqqP7WqCAW3VxngR1Ag29XkjA';
  final m = 'gemini-2.0-flash';
  
  try {
    print('Trying $m with chat history...');
    final model = GenerativeModel(model: m, apiKey: apiKey);
    final chat = model.startChat(history: [
      Content.text('You are an AI.'),
      Content.model([TextPart('Understood.')]),
    ]);
    final response = await chat.sendMessage(Content.text('Hi'));
    print('Success: ${response.text}');
  } catch (e) {
    print('Failed: $e');
  }
}
