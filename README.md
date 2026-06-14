# 🌾 Kisan Mitra (Farmer's Friend)

<div align="center">
  <img src="https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white" alt="Flutter" />
  <img src="https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black" alt="Firebase" />
  <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini" />
  <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel" />
</div>

<br>

**Kisan Mitra** is a modern, AI-powered agricultural application designed to empower farmers with real-time data, intelligent agronomic guidance, and seamless farm management tools. Built entirely on a highly scalable Serverless Architecture, it bridges the gap between technology and traditional farming.

🌐 **Live Web App:** [https://kisan-mitra-seven.vercel.app](https://kisan-mitra-seven.vercel.app)

---

## ✨ Key Features

- 🤖 **AI-Powered Agronomist:** Integrated directly with the **Google Gemini API** to provide personalized, context-aware daily crop guidance and visual disease detection (via camera/image upload).
- 📊 **Real-Time Market Prices:** Fetches live APMC (Mandi) market data directly from the **Government of India API (`data.gov.in`)**. Includes intelligent filtering to prioritize local state markets ("My State First").
- 🌦️ **Dynamic Weather & Alerts:** Real-time localized weather tracking and extreme weather alerts based on the farmer's registered location.
- 🌍 **Full Localization:** Complete multi-lingual support, allowing farmers to interact with the app in their native language for maximum accessibility.
- 🚜 **Multi-Crop Management:** Allows tracking and managing multiple crops simultaneously with isolated tracking timelines and automated health assessments.

---

## 🏛️ System Architecture

Kisan Mitra utilizes a modern **Serverless Architecture** to ensure zero maintenance downtime, high scalability, and extreme cost-efficiency. 

* **Frontend (Client):** Developed in **Flutter / Dart**. Compiled natively for Android (APK) and the Web.
* **Backend (BaaS):** Powered completely by **Google Firebase**.
  * *Firebase Authentication:* Secure user login and session management.
  * *Cloud Firestore:* NoSQL real-time database for storing farm configurations, crop data, and user preferences.
* **Direct Microservices Integration:**
  * To minimize latency, the Flutter client connects directly to third-party APIs (Gemini, Gov API, OpenWeather) without a middleman server, ensuring ultra-fast data retrieval.

---

## 🚀 Getting Started (Local Development)

Follow these steps to run the project locally on your machine.

### Prerequisites
- [Flutter SDK](https://docs.flutter.dev/get-started/install) (latest stable version)
- Node.js (Optional, for Vercel CLI deployment)
- A Firebase Project (with Auth and Firestore enabled)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/kisan-mitra.git
   cd kisan_mitra
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure API Keys**
   - Ensure your Firebase `google-services.json` (Android) and `firebase_options.dart` are correctly configured.
   - Update the API endpoints for Gemini and `data.gov.in` in your environment config file.

4. **Run the App**
   ```bash
   # To run on Web
   flutter run -d chrome

   # To run on an Android emulator or connected device
   flutter run
   ```

---

## 📦 Deployment

### Web (Vercel)
The web version of Kisan Mitra is hosted on Vercel. To deploy an update:
```bash
# Build the production web files
flutter build web --release

# Navigate to the output directory and deploy
cd build/web
vercel --prod
```
*Note: Make sure to whitelist your Vercel URL in the Firebase Authentication console (Authorized Domains).*

### Mobile (Android)
To generate a production-ready APK for Android devices:
```bash
flutter build apk --release
```
The generated APK will be located at `build/app/outputs/flutter-apk/app-release.apk`.

---

<div align="center">
  <i>Built with ❤️ for Farmers</i>
</div>
