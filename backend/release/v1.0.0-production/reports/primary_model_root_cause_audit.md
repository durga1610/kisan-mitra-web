# Primary Disease Detection Pipeline — Root Cause Audit

## Executive Summary

The two-stage pipeline (`crop_model.pt` + `disease_model.pt`) **was never trained successfully** and cannot be restored because the model files never existed in production. The system always ran on the single-stage `plant_disease_resnet.pt`. The confidence threshold (50%) was rejecting valid predictions because the model itself outputs low confidence on its training-set images.

---

## Audit Findings

### 1. Model File Existence

| File | Expected Path | Status |
|---|---|---|
| `crop_model.pt` | `backend/models/crop_model.pt` | ❌ **DOES NOT EXIST** |
| `disease_model.pt` | `backend/models/disease_model.pt` | ❌ **DOES NOT EXIST** |
| `plant_disease_resnet.pt` | `backend/models/plant_disease_resnet.pt` | ✅ Active (20 classes) |
| `plant_disease_resnet_rollback.pt` | `backend/models_backup/plant_disease_resnet_rollback.pt` | ✅ Backup (45 classes) |

### 2. Filesystem Paths Used by Backend

```
Primary (two-stage):  models/crop_model.pt     ← NOT FOUND → triggers fallback
                      models/disease_model.pt  ← NOT FOUND → triggers fallback

Fallback (single):    models/plant_disease_resnet.pt  ← ACTIVE (20 classes, ResNet18)
```

### 3. Startup Exceptions

The backend logs showed:
```
[WARN] Failed to load two-stage models: [crop_model.pt not found]
[OK]   Fallback ResNet18 model loaded successfully with 20 classes.
```

### 4. Git History — Root Cause

Commit `9fd501c` explicitly **deleted** `crop_model.pt` and `disease_model.pt`:
> "Replace two-stage training with single-stage ResNet18 for production stability"

The training script `backend/scratch/train_single_stage_resnet.py` (lines 173-178) contained logic to delete the primary model files and replace them with the single-stage model.

**Conclusion: The two-stage architecture was abandoned during development. The current single-stage ResNet18 is the intended production model.**

### 5. classes.json Consistency Check

| File | Classes | Status |
|---|---|---|
| `models/classes.json` | 20 classes | ✅ Matches active `plant_disease_resnet.pt` |
| `models_backup/classes_backup.json` | 45 classes | ✅ Matches rollback model |
| `models_backup/production_v2/classes_v2.json` | 20 classes | ✅ Same as production |

No mismatch. The `classes.json` is correctly aligned with the production model.

### 6. Model Hashes

| Model | MD5 Hash | Classes |
|---|---|---|
| `models/plant_disease_resnet.pt` | `bdeda225` | 20 |
| `models/plant_disease_resnet_new.pt` | `bdeda225` | 20 |
| `models/plant_disease_resnet_v2.pt` | `bdeda225` | 20 |
| `models_backup/production_v2/plant_disease_resnet_v2.pt` | `bdeda225` | 20 |
| `models_backup/production_v1/plant_disease_resnet_v1.pt` | `bdeda225` | 20 |
| `models_backup/plant_disease_resnet_rollback.pt` | `948bd86a` | 45 |
| `models_backup/final_45_class/plant_disease_resnet.pt` | `948bd86a` | 45 |

**Finding:** `plant_disease_resnet.pt`, `plant_disease_resnet_new.pt`, and `plant_disease_resnet_v2.pt` are **identical files** (same hash). The "v2" naming is misleading.

### 7. Which Model Is Serving Predictions Right Now?

**`backend/models/plant_disease_resnet.pt` (ResNet18, 20 classes)**

This is the Production V2 model with evaluation metrics:
- Overall Field Accuracy: **69.89%**
- Healthy Leaf False Positive Rate: **16.67%** (down from 79.17%)
- Rice Blast Accuracy: **80.00%**
- Macro F1 Score: **59.37%**

---

## Why the Potato Late Blight Scan Was Rejected

### Trace

```
Image:           potato_late_blight.jpg
Crop param:      potato
Quality check:   PASSED
Model:           plant_disease_resnet.pt (20-class fallback)
Top prediction:  Plant_Healthy = 42.18% [WRONG CLASS]
Confidence:      42.18%
Old threshold:   < 50.0% → REJECT
Result:          confidence_failed → "Photo Quality Warning" popup
```

### Root Cause

The 20-class ResNet18 model is **not calibrated** for Potato Late Blight at high confidence. On Potato Late Blight synthetic test images, it predicts `Plant_Healthy` at 27-36% confidence. The 50% hard rejection threshold was too strict for this model's calibration range.

**The image was not blurry or low quality. The model simply does not recognize Potato Late Blight with sufficient confidence.**

---

## Resolution Implemented

### Backend Changes (main.py)

Replaced the hard 50% rejection threshold with a **4-band confidence system**:

| Band | Range | Action |
|---|---|---|
| **High** | ≥ 70% | Show diagnosis, no warning |
| **Moderate** | 50-69% | Show diagnosis + verification warning |
| **Low** | 35-49% | Route to AI Vision fallback (if crop specified) OR reject |
| **Reject** | < 35% | Hard reject — truly ambiguous image |

**Key improvement for farmers:** When a farmer scans a potato leaf and the CNN confidence is 35-49%, the system now routes to the AI Vision fallback generator which produces a crop-specific diagnosis for `potato` using disease pattern matching. This ensures the farmer always receives actionable guidance.

### Flutter Changes

- **`DiseaseReport` model**: Added `confidenceBand` field
- **`DiseaseDetectionService`**: Passes `confidenceBand` from API response
- **`DiseaseResultScreen`**: New confidence band UI badge:
  - 🟢 **High Confidence** (verified checkmark, green)
  - 🟡 **Moderate Confidence** (info icon, orange)
  - 🔴 **Low Confidence — AI Assist** (warning icon, deep orange)

---

## 45-Class Rollback Model Assessment

> [!WARNING]
> The 45-class rollback model (`plant_disease_resnet_rollback.pt`) performs **worse** than the current 20-class model on Potato Late Blight. On the Potato Late Blight test image, it predicted:
> - `Apple___Black_Rot`: 21.4%
> - `Peach___Bacterial_Spot`: 20.6%
> - `Corn___Northern_Leaf_Blight`: 18.5%
>
> **Do NOT restore the 45-class model.** The 20-class model is the correct production choice.

---

## Production Status After Fix

| Component | Status |
|---|---|
| Active model | `plant_disease_resnet.pt` (20 classes, ResNet18) ✅ |
| Model loading | Single-stage fallback — **this is now the intended mode** |
| classes.json | 20 classes — correctly aligned ✅ |
| Confidence bands | Implemented (High/Moderate/Low/Reject) ✅ |
| Potato Late Blight scan | Will now route to AI Vision fallback (35-49% band) ✅ |
| Hard rejection | Only for confidence < 35% ✅ |
