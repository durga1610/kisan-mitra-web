import 'package:flutter/foundation.dart';

class ApiConfig {
  ApiConfig._();

  // OpenWeather API Key
  static const String openWeatherApiKey = String.fromEnvironment('OPENWEATHER_API_KEY', defaultValue: 'YOUR_OPENWEATHER_API_KEY');

  static const String geminiApiKey = String.fromEnvironment('GEMINI_API_KEY', defaultValue: 'YOUR_GEMINI_API_KEY');

  // Gemini model for text-only tasks
  static const String geminiModel = 'gemini-2.5-flash';
  
  // Gemini model for vision/image tasks
  static const String geminiVisionModel = 'gemini-2.5-flash';

  // Custom AI Backend URL
  // Default to 10.0.2.2:8000 for Android emulator, or http://localhost:8000 for web/iOS
  static String get customAiBackendUrl {
    const customUrl = String.fromEnvironment('CUSTOM_AI_BACKEND_URL');
    if (customUrl.isNotEmpty) return customUrl;
    if (kIsWeb) return 'http://localhost:8000';
    return 'http://10.0.2.2:8000';
  }

  // Mandi (Market) Data API — data.gov.in (Ministry of Agriculture)
  static const String mandiApiKey = String.fromEnvironment('MANDI_API_KEY', defaultValue: 'YOUR_MANDI_API_KEY'); 
  static const String mandiApiBaseUrl = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070';

  // Toggle to completely disable Firebase Storage upload/download attempts
  static const bool enableFirebaseStorage = bool.fromEnvironment('ENABLE_FIREBASE_STORAGE', defaultValue: false);

  // AI Assistant System Prompt
  static const String assistantSystemPrompt = '''
You are "Kisan Mitra AI", a highly professional agricultural assistant for Indian farmers.
Your goal is to provide concise, direct, and context-aware answers to the farmer's questions.

CRITICAL: Keep your response short and answer the question directly. Do NOT include any unwanted sections, templates (like Farm Analysis, Risk Assessment, Weather Impact, Confidence Score), boilerplate introduction, or unrelated information unless the user explicitly asks for a full report or analysis. For example, if a user asks a simple question (e.g., "best crop for red soil"), answer with the recommended crops and a brief explanation in 1-2 sentences.
''';
}
