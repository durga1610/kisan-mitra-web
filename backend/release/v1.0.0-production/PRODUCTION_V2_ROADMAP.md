# Kisan Mitra — Production v2 Disease Model Roadmap

> **Scope**: Disease detection model improvement only.  
> **Frozen (do not touch)**: routing logic, confidence bands, advisor, weather, universal crop support, fertilizer engine.  
> **Baseline**: v1.0.0-production (ResNet18, 20 classes, 69.89% field accuracy)

---

## Executive Goal

Production v2 targets a **≥85% field accuracy** disease detection model with **real farmer-collected images**, expanded to cover a minimum of **45 disease classes across 12 crops**. The confidence band system and AI Vision fallback stay identical — v2 simply improves the CNN hit rate so that more predictions fall in HIGH/MODERATE bands instead of LOW/REJECT.

---

## 1. Real Field Image Collection Strategy

### Why synthetic images are insufficient

The v1.0 test set (`synth_*.jpg`) consists entirely of programmatically generated images. The 20-class model achieves 69.89% on these but scores poorly on unseen real images (Potato Late Blight: 0/5 correct on synthetic set, likely due to synthetic artifacts). A real-photo dataset is mandatory for v2.

### Collection Channels

| Channel | Target Images/Month | Priority |
|---|---|---|
| **Kisan Mitra app in-app capture** | 500–1,000 | HIGH — install feedback loop in disease scan UI to allow farmers to tag confirmed diagnoses |
| **ICAR / KVK partnerships** | 1,000–2,000 | HIGH — district Krishi Vigyan Kendras have field extension officers with labelled photos |
| **PlantVillage real-photo subset** | 3,000 | MEDIUM — select only real (non-synthetic) images from PlantVillage dataset |
| **iNaturalist plant disease observations** | 500–1,000 | MEDIUM — use their CC-licensed dataset, filter to India-region crops |
| **WhatsApp farmer groups (opt-in)** | 200–500 | LOW — collect with explicit consent; label with agronomist review |

### In-App Collection Pipeline

```
Farmer scans leaf
    → Disease result shown
    → "Was this diagnosis correct?" prompt (Yes / No / Unsure)
    → If Yes: image + label sent to collection bucket (with consent)
    → If No: image flagged for agronomist review
    → Verified images enter training queue monthly
```

### Image Quality Standards for Training

- Minimum resolution: **512×512 px** (higher than inference minimum)
- Lighting: natural daylight only; reject flash/indoor
- Leaf coverage: ≥ 60% of frame
- Blur: Laplacian variance ≥ 100 (stricter than inference gate)
- Label verification: minimum 2 independent reviewers per image
- Metadata required: crop name, disease name, GPS region, capture date, growth stage

---

## 2. Dataset Expansion Targets per Crop

### Current v1.0 Status

| Crop | Diseases (CNN) | Training Images | Field Accuracy |
|---|---|---|---|
| Cotton | 2 | ~400 | ~94% |
| Grape | 3 | ~600 | ~30–60% |
| Potato | 2 | ~400 | 0% (synthetic only) |
| Rice | 3 | ~600 | 80% (Blast) |
| Tomato | 9 | ~1,800 | 30–70% |

### Production v2 Targets

| Crop | Target Diseases | Real Images Required | Priority |
|---|---|---|---|
| **Rice** | Blast, Brown Spot, Bacterial Leaf Blight, Sheath Blight, Neck Rot | 500/disease | P0 — highest Indian crop coverage |
| **Wheat** | Leaf Rust, Stem Rust, Powdery Mildew, Loose Smut, Karnal Bunt | 400/disease | P0 — major Rabi crop |
| **Tomato** | All 9 existing + Late Blight improvement | 300/disease | P0 — most disease classes |
| **Potato** | Early Blight, Late Blight | 500/disease (real only) | P0 — critical, current accuracy 0% |
| **Cotton** | Bacterial Blight, Leaf Curl + Bollworm damage | 400/disease | P1 |
| **Maize/Corn** | Common Rust, Northern Leaf Blight, Gray Leaf Spot, Fall Armyworm | 400/disease | P1 |
| **Groundnut** | Early Leaf Spot, Late Leaf Spot, Tikka Disease, Rust | 350/disease | P1 |
| **Soybean** | Bacterial Pustule, Pod Blight, Sudden Death | 350/disease | P1 |
| **Grape** | Black Rot, Downy Mildew, Powdery Mildew, Anthracnose | 400/disease | P1 |
| **Chilli/Pepper** | Anthracnose, Bacterial Leaf Spot, Phytophthora Blight | 350/disease | P2 |
| **Mango** | Anthracnose, Powdery Mildew, Bacterial Black Spot | 300/disease | P2 |
| **Banana** | Sigatoka Leaf Spot, Panama Wilt, Bunchy Top | 300/disease | P2 |

**Total target**: ~45 disease classes, ~16,000 real field images minimum

### Class Balance Requirements

- Maximum class imbalance ratio: **5:1** (vs 86:1 in current synthetic set)
- Per-class minimum: **300 real field images** for training
- Per-class validation minimum: **75 images** (held-out, never seen by model during training)

---

## 3. Validation Dataset Requirements

### Split Strategy for v2

| Split | Size | Source | Usage |
|---|---|---|---|
| **Train** | 70% | Real field images | Model training |
| **Validation** | 15% | Real field images (held-out) | Epoch monitoring, early stopping |
| **Field Test** | 15% | Real field images (never used in training) | Final acceptance testing |
| **Regression Suite** | Fixed 100 images/crop | Mix of real + held-out | Must pass before any release |

### Validation Metrics Required for v2 Promotion

| Metric | v1.0 Baseline | v2 Target | Minimum Accept |
|---|---|---|---|
| Overall field accuracy | 69.89% | ≥85% | ≥80% |
| Macro F1 | 59.37% | ≥75% | ≥70% |
| Healthy leaf FP rate | 16.67% | ≤10% | ≤15% |
| Potato Late Blight accuracy | 0% (synthetic) | ≥75% | ≥60% |
| Rice Blast accuracy | 80% | ≥90% | ≥85% |
| Wheat Rust accuracy | N/A (new) | ≥80% | ≥70% |
| Per-class minimum accuracy | — | ≥60% for all classes | No class below 50% |
| Confidence calibration | — | Top-1 confidence ≥ 50% on correctly classified images | — |

### Confusion Matrix Analysis

For each release candidate:
1. Generate full confusion matrix for all 45 classes
2. Identify top-10 confused pairs
3. Pairs with >10% confusion rate must be reviewed by plant pathologist
4. If pair confusion >20%, add additional training images for that pair before promoting

---

## 4. Training Plan for Production v3 (Model Architecture)

> v2 uses improved data with the same ResNet18 architecture.  
> v3 targets architectural upgrade for higher accuracy.

### v2 Training Plan (Data-Driven, Same Architecture)

| Phase | Action | Duration |
|---|---|---|
| **Data collection** | Collect 16,000 real field images across 45 classes | 3–6 months |
| **Data audit** | Run label verification pipeline; reject duplicates/blurry | 2 weeks |
| **Preprocessing** | Augment: flip, rotation, color jitter, CutMix, MixUp | 1 week |
| **Training** | Fine-tune ResNet18 from v1.0 weights; 50 epochs, LR=1e-4 | 1–2 days |
| **Validation** | Run on held-out field test set; check acceptance metrics | 1 week |
| **Promotion** | If metrics pass → tag v2.0.0-production; update classes.json | 1 day |

**Training configuration (v2):**
```python
Model:         ResNet18 (initialized from v1.0 weights)
Optimizer:     AdamW (lr=1e-4, weight_decay=1e-4)
Scheduler:     CosineAnnealingLR (T_max=50)
Loss:          CrossEntropyLoss with class weights (inverse frequency)
Augmentation:  RandomHorizontalFlip, RandomRotation(30), ColorJitter,
               RandomErasing, CutMix(p=0.5), MixUp(alpha=0.2)
Batch size:    64
Input size:    128x128 (same as v1.0 to keep inference transform identical)
Early stop:    patience=10 on validation F1
```

### v3 Training Plan (Architecture Upgrade)

**Prerequisite**: v2 field accuracy must be ≥80% before v3 work begins.

| Phase | Action |
|---|---|
| **Architecture selection** | Benchmark EfficientNet-B2, MobileNetV3-Large, ConvNeXt-Tiny on v2 dataset |
| **Transfer learning** | Initialize from ImageNet; add 45-class head |
| **Progressive training** | Freeze backbone → train head (10 epochs) → unfreeze → train full (40 epochs) |
| **Knowledge distillation** | Optionally distill v3 teacher into smaller student for mobile deployment |
| **ONNX export** | Export to ONNX for potential TFLite conversion for offline Android support |
| **Promotion** | Must beat v2 on ALL metrics before tagging v3.0.0-production |

**Expected v3 accuracy targets:**

| Metric | v3 Target |
|---|---|
| Overall field accuracy | ≥90% |
| Macro F1 | ≥85% |
| Potato Late Blight | ≥90% |
| Inference latency (CPU) | ≤200ms |

---

## 5. Expected Accuracy Improvements

### Improvement Pathway

```
v1.0 (synthetic data, 20 classes, ResNet18)
  → 69.89% field accuracy
  → Potato Late Blight: 0% (not in training set)
  → LOW/REJECT band: ~60% of potato/tomato predictions

        ↓ (real field data collection, 45 classes)

v2.0 (real field data, 45 classes, ResNet18 fine-tuned)
  → Target: 85%+ field accuracy
  → Potato Late Blight: 75%+ (real training images)
  → LOW/REJECT band: <20% of predictions (more fall in HIGH/MODERATE)

        ↓ (architecture upgrade, progressive training)

v3.0 (real field data, 45+ classes, EfficientNet-B2 or ConvNeXt)
  → Target: 90%+ field accuracy
  → All major crops: ≥85% per-class accuracy
  → LOW/REJECT band: <10% of predictions
```

### Impact on Confidence Band Distribution

| Band | v1.0 estimate | v2 target | v3 target |
|---|---|---|---|
| HIGH (≥70%) | ~20% of scans | ~50% | ~70% |
| MODERATE (50–70%) | ~15% | ~25% | ~20% |
| LOW (AI Vision) | ~30% | ~15% | ~8% |
| REJECT (<35%) | ~20% | ~5% | ~2% |
| Quality failed | ~15% | ~5% | ~5% (no change) |

> [!NOTE]
> The confidence band system does NOT change between v1, v2, and v3. Only the CNN model improves. As the model improves, more predictions naturally migrate from LOW/REJECT into MODERATE/HIGH without any routing logic changes.

---

## 6. What Stays Frozen Across All Versions

| Component | v2 | v3 |
|---|---|---|
| Confidence band thresholds | FROZEN | FROZEN |
| AI Vision fallback routing | FROZEN | FROZEN |
| Quality gate thresholds | FROZEN | FROZEN |
| Universal crop support (258 crops) | FROZEN (additive only) | FROZEN |
| Inference transform (128×128) | FROZEN | Re-evaluate if architecture changes |
| Advisory engine | FROZEN | FROZEN |
| Weather logic | FROZEN | FROZEN |
| Fertilizer engine | FROZEN | FROZEN |
| API contract (`/api/v1/disease/detect`) | FROZEN | FROZEN |
| `confidenceBand` response field | FROZEN | FROZEN |

---

## 7. Release Criteria for v2.0.0-production

All of the following must be true before tagging `v2.0.0-production`:

- [ ] ≥16,000 real field images collected and verified
- [ ] All 45 target disease classes represented with ≥300 training images
- [ ] Overall field accuracy ≥ 80% (minimum acceptable) or ≥ 85% (target)
- [ ] No class below 50% field accuracy
- [ ] Healthy leaf FP rate ≤ 15%
- [ ] Potato Late Blight accuracy ≥ 60%
- [ ] Regression suite: 100% pass on v1.0 accepted test scenarios
- [ ] SHA-256 of new model recorded and committed to release manifest
- [ ] Confidence band validation audit re-run and passed
- [ ] `classes.json` updated to match new 45-class taxonomy
- [ ] Deployment report written and approved

---

## Timeline Estimate

| Milestone | Estimated Duration |
|---|---|
| In-app collection pipeline deployment | 2 weeks |
| ICAR/KVK partnership and image collection | 3–6 months |
| Data audit and preprocessing | 3 weeks |
| v2 model training and validation | 2 weeks |
| v2 acceptance testing | 1 week |
| **v2.0.0-production tag** | **~6 months from today** |
| v3 architecture research | 2 months |
| v3 training and validation | 1 month |
| **v3.0.0-production tag** | **~9–12 months from today** |
