# Kisan Mitra: Architectural Analysis & Local AI Migration Technical Report

This technical report presents a complete architectural breakdown of the **Kisan Mitra** project and outlines a comprehensive technical design to replace all Gemini API dependencies with a **100% locally trained, dataset-driven Machine Learning & AI system**.

---

## 1. Project Overview

### Overall Architecture
Kisan Mitra is built as a multi-platform smart agriculture system. It follows a decoupled client-server architecture with a mobile/web frontend connected to a cloud database (Firebase) and a custom Python backend (FastAPI).

```
┌─────────────────────────────────────────────────────────┐
│                    Flutter Client                       │
│        (Mobile / Web - Provider State Management)       │
└──────────────┬───────────────────────────┬──────────────┘
               │                           │
               ▼                           ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│    Firebase Cloud         │ │   FastAPI Python Backend  │
│  (Auth, Firestore, FCM)   │ │   (Render / Port 8000)    │
└───────────────────────────┘ └────────────┬──────────────┘
                                           │
                                           ▼
                              ┌───────────────────────────┐
                              │  Local Datasets & ML      │
                              │  (ONNX / PyTorch / SQLite)│
                              └───────────────────────────┘
```

* **Frontend Technology**: Flutter 3.x with Dart, GoRouter navigation (`lib/config/routes/app_router.dart`), Provider for state management, Google Fonts, OpenWeatherMap integration, and data.gov.in Mandi integration.
* **Backend Technology**: Python 3.11 with FastAPI (`backend/main.py`), PyTorch, SQLite database (`backend/kisan_mitra.db`), and Uvicorn server hosted on Render.
* **Firebase Services**: Firebase Authentication (Email/Password, Google Auth), Cloud Firestore (NoSQL database), Firebase Storage (optional file uploads), Firebase Cloud Messaging (FCM alerts).
* **State Management**: Provider pattern using dedicated ChangeNotifiers:
  - [auth_provider.dart](file:///c:/Users/durga/kisan_mitra/lib/core/providers/auth_provider.dart)
  - [user_provider.dart](file:///c:/Users/durga/kisan_mitra/lib/core/providers/user_provider.dart)
  - [farm_provider.dart](file:///c:/Users/durga/kisan_mitra/lib/core/providers/farm_provider.dart)
  - [language_provider.dart](file:///c:/Users/durga/kisan_mitra/lib/core/providers/language_provider.dart)
  - [market_provider.dart](file:///c:/Users/durga/kisan_mitra/lib/features/market/presentation/providers/market_provider.dart)
  - [profit_provider.dart](file:///c:/Users/durga/kisan_mitra/lib/features/profit_analyzer/presentation/providers/profit_provider.dart)

### Folder Structure
```
kisan_mitra/
├── lib/
│   ├── config/             # App routing (app_router.dart)
│   ├── core/
│   │   ├── config/         # API configs (api_config.dart)
│   │   ├── constants/      # App colors, strings, themes
│   │   ├── localization/   # Multilingual translations (AppTranslations)
│   │   ├── models/         # Core data models (UserModel, FarmModel, RecommendationModel)
│   │   ├── providers/      # Application state providers
│   │   ├── repositories/   # Data access repositories (Market, Advisory, Weather, Farm)
│   │   └── services/       # External service callers (Auth, Weather, Location, Gemini)
│   └── features/           # Feature modules
│       ├── advisory/       # AI Advisory & Fertilizer calculator
│       ├── ai_assistant/   # Conversational Chatbot interface
│       ├── auth/           # Login & Auth screens
│       ├── crop_recommendation/ # Soil/Climate recommendation feature
│       ├── crops/          # Farm & crop management UI
│       ├── home/           # Dashboard shell & quick action grid
│       ├── market/         # Real-time Mandi price viewer
│       ├── notifications/  # Alert history & notification management
│       ├── profile/        # User profile, settings, farm manager
│       ├── profile_setup/  # First-time onboarding screen
│       ├── profit_analyzer/ # Financial yield & profit calculations
│       ├── splash/         # App initialization & splash screen
│       └── weather/        # Weather forecast & dashboard
├── backend/                # Python FastAPI Backend
│   ├── main.py             # FastAPI entry point & API endpoints
│   ├── setup_database.py   # SQLite schema initialization
│   ├── services/           # Backend services (recommendation_engine.py, fertilizer_engine.py, gemini_fallback.py)
│   └── documents/          # Agricultural text domain knowledge documents
```

---

## 2. Firebase Analysis

### List of Firebase Services Used
1. **Firebase Authentication**: Email/Password authentication and Google Sign-In via `FirebaseAuth`.
2. **Cloud Firestore**: Real-time NoSQL database used to store profiles, farms, recommendations, and chat histories.
3. **Firebase Storage**: Stores user avatar images and uploaded farm media (governed by `ApiConfig.enableFirebaseStorage`).
4. **Firebase Cloud Messaging (FCM)**: Delivers notification topics (`weather`, `market`, `irrigation`).

### Firestore Collections & Document Structures

#### Collection: `users`
* **Document ID**: User UID (`FirebaseAuth.currentUser.uid`)
* **Fields**:
  - `uid` (String): User unique identifier
  - `name` (String): Farmer full name
  - `email` (String): Email address
  - `phone` (String): Phone number
  - `state` (String): State name (e.g., "Maharashtra")
  - `district` (String): District name (e.g., "Pune")
  - `language` (String): Selected language code (e.g., "en", "hi", "te")
  - `createdAt` (Timestamp): Creation timestamp
  - `updatedAt` (Timestamp): Last update timestamp

#### Collection: `farms`
* **Document ID**: Auto-generated document ID or custom Farm ID
* **Fields**:
  - `id` (String): Farm ID
  - `uid` (String): Owner user UID
  - `name` (String): Farm name (e.g., "North Field")
  - `area` (double): Farm land area
  - `areaUnit` (String): Unit ("Acres", "Hectares", "Bigha")
  - `soilType` (String): Soil classification ("Black", "Red", "Alluvial", "Clay", "Loamy", "Sandy")
  - `location` (String): Location address / village name
  - `irrigationType` (String): Irrigation method ("Drip", "Sprinkler", "Canal", "Rainfed", "Borewell")
  - `crops` (List<String>): List of currently cultivated crops
  - `createdAt` (Timestamp): Creation date
  - `updatedAt` (Timestamp): Modification date

#### Collection: `crop_recommendations`
* **Document ID**: Auto-generated
* **Fields**:
  - `uid` (String): Owner user UID
  - `cropName` (String): Recommended crop name
  - `confidence` (double): Confidence score (0.0 - 1.0)
  - `factors` (List<String>): Environmental matching factors
  - `createdAt` (Timestamp): Timestamp of recommendation request

#### Collection: `chat_sessions`
* **Document ID**: Auto-generated session ID
* **Fields**:
  - `sessionId` (String): Session ID
  - `userId` (String): Owner user UID
  - `title` (String): Topic summary of conversation
  - `messages` (Array of Maps): 
    - `role` (String): `"user"` or `"assistant"`
    - `content` (String): Text message
    - `timestamp` (String/Timestamp)
  - `createdAt` (Timestamp)
  - `updatedAt` (Timestamp)

#### Collection: `user_preferences`
* **Document ID**: User UID
* **Fields**:
  - `uid` (String): Owner user UID
  - `autoBackup` (bool): Preference toggle
  - `marketAlertCrops` (List<String>): Selected crops for market alerts

### Models Mapped to Firestore
* [UserModel](file:///c:/Users/durga/kisan_mitra/lib/core/models/user_model.dart): `fromMap()`, `toMap()`
* [FarmModel](file:///c:/Users/durga/kisan_mitra/lib/core/models/farm_model.dart): `fromMap()`, `toMap()`
* [RecommendationModel](file:///c:/Users/durga/kisan_mitra/lib/core/models/recommendation_model.dart): `fromMap()`, `toMap()`

### Data Flow between Flutter and Firebase
```
Flutter UI Screen
  └── Provider Call (e.g., UserProvider / FarmProvider)
        └── Service / Repository Call (FirestoreService / AuthService)
              └── Firebase SDK (cloud_firestore / firebase_auth)
                    └── Firebase Cloud
```
Flutter screens consume `UserProvider` and `FarmProvider`. Updates perform asynchronous writes to Firestore via `FirestoreService`, and Firestore streams auto-update the UI via Provider listener callbacks.

---

## 3. Existing AI Features

| Feature Name | Primary Purpose | Current Implementation Mechanism | Key Files Involved |
| :--- | :--- | :--- | :--- |
| **AI Assistant** | Conversational chat for farmer questions | Direct call to **Gemini API** (`gemini-2.5-flash`) via `GeminiService` or backend endpoint `/api/v1/advisory/chat` | `ai_assistant_screen.dart`, `gemini_service.dart`, `advisory_repository.dart`, `backend/services/gemini_fallback.py` |
| **AI Advisory** | Customized crop guidance reports | **Gemini API** with fallback to backend local domain rule templates | `ai_advisory_screen.dart`, `advisory_repository.dart`, `backend/services/gemini_fallback.py` |
| **Fertilizer Engine** | Recommended NPK dosage & schedule | **Rule-based calculation engine** (`fertilizer_engine.py`) with Gemini fallback for unsupported crops | `fertilizer_screen.dart`, `backend/services/fertilizer_engine.py`, `backend/services/gemini_fallback.py` |
| **Crop Recommendation** | Soil & climate suitability matching | **Rule-based matrix** in Flutter repository & Python backend (`recommendation_engine.py`) matching soil type, state, and season | `crop_recommendation_screen.dart`, `recommendation_repository.dart`, `backend/services/recommendation_engine.py` |
| **Profit Analyzer** | Financial yield and net profit estimation | **Mathematical formula model** calculating total yield × market price minus input costs | `profit_analyzer_screen.dart`, `profit_provider.dart`, `new_profit_record_screen.dart` |

---

## 4. Gemini API Analysis

### Inventory of Gemini API References
1. **Service Classes**:
   - [lib/core/services/gemini_service.dart](file:///c:/Users/durga/kisan_mitra/lib/core/services/gemini_service.dart): Implements `getResponse()` to send raw HTTP requests to Google Gemini REST endpoint `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`.
   - `backend/services/gemini_fallback.py`: Python high-availability Gemini manager with a 6-key rotation pool (`GEMINI_API_KEY_1`..`6`), usage logging, and SQLite caching.

2. **Repositories**:
   - [lib/core/repositories/advisory_repository.dart](file:///c:/Users/durga/kisan_mitra/lib/core/repositories/advisory_repository.dart): Orchestrates AI responses, calling `GeminiService` or fallback routes.

3. **Screens**:
   - [lib/features/ai_assistant/presentation/screens/ai_assistant_screen.dart](file:///c:/Users/durga/kisan_mitra/lib/features/ai_assistant/presentation/screens/ai_assistant_screen.dart): Renders chat UI and triggers `GeminiService.getResponse()`.
   - [lib/features/advisory/presentation/screens/ai_advisory_screen.dart](file:///c:/Users/durga/kisan_mitra/lib/features/advisory/presentation/screens/ai_advisory_screen.dart): Sends farmer profile & prompt to Gemini for detailed advisory generation.

4. **Configuration Files**:
   - [lib/core/config/api_config.dart](file:///c:/Users/durga/kisan_mitra/lib/core/config/api_config.dart): Declares `geminiApiKey`, `geminiModel`, and `assistantSystemPrompt`.

### Request & Response Flow of Gemini API
```
[User Input in AIAssistantScreen]
       │
       ▼
[GeminiService.getResponse(message)]
       │
       ├─────────────────────────────────────────┐
       ▼ (Direct REST Mode)                      ▼ (Backend Proxy Mode)
[Google Gemini REST API Endpoint]      [FastAPI Endpoint /api/v1/advisory/chat]
https://generativelanguage.googleapis       │
  .com/v1beta/models/gemini-2.5-flash       ▼
       │                               [GeminiKeyManager in gemini_fallback.py]
       │                                    │  (Checks SQLite response cache)
       │                                    ▼  (Rotates KEY_1..KEY_6 on 429 rate limit)
       │                               [Google Gemini REST API]
       ▼                                    │
[JSON Response: candidates[0].text]         ▼
       │                               [JSON Response + Source metadata]
       └────────────────────────────────────┘
       │
       ▼
[Rendered markdown message in Flutter UI]
```

---

## 5. Current Features Implementation

1. **Farmer Registration**: `LoginScreen` handles phone/email authentication using `AuthService`. New users are redirected to `ProfileSetupScreen` to collect name, state, district, and preferred language, saving a `UserModel` document in Firestore (`users`).
2. **Farm Management**: Managed via `ManageFarmsScreen`, `EditFarmScreen`, and `FarmProvider`. Farmers add land area, soil type, irrigation type, and active crops. Data is saved in Firestore (`farms`).
3. **Weather Feature**: `WeatherScreen` and `WeeklyForecastScreen` call `WeatherService` -> `WeatherRepository`. Queries OpenWeatherMap API using farm coordinates, showing current conditions and 5-day forecast.
4. **Market Price Feature**: `MarketScreen` calls `MarketRepository`. Fetches commodity price data from `data.gov.in` Mandi resource API based on state and district filter.
5. **AI Assistant**: `AIAssistantScreen` provides an interactive chat interface. User prompts are sent to `GeminiService` or backend advisory endpoints and stored in Firestore `chat_sessions`.
6. **AI Advisory**: `AIAdvisoryScreen` generates comprehensive farming reports by assembling user state, soil type, farm crops, and local weather into a structured prompt sent to Gemini or local rule fallback.
7. **Crop Recommendation**: `CropRecommendationScreen` collects soil type, region/state, and season. Calls `RecommendationRepository` to filter crops against an internal knowledge matrix.
8. **Authentication**: Handled by `AuthService` and `AuthProvider` using `firebase_auth`. Manages login, logout, password resets, and session tokens.
9. **User Profile**: `ProfileScreen` displays farmer credentials, active farms, app settings, and language selection.

---

## 6. Data Models

### 1. `UserModel` ([user_model.dart](file:///c:/Users/durga/kisan_mitra/lib/core/models/user_model.dart))
* **Fields**: `uid` (String), `name` (String), `email` (String), `phone` (String), `state` (String), `district` (String), `language` (String), `createdAt` (DateTime).
* **Purpose**: Represents the farmer's account and location profile.
* **Relationships**: Parent object; owns 1-to-N `FarmModel` instances and 1-to-N Firestore `chat_sessions`.

### 2. `FarmModel` ([farm_model.dart](file:///c:/Users/durga/kisan_mitra/lib/core/models/farm_model.dart))
* **Fields**: `id` (String), `uid` (String), `name` (String), `area` (double), `areaUnit` (String), `soilType` (String), `location` (String), `irrigationType` (String), `crops` (List<String>), `createdAt` (DateTime).
* **Purpose**: Stores land specs, soil classification, and crop choices for a specific farm.
* **Relationships**: Belongs to `UserModel` (`uid`). Referenced by recommendation and advisory services.

### 3. `WeatherModel` ([weather_model.dart](file:///c:/Users/durga/kisan_mitra/lib/features/weather/data/models/weather_model.dart))
* **Fields**: `temperature` (double), `minTemp` (double), `maxTemp` (double), `humidity` (int), `description` (String), `windSpeed` (double), `cityName` (String), `iconCode` (String), `forecastList` (List<DailyForecast>).
* **Purpose**: Formats external OpenWeatherMap payload into clean UI primitives.
* **Relationships**: Standalone data transfer object (DTO) associated with current farm location coordinates.

### 4. `MarketModel` ([market_model.dart](file:///c:/Users/durga/kisan_mitra/lib/features/market/data/models/market_model.dart))
* **Fields**: `state` (String), `district` (String), `market` (String), `commodity` (String), `variety` (String), `minPrice` (double), `maxPrice` (double), `modalPrice` (double), `arrivalDate` (String).
* **Purpose**: Represents Mandi market price records.
* **Relationships**: Standalone DTO filtered by `UserModel.state` and `UserModel.district`.

### 5. `RecommendationModel` ([recommendation_model.dart](file:///c:/Users/durga/kisan_mitra/lib/core/models/recommendation_model.dart))
* **Fields**: `cropName` (String), `confidence` (double), `matchingFactors` (List<String>), `description` (String).
* **Purpose**: Holds output from crop recommendation engines.
* **Relationships**: Linked to user session; saved in Firestore `crop_recommendations`.

---

## 7. Services Summary

| Service Class | File Location | Responsibility |
| :--- | :--- | :--- |
| `AuthService` | `lib/core/services/auth_service.dart` | Handles Firebase Authentication (sign in, sign up, Google login, password reset, auth tokens). |
| `FirestoreService` | `lib/core/services/firestore_service.dart` | Executes raw Firestore CRUD operations for user profiles, farm records, and user preferences. |
| `GeminiService` | `lib/core/services/gemini_service.dart` | Communicates directly with Google Gemini REST API. *(Target for replacement)* |
| `WeatherService` | `lib/core/services/weather_service.dart` | Calls OpenWeatherMap REST API to retrieve current weather & forecast. |
| `LocationService` | `lib/core/services/location_service.dart` | Interacts with device GPS to obtain latitude, longitude, and geocoded address. |
| `SessionService` | `lib/core/services/session_service.dart` | Manages local session caching and secure storage. |
| `StorageService` | `lib/core/services/storage_service.dart` | Manages Firebase Storage uploads for user avatar images. |
| `recommendation_engine.py` | `backend/services/recommendation_engine.py` | Python backend service for evaluating crop suitability matrices. |
| `fertilizer_engine.py` | `backend/services/fertilizer_engine.py` | Python backend NPK fertilizer calculator engine. |

---

## 8. APIs

| External API | Purpose | Endpoint | Auth | Calling Files | Target Screens |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenWeatherMap** | Live weather & 5-day forecast | `https://api.openweathermap.org/data/2.5/weather`<br>`https://api.openweathermap.org/data/2.5/forecast` | API Key (`appid`) | `weather_service.dart` | `HomeScreen`, `WeatherScreen`, `WeeklyForecastScreen` |
| **data.gov.in Mandi API** | Commodity market prices | `https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070` | API Key (`api-key`) | `market_repository.dart` | `MarketScreen` |
| **Google Gemini REST API** | AI chat & advisory | `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent` | API Key (`key`) | `gemini_service.dart`, `gemini_fallback.py` | `AIAssistantScreen`, `AIAdvisoryScreen` *(To be replaced)* |
| **Custom FastAPI Backend** | Machine learning & analytical endpoints | `https://kisan-mitra-backend-p21a.onrender.com` / `http://10.0.2.2:8000` | Firebase Bearer Token | `gemini_service.dart`, `advisory_repository.dart` | `AIAdvisoryScreen`, `FertilizerScreen`, `CropRecommendationScreen` |

---

## 9. Screens Inventory

| Screen Name | File Location | Purpose | Dependencies |
| :--- | :--- | :--- | :--- |
| **SplashScreen** | `splash_screen.dart` | App initialization & session validation | `AuthProvider`, GoRouter |
| **LoginScreen** | `login_screen.dart` | User authentication interface | `AuthService`, `AuthProvider`, Firebase Auth |
| **HomeScreen** | `home_screen.dart` | Dashboard hub & quick action launcher | `UserProvider`, `FarmProvider`, `WeatherService` |
| **CropsScreen** | `crops_screen.dart` | View and manage crops for active farms | `FarmProvider`, `FirestoreService` |
| **MarketScreen** | `market_screen.dart` | Real-time commodity market prices | `MarketRepository`, data.gov.in API |
| **WeatherScreen** | `weather_screen.dart` | Detailed current weather metrics | `WeatherService`, Location GPS |
| **WeeklyForecastScreen** | `weekly_forecast_screen.dart` | 5 to 7 day weather forecast | `WeatherService`, `WeatherModel` |
| **AIAssistantScreen** | `ai_assistant_screen.dart` | Conversational farming assistant | `GeminiService` *(Replace with Local RAG)* |
| **AIAdvisoryScreen** | `ai_advisory_screen.dart` | Personalized farming advice report | `AdvisoryRepository` *(Replace with Local ML)* |
| **FertilizerScreen** | `fertilizer_screen.dart` | NPK fertilizer requirement calculator | `backend/fertilizer_engine.py` |
| **CropRecommendationScreen** | `crop_recommendation_screen.dart` | Soil & environment crop matcher | `RecommendationRepository` |
| **ProfitAnalyzerScreen** | `profit_analyzer_screen.dart` | Yield & income calculator | `ProfitProvider` |
| **NewProfitRecordScreen** | `new_profit_record_screen.dart` | Add financial transaction record | `ProfitProvider` |
| **ProfileScreen** | `profile_screen.dart` | Farmer account management | `UserProvider`, `AuthService`, Firebase |
| **ProfileSetupScreen** | `profile_setup_screen.dart` | First-time farmer registration onboarding | `UserProvider`, `FirestoreService` |
| **ManageFarmsScreen** | `manage_farms_screen.dart` | List, add, and remove farm plots | `FarmProvider`, `FirestoreService` |
| **EditFarmScreen** | `edit_farm_screen.dart` | Modify existing farm plot parameters | `FarmProvider` |
| **EditProfileScreen** | `edit_profile_screen.dart` | Update farmer contact & region details | `UserProvider` |
| **SettingsScreen** | `settings_screen.dart` | Manage app preferences, language & sync | `SharedPreferences`, `UserProvider` |

---

## 10. Architecture Flow Diagram

```
                       ┌─────────────────────────┐
                       │     Flutter UI Layer    │
                       │   (Screens & Widgets)   │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │   State Provider Layer  │
                       │ (User, Farm, Auth, etc) │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │    Repository Layer     │
                       │(Market, Advisory, Farm) │
                       └─────┬─────────────┬─────┘
                             │             │
              ┌──────────────┘             └──────────────┐
              ▼                                           ▼
┌───────────────────────────┐               ┌───────────────────────────┐
│     Services Layer        │               │   FastAPI Python Backend  │
│(Weather, Auth, Firestore) │               │   (ML Models & Local RAG) │
└─────────────┬─────────────┘               └─────────────┬─────────────┘
              │                                           │
              ▼                                           ▼
┌───────────────────────────┐               ┌───────────────────────────┐
│     Firebase Cloud        │               │  Local Datasets & ONNX    │
│  (Auth, Firestore, FCM)   │               │ (Crop_recommendation.csv) │
└───────────────────────────┘               └───────────────────────────┘
```

---

## 11. Crop Recommendation ML Model Integration Plan

To integrate a machine learning crop recommendation model trained on `Crop_recommendation.csv` (containing 2,200 rows with columns `N`, `P`, `K`, `temperature`, `humidity`, `ph`, `rainfall`, and target `label` across 22 crops):

```
                       Crop_recommendation.csv
                                  │
                                  ▼
                     [Train Random Forest / XGBoost]
                                  │
                                  ▼
                   [Export to ONNX Format (.onnx)]
                                  │
                                  ▼
             ┌────────────────────┴────────────────────┐
             ▼                                         ▼
   [FastAPI Backend Host]                    [Local Flutter Host]
backend/models/crop_rec.onnx               onnxruntime Flutter Plugin
             │                                         │
             ▼                                         ▼
 Endpoint: POST /api/v1/crop-rec/predict     Offline In-App Inference
```

### Recommendation Strategy
1. **Model Training & Export**:
   - Train a **Random Forest Classifier** or **XGBoost Classifier** in Python using Scikit-Learn.
   - Convert the trained model to **ONNX format** (`crop_recommendation.onnx`) using `skl2onnx` for lightweight, zero-dependency inference.
2. **Backend Service Integration**:
   - Save `crop_recommendation.onnx` inside `backend/models/`.
   - Create a dedicated FastAPI service endpoint: `POST /api/v1/recommendation/predict`.
   - The endpoint receives `{ N, P, K, temperature, humidity, ph, rainfall }` as input, executes ONNX inference using `onnxruntime`, and returns the top 3 recommended crops with probability scores.
3. **Flutter Client Integration**:
   - Flutter collects soil test parameters (`N`, `P`, `K`, `pH`) on `CropRecommendationScreen`.
   - Automatically populates `temperature`, `humidity`, and `rainfall` using current farm location data from `WeatherService`.
   - Calls `RecommendationRepository.predictCrop(params)`, sending a request to the FastAPI ML endpoint and rendering interactive crop recommendation cards with confidence percentages.

---

## 12. Local AI Assistant Replacement Architecture (Zero Gemini API)

To permanently replace Gemini API with a 100% dataset-driven local AI assistant, implement a **Retrieval-Augmented Generation (RAG)** pipeline.

```
 Farmer Query ("How to treat yellow leaves in sugarcane?")
                         │
                         ▼
        [SentenceTransformers Embedding Engine]
               (all-MiniLM-L6-v2 - 384 dim)
                         │
                         ▼
             [Vector Search Engine]
         (FAISS / SQLite Vector Search)
                         │
                         ▼
        [Retrieved Top-K Knowledge Chunks]
    (From local agricultural manuals dataset)
                         │
                         ▼
          [Local Small Language Model (SLM)]
     (Llama-3.2-1B-Instruct / Qwen2.5-1.5B via llama.cpp)
                         │
                         ▼
         [Grounding Verification & Response]
                         │
                         ▼
             [Flutter AIAssistantScreen]
```

### Architectural Breakdown
1. **Knowledge Base Location**: Store domain-specific agricultural manuals, regional farming guides, pesticide safety databases, and crop calendars as structured text/markdown documents inside `backend/documents/` and index them into an SQLite database (`backend/rag_knowledge.db`).
2. **Embedding Storage**: Use an offline embedding model like `SentenceTransformers (all-MiniLM-L6-v2)` (384-dimensional vector embeddings, footprint < 90MB). Store embeddings in a **FAISS** index (`backend/vector_index.faiss`) or directly in SQLite using vector extensions.
3. **Retrieval Process**: When a farmer submits a chat query, compute its vector embedding and perform cosine similarity search against the FAISS index to retrieve the top 3-5 most relevant knowledge snippets.
4. **Response Generation**: Pass the retrieved knowledge snippets into a small, quantized local SLM (such as **Llama-3.2-1B-Instruct-Q4** or **Qwen2.5-1.5B-Instruct-Q4**) using `llama-cpp-python` or ONNX Runtime. The model synthesizes a concise, grounded answer based strictly on the retrieved context.
5. **Conversation Memory**: Chat sessions continue to be persisted in Firestore under `chat_sessions/{sessionId}`, preserving message history without cloud AI dependency.

---

## 13. Personalized AI Advisory Workflow

The personalized AI advisory module will combine farmer profile data, real-time environment metrics, local market trends, and ML predictions into a unified pipeline:

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Farmer Profile  │  │  Current Farm   │  │  Live Weather   │
│(State, District)│  │ (Soil, Area, NPK)│  │(Temp, Rain, Hum)│
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
           ┌─────────────────────────────────────┐
           │   Local Decision Engine Integrator  │
           └──────────────────┬──────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    ▼                         ▼                         ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ ML Crop Rec   │     │ NPK Fertilizer│     │ Market Trend  │
│ (ONNX Model)  │     │ (Rule Engine) │     │ (Mandi API)   │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
           ┌─────────────────────────────────────┐
           │ Personalized Farming Advice Synthesizer │
           └──────────────────┬──────────────────┘
                              │
                              ▼
           ┌─────────────────────────────────────┐
           │ Structured Advisory Output Rendered │
           │         in AIAdvisoryScreen         │
           └─────────────────────────────────────┘
```

### Complete Execution Steps
1. **Data Gathering**: Fetch `UserModel` (State, District), active `FarmModel` (Soil Type, Irrigation, Current Crops), and live `WeatherModel` for farm coordinates.
2. **ML Crop Recommendation**: Execute the local ONNX ML model to determine the optimal crop choice for the current soil and weather conditions.
3. **NPK Fertilizer Schedule Calculation**: Calculate exact nitrogen, phosphorus, and potassium dosage requirements based on soil type and selected crop using `fertilizer_engine.py`.
4. **Market Opportunity Evaluation**: Query local Mandi market prices for the recommended crops to evaluate current market trends and profitability potential.
5. **Advisory Synthesis**: Assemble the combined metrics into a structured, localized advisory report with irrigation schedules, pest alerts, and fertilizer application timings.

---

## 14. Future AI Architecture (Zero Paid APIs)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Kisan Mitra Flutter Frontend                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Local AI Server                         │
│                                                                        │
│   ┌────────────────────────┐  ┌────────────────────────────────────┐   │
│   │ Crop Recommendation ML │  │      Local RAG AI Assistant       │   │
│   │   (ONNX Random Forest) │  │  (MiniLM + FAISS + Llama 1B SLM)   │   │
│   └────────────────────────┘  └────────────────────────────────────┘   │
│   ┌────────────────────────┐  ┌────────────────────────────────────┐   │
│   │ NPK Fertilizer Engine  │  │   Personalized Advisory Engine     │   │
│   │     (Rule-Based ML)    │  │ (Profile + Weather + Market Fusion)│   │
│   └────────────────────────┘  └────────────────────────────────────┘   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         Local Database Storage                         │
│         (SQLite kisan_mitra.db & FAISS Vector Store index.faiss)       │
└────────────────────────────────────────────────────────────────────────┘
```

* **Crop Recommendation**: ONNX Machine Learning model trained on `Crop_recommendation.csv` executing locally on CPU.
* **AI Assistant**: Offline RAG pipeline using `SentenceTransformers` embeddings, FAISS vector search, and a quantized 1B/1.5B Small Language Model (SLM) executing on CPU/GPU via `llama-cpp-python`.
* **Personalized AI Advisory**: Algorithmic fusion of soil data, weather metrics, market pricing, and local ML predictions.
* **Cost & Dependency**: 100% free, zero external LLM API keys required, zero rate limits.

---

## 15. Implementation Roadmap

### Phase 1: Machine Learning Crop Recommendation Model
* Clean and preprocess `Crop_recommendation.csv`.
* Train a Scikit-Learn **Random Forest Classifier** achieving >98% accuracy.
* Export trained model to `backend/models/crop_recommendation.onnx`.
* Create FastAPI endpoint `POST /api/v1/recommendation/predict`.
* Update [recommendation_repository.dart](file:///c:/Users/durga/kisan_mitra/lib/core/repositories/recommendation_repository.dart) to call the ONNX endpoint.

### Phase 2: Local RAG Knowledge Base Construction
* Aggregate domain knowledge documents (crop protection guides, fertilizer handbooks) into `backend/documents/`.
* Chunk documents and generate 384-dim embeddings using `SentenceTransformers (all-MiniLM-L6-v2)`.
* Build and persist FAISS index `backend/vector_index.faiss`.

### Phase 3: Gemini API Deprecation & RAG Endpoint Activation
* Install `llama-cpp-python` and download quantized `Llama-3.2-1B-Instruct-Q4.gguf` model into `backend/models/`.
* Create FastAPI endpoint `POST /api/v1/assistant/chat` implementing vector retrieval + SLM synthesis.
* Remove [gemini_service.dart](file:///c:/Users/durga/kisan_mitra/lib/core/services/gemini_service.dart) and `backend/services/gemini_fallback.py`.
* Update [ai_assistant_screen.dart](file:///c:/Users/durga/kisan_mitra/lib/features/ai_assistant/presentation/screens/ai_assistant_screen.dart) and [ai_advisory_screen.dart](file:///c:/Users/durga/kisan_mitra/lib/features/advisory/presentation/screens/ai_advisory_screen.dart) to connect to local RAG endpoints.

### Phase 4: Verification & Performance Optimization
* Run load testing to verify local inference throughput on standard CPU hardware.
* Ensure Flutter UI gracefully handles offline fallback states when local server is unreachable.
