# Kisan Mitra: Soil-Type Default Mapping Matrix Architecture & Upgrade Documentation

This document explains the technical implementation of **Strategy A (Soil-Type Default Mapping Matrix)** in `backend/advisory_engine.py` and provides a technical guide for future upgrades to direct soil chemistry data sources.

---

## 1. How the Soil Mapping Works

The backend feature extractor `extract_prediction_features(farm_ctx, weather_ctx)` accepts the farm context object containing the farmer's selected `soilType` string (e.g., `"Black Soil"`, `"Alluvial Soil"`, `"Red Soil"`).

The helper function `get_soil_default_values(soil_type)` inspects the soil type name and maps it to Indian agronomic baseline values for Nitrogen ($N$), Phosphorus ($P$), Potassium ($K$), and $pH$:

```
               FarmModel (soilType: "Black Soil")
                               │
                               ▼
            [get_soil_default_values("Black Soil")]
                               │
                               ▼
             ┌───────────────────────────────────┐
             │  N  = 50 kg/ha                    │
             │  P  = 55 kg/ha                    │
             │  K  = 50 kg/ha                    │
             │  pH = 7.5                         │
             └───────────────────────────────────┘
                               │
                               ▼
        [extract_prediction_features() Feature Vector]
   { N: 50, P: 55, K: 50, temp: 28.5, hum: 75.0, ph: 7.5, rain: 150.0 }
```

### Agronomic Baseline Matrix

| Soil Type Input | Nitrogen (N) | Phosphorus (P) | Potassium (K) | pH Level | Agronomic Baseline Rationale |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Alluvial Soil** | `80` | `50` | `45` | `6.8` | Highly fertile river-basin soil, balanced nutrients, near-neutral pH. |
| **Black Soil (Regur)** | `50` | `55` | `50` | `7.5` | Clay-rich basaltic soil, high potassium/calcium, slightly alkaline. |
| **Red Soil / Laterite** | `35` | `30` | `35` | `5.8` | Iron-rich porous soil, low organic nitrogen & phosphorus, acidic. |
| **Clay Soil** | `60` | `45` | `55` | `7.2` | High cation exchange capacity, retains potassium, neutral-alkaline. |
| **Loamy Soil** | `70` | `45` | `40` | `6.5` | Ideal agricultural mixture, optimal nutrient holding capacity. |
| **Sandy Soil** | `25` | `20` | `20` | `6.0` | Coarse texture, high leaching rates, low nutrient retention. |
| **Unknown / Unspecified** | `50` | `40` | `40` | `6.5` | Standard pan-Indian agricultural average fallback. |

---

## 2. Why Strategy A is Used

1. **Zero User Friction**: Farmers in rural India often do not know exact numerical NPK values (in kg/ha) or soil pH levels without lab testing. Soil mapping allows the app to function immediately using basic soil choices (`soilType`).
2. **Zero Flutter UI & Database Modifications**: Requires 0 changes to Flutter screens, 0 changes to Firebase Firestore schemas, and 0 API route signature changes.
3. **Exact Feature Vector Match**: Prepares the exact 7 numerical features (`N`, `P`, `K`, `temperature`, `humidity`, `ph`, `rainfall`) required by the trained Random Forest model.

---

## 3. Future Upgrade Pathways (Replacing Defaults with Real Data)

The `extract_prediction_features()` architecture is designed with a plugin fallback pattern, making future upgrades simple without breaking existing functionality:

```
                      Incoming Request (farm, weather)
                                     │
                                     ▼
                ┌────────────────────────────────────────┐
                │ Does farm_ctx contain explicit NPK/pH? │
                └───────────────┬────────────────┬───────┘
                                │ Yes            │ No
                                ▼                ▼
                      [User Soil Card]   ┌──────────────────────────────┐
                      (Direct N,P,K,pH)  │ Query SoilGrids / ICAR API   │
                                         └──────────────┬───────────────┘
                                                        │ Found?
                                                        ├─────────────┐
                                                        │ Yes         │ No (Fallback)
                                                        ▼             ▼
                                                [Regional Soil] [Strategy A Matrix]
                                                  (Location NPK) (Default Soil Mapping)
```

### Upgrade 1: User Soil Health Card Integration
- **Concept**: Add optional fields on `ManageFarmsScreen` (`soilNitrogen`, `soilPhosphorus`, `soilPotassium`, `soilPh`).
- **Backend Flow**: If `f_dict.get("soil_nitrogen")` is provided, use exact farmer values; if missing or `None`, fallback to `get_soil_default_values(soil_type)`.

### Upgrade 2: ISRIC SoilGrids REST API Integration
- **Concept**: Query the free ISRIC SoilGrids API (`https://rest.isric.org/soilgrids/v2.0/properties/query`) using farm `latitude` and `longitude`.
- **Returned Metrics**: Retrieves clay percentage, sand percentage, organic carbon (nitrogen proxy), and pH at 0-30cm depth globally.

### Upgrade 3: ICAR / Indian Soil Health Card (SHC) API Integration
- **Concept**: Connect to state/national Soil Health Card portal databases via district/village code lookups to fetch verified government soil testing laboratory results.
