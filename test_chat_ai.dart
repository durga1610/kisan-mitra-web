import 'package:google_generative_ai/google_generative_ai.dart';

void main() async {
  const apiKey = 'AIzaSyDmktbHbZnqqP7WqCAW3VxngR1Ag29XkjA';

  print('=== Test 1: Chat with system prompt in history (gemini-3.5-flash) ===');
  try {
    final model = GenerativeModel(
      model: 'gemini-3.5-flash',
      apiKey: apiKey,
    );

    final chat = model.startChat(history: [
      Content.text(
        'You are "Kisan Mitra AI", a specialized agricultural assistant for Indian farmers. '
        'Provide accurate, practical, and localized advice. '
        'The user\'s farm: Location: Nagulapadu, Prakasam, Andhra Pradesh. '
        'Soil Type: Alluvial. Water: High. Planted Crops: Hybrid Cotton.',
      ),
      Content.model([
        TextPart('Understood. I am Kisan Mitra AI, your personalized agricultural assistant. How can I help you today?'),
      ]),
    ]);

    final response = await chat.sendMessage(
      Content.text('What is the best crop to plant in sandy loam soil during Kharif season?'),
    );

    print('  CHAT SUCCESS!');
    print('  Response: ${response.text}\n');
  } catch (e) {
    print('  CHAT FAILED: $e\n');
  }

  print('=== Test 2: Recommendation reasoning (gemini-3.5-flash) ===');
  try {
    final model2 = GenerativeModel(
      model: 'gemini-3.5-flash',
      apiKey: apiKey,
    );
    final prompt = 'You are an expert AI agronomist. The farmer is considering growing Mango in Andhra Pradesh. '
        'Current weather: Clouds, 41.4°C, Zaid season. '
        'Soil type: Alluvial. Water availability: High. '
        'Market data for Mango: prices trending up 2%. '
        'In exactly ONE sentence of max 20 words, explain why Mango is a smart choice right now.';

    final response = await model2.generateContent([Content.text(prompt)]);
    print('  REASONING SUCCESS!');
    print('  Response: ${response.text}\n');
  } catch (e) {
    print('  REASONING FAILED: $e\n');
  }

  print('=== Test 3: Disease detection prompt (gemini-3.5-flash) ===');
  try {
    final model3 = GenerativeModel(
      model: 'gemini-3.5-flash',
      apiKey: apiKey,
    );
    final response = await model3.generateContent([
      Content.text('Describe common symptoms of cotton bollworm infestation in 2 sentences.'),
    ]);
    print('  DISEASE DETECTION SUCCESS!');
    print('  Response: ${response.text}\n');
  } catch (e) {
    print('  DISEASE DETECTION FAILED: $e\n');
  }

  print('=== All tests complete ===');
}
