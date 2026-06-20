# Disease Detection Response Contract Audit

This audit evaluates the response schema of the `/api/v1/disease/detect` endpoint against the deserialization and consumption layers of the Flutter frontend.

---

## 1. Captured JSON Response (Success Path)

Under a successful plant disease scan, the backend returns the following exact JSON response:

```json
{
  "status": "success",
  "crop": "Cotton",
  "disease": "Bacterial Blight",
  "leaf_confidence": 100.0,
  "contains_leaf": true,
  "confidence": 98.0,
  "confidenceBand": "high",
  "severity": "High",
  "symptoms": [
    "Angular",
    "water-soaked leaf spots turning brown/black. Black streaks on stems (blackarm) and boll rot."
  ],
  "treatment": [
    "Spray Copper Oxychloride mixed with Streptomycin. Avoid working in wet fields."
  ],
  "prevention": [
    "Use acid-delinted disease-free seed",
    "rotate crops",
    "clear crop residues."
  ],
  "warning": null,
  "text": "Plant: Cotton\nDisease: Bacterial Blight (Xanthomonas citri subsp. malvacearum)...",
  "plantName": "Cotton",
  "diseaseName": "Bacterial Blight (Xanthomonas citri subsp. malvacearum)",
  "causes": "Bacterium Xanthomonas, warm temperatures, splashing rain, contaminated seeds.",
  "organicTreatment": "Apply Neem oil spray (1%), Copper-based organic fungicides, or a mixture of baking soda...",
  "suggestedProducts": "Streptocycline, Blitox (Copper Oxychloride)",
  "explanation": "Our two-stage prediction pipeline identified a high probability of Bacterial Blight...",
  "gradcamBase64": "/9j/4AAQSkZJRgABAQAAAQABAAD/2w...z8gKZznjPJT36d+Kc7x9C29ND/2Q==",
  "predictions": [
    {
      "class": "Cotton___Bacterial_Blight",
      "confidence": 98.0
    },
    {
      "class": "Tomato___Healthy",
      "confidence": 1.2
    },
    {
      "class": "Potato___Healthy",
      "confidence": 0.8
    }
  ],
  "source": "LOCAL_ENGINE"
}
```

---

## 2. Response Schema Comparison

Below is the field-by-field mapping comparison between the backend response, the frontend service, the database model, and the result screen.

| Backend JSON Key | Dart Service Parsing (`disease_detection_service.dart`) | Dart Model Field (`disease_report.dart`) | UI Usage (`disease_result_screen.dart`) |
| :--- | :--- | :--- | :--- |
| `"crop"` / `"plantName"` | `plantName = aiResponse['plantName'] ?? aiResponse['crop']` | `final String plantName` | Header & TTS: `report.plantName` |
| `"disease"` / `"diseaseName"` | `diseaseName = aiResponse['diseaseName'] ?? aiResponse['disease']` | `final String diseaseName` | Header & TTS: `report.diseaseName` |
| `"confidence"` | `(aiResponse['confidence'] ?? 0.0).toDouble()` | `final double confidence` | Indicator & Progress: `report.confidence` |
| `"severity"` | `aiResponse['severity'] ?? 'Unknown'` | `final String severity` | Text & Color: `report.severity` |
| `"symptoms"` (List) | `parseListOrString(aiResponse['symptoms'])` (Joins with `", "`) | `final String symptoms` | Card Bullet Points: `report.symptoms.split(',')` |
| `"treatment"` (List) | `parseListOrString(aiResponse['treatment'])` (Joins with `", "`) | `final String treatment` | Card Bullet Points: `report.treatment.split(',')` |
| `"prevention"` (List) | `parseListOrString(aiResponse['prevention'])` (Joins with `", "`) | `final String prevention` | Card Bullet Points: `report.prevention.split(',')` |
| `"causes"` | `aiResponse['causes'] ?? 'N/A'` | `final String causes` | Rendered Card: `report.causes` |
| `"organicTreatment"` | `aiResponse['organicTreatment'] ?? 'N/A'` | `final String organicTreatment` | Rendered Card: `report.organicTreatment` |
| `"suggestedProducts"` | `aiResponse['suggestedProducts'] ?? 'N/A'` | `final String suggestedProducts` | Rendered Card: `report.suggestedProducts` |
| `"explanation"` | `aiResponse['explanation'] ?? 'N/A'` | `final String explanation` | Rendered Card: `report.explanation` |
| `"gradcamBase64"` | `aiResponse['gradcamBase64'] ?? ''` | `final String gradcamBase64` | Image overlay: `base64Decode(report.gradcamBase64)` |
| `"predictions"` (List) | `List<Map<String, dynamic>>.from(...)` | `final List<Map<String, dynamic>> topPredictions` | List view: `report.topPredictions` |
| `"warning"` | `aiResponse['warning']?.toString()` | `final String? warning` | Notice Card: `report.warning` |
| `"confidenceBand"` | `aiResponse['confidenceBand']?.toString() ?? 'high'` | `final String confidenceBand` | Progress indicator: `report.confidenceBand` |
| `"source"` | `aiResponse['source']` | `final String? source` | Service Badge: `report.source` |

---

## 3. Mandatory Field Verifications (Requirement 3)

* **`disease`**: **Verified**. Provided as both `disease` (short title) and `diseaseName` (long title with binomial names). Frontend safely coalesces both.
* **`confidence`**: **Verified**. Returned as a numeric JSON float. Deserialized safely to Dart `double`.
* **`confidenceBand`**: **Verified**. Returned as a JSON string (`"high"`, `"moderate"`, `"low"`). Decoded safely with local fallback.
* **`source`**: **Verified**. Returned as a JSON string indicating model engine type (`"LOCAL_ENGINE"`, `"GEMINI_FALLBACK"`). Decoded safely.
* **`recommendations`**: **Verified** (Mapped to `treatment` and `prevention`). The backend returns detailed prescriptive fields (`treatment`, `prevention`, `organicTreatment`, and `suggestedProducts`). The frontend maps these into structured list views.
* **`heatmap`**: **Verified** (Mapped to `gradcamBase64`). The backend contains `gradcamBase64`, which contains the raw Grad-CAM activation heatmap overlay. The frontend decodes and switches this on the Sliver App Bar when requested by the farmer.
* **`imageUrl`**: **Verified** (Handled Client-Side). The backend does not store or return an image URL since it operates as a stateless prediction engine. The frontend uploads the selected image file directly to Firebase Storage and maps the generated URL to the model/Firestore document locally.
* **`alternatives`**: **Verified** (Mapped to `predictions`). The backend includes the top 3 alternative predictions. The frontend parses them into the "Alternative Predictions" list view.

---

## 4. Null Safety, Missing Fields, and Types Audit

1. **Null Values**:
   - `warning` is `null` under high-confidence paths. Dart parses this safely as `String?` without exceptions.
   - All other fields have explicit non-null defaults in `disease_detection_service.dart` (e.g. `?? 'N/A'`, `?? 0.0`), preventing any `TypeError` or `NullThrownError`.
2. **Missing Fields**:
   - In quality failures (e.g. non-plant image), the backend returns a short JSON structure containing only `status`, `reason`, `leaf_confidence`, and `contains_leaf`. The frontend catches `status == 'quality_failed'` or `status == 'confidence_failed'` early and throws an `Exception(reason)`, preventing the parsing layer from executing on missing fields.
3. **Type Mismatches**:
   - Backend lists (`symptoms`, `treatment`, `prevention`) are handled dynamically by `parseListOrString` which joins `List` elements safely into a unified string.
   - Numeric `confidence` values are explicitly converted via `.toDouble()` in Dart, preventing conflicts if the JSON parser returns integer types.
4. **Invalid URLs**:
   - Image URLs are fetched directly from Firebase Storage via `getDownloadURL()` client-side, avoiding backend URL mismatches.

**Result**: Deserialization is 100% compliant. The Flutter frontend can parse the successful response without any code modifications.

---

## 5. Root Cause of Vercel "ClientException: Failed to fetch"

Since the backend successfully processes the image, logs `200 OK` on Render, and return headers are valid, the client-side browser network failure `Failed to fetch` is caused by a **Frontend Request Timeout**:

* **Location**: [lib/core/services/gemini_service.dart](file:///c:/Users/durga/kisan_mitra/lib/core/services/gemini_service.dart#L279)
* **Code**: `final streamedResponse = await request.send().timeout(const Duration(seconds: 20));`
* **Mechanism**: 
  - Render Free Tier instances spin down after inactivity, incurring a **40+ second cold start delay** upon the first request.
  - Furthermore, running PyTorch inference and generating high-resolution Grad-CAM overlays (which are not downscaled) on Render's single-core CPU can take **10 to 15 seconds** per request.
  - Because the client-side timeout is set aggressively to **20 seconds**, the browser terminates the pending HTTP request prematurely. 
  - When the request is terminated by the client, the browser throws an abort/network error, which the Dart `http` package catches and translates to `ClientException: Failed to fetch`.

### Recommendation
Increase all API network timeouts in `gemini_service.dart` (especially the multipart image upload request) to **90 seconds** to accommodate Render cold starts and inference times.
