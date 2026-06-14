import 'package:google_generative_ai/google_generative_ai.dart';

void main() async {
  const apiKey = 'AIzaSyDmktbHbZnqqP7WqCAW3VxngR1Ag29XkjA';

  // Test using gemini-2.5-flash (which passed earlier and has separate quota)
  print('=== Test 1: Chat with embedded system prompt (gemini-2.5-flash) ===');
  try {
    final model = GenerativeModel(
      model: 'gemini-2.5-flash',
      apiKey: apiKey,
    );

    final chat = model.startChat(history: [
      Content.text('You are "Kisan Mitra AI", a specialized agricultural assistant for Indian farmers. '
          'Your goal is to provide accurate, practical, and localized advice on crops, fertilizers, pests, '
          'irrigation, and market trends. Always be polite, helpful, and use simple language.'),
      Content.model([TextPart('Understood. I am Kisan Mitra AI, your personalized agricultural assistant. How can I help you today?')]),
    ]);

    final response = await chat.sendMessage(Content.text('What fertilizer should I use for wheat?'));
    final text = response.text ?? '';
    print('  SUCCESS (${text.length} chars): ${text.substring(0, text.length.clamp(0, 300))}...');
    print('');
  } catch (e) {
    print('  FAILED: $e');
    print('');
  }

  // Test 2: Recommendation reasoning
  print('=== Test 2: Recommendation reasoning (gemini-2.5-flash) ===');
  try {
    final model = GenerativeModel(
      model: 'gemini-2.5-flash',
      apiKey: apiKey,
    );

    final prompt = 'You are an expert AI agronomist. The farmer is considering growing Mango in Andhra Pradesh. '
        'Current weather: Clear, 38.5°C, Summer season. Soil type: Red soil. Water availability: Medium. '
        'In exactly ONE sentence of max 20 words, explain why Mango is a smart choice right now. '
        'Be specific about market or weather. Do NOT use asterisks or markdown.';

    final response = await model.generateContent([Content.text(prompt)]);
    print('  SUCCESS: ${response.text}');
    print('');
  } catch (e) {
    print('  FAILED: $e');
    print('');
  }

  print('=== All tests complete ===');
}
