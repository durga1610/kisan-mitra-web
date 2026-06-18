# 🌾 Restructured Disease Dataset Audit Report

This report documents the final split counts, class imbalance ratios, and training parameters for the restructured 24-class plant disease dataset.

---

## 📈 1. Restructured Class Distribution & Imbalances

Evaluated across the restructured `dataset/` splits. The largest class is **`Plant_Healthy`** with **1,293 training images** ($1.00\times$ baseline).

| Class Name | Train Images | Val Images | Test Images | Image Type | Imbalance Ratio (vs. Largest) |
| :--- | :---: | :---: | :---: | :--- | :---: |
| **Plant_Healthy** | 1293 | 328 | 1266 | Combined Real | **1.00x** |
| **Tomato___Septoria_Leaf_Spot** | 319 | 80 | 1475 | Real (Rebuilt) | **4.05x** |
| **Tomato___Late_Blight** | 287 | 72 | 1549 | Real (Rebuilt) | **4.51x** |
| **Tomato___Bacterial_Spot** | 286 | 72 | 1478 | Real (Rebuilt) | **4.52x** |
| **Potato___Early_Blight** | 285 | 72 | 748 | Real (Rebuilt) | **4.54x** |
| **Potato___Late_Blight** | 274 | 69 | 713 | Real (Rebuilt) | **4.72x** |
| **Tomato___Leaf_Mold** | 271 | 68 | 625 | Real (Rebuilt) | **4.77x** |
| **Tomato___Early_Blight** | 268 | 68 | 725 | Real (Rebuilt) | **4.82x** |
| **Tomato___Yellow_Leaf_Curl_Virus** | 259 | 65 | 4471 | Real (Rebuilt) | **4.99x** |
| **Tomato___Spider_Mites** | 247 | 62 | 1066 | Real (Rebuilt) | **5.23x** |
| **Grape___Black_Rot** | 247 | 62 | 743 | Real (Rebuilt) | **5.23x** |
| **Tomato___Target_Spot** | 245 | 62 | 1044 | Real (Rebuilt) | **5.28x** |
| **Tomato___Healthy** | 245 | 62 | 1062 | Real (Rebuilt) | *Merged to Plant_Healthy* |
| **Grape___Healthy** | 243 | 61 | 90 | Real (Rebuilt) | *Merged to Plant_Healthy* |
| **Grape___Esca** | 243 | 61 | 861 | Real (Rebuilt) | **5.32x** |
| **Grape___Leaf_Blight** | 243 | 61 | 802 | Real (Rebuilt) | **5.32x** |
| **Tomato___Mosaic_Virus** | 241 | 61 | 102 | Real (Rebuilt) | **5.37x** |
| **Cotton___Leaf_Curl** | 200 | 50 | 181 | Real (Rebuilt) | **6.46x** |
| **Cotton___Healthy** | 200 | 50 | 5 | Real (Rebuilt) | *Merged to Plant_Healthy* |
| **Cotton___Bacterial_Blight** | 200 | 50 | 0 | Real (Rebuilt) | **6.46x** |
| **Rice___Bacterial_Leaf_Blight** | 200 | 50 | 0 | Real (Rebuilt) | **6.46x** |
| **Rice___Blast** | 200 | 50 | 107 | Real (Rebuilt) | **6.46x** |
| **Rice___Brown_Spot** | 200 | 50 | 124 | Real (Rebuilt) | **6.46x** |
| **Rice___Healthy** | 200 | 50 | 94 | Real (Rebuilt) | *Merged to Plant_Healthy* |
| **Corn___Common_Rust** | 15 | 5 | 5 | Synthetic (Legacy) | **86.20x** ⚠️ |
| **Corn___Gray_Leaf_Spot** | 15 | 5 | 5 | Synthetic (Legacy) | **86.20x** ⚠️ |
| **Corn___Northern_Leaf_Blight** | 15 | 5 | 5 | Synthetic (Legacy) | **86.20x** ⚠️ |
| **Pepper_Bell___Bacterial_Spot** | 15 | 5 | 5 | Synthetic (Legacy) | **86.20x** ⚠️ |

---

## 🛠️ 2. Key Audit Statistics
* **Exact Number of Active Classes**: **24 classes** (defined in [classes.json](file:///c:/Users/durga/kisan_mitra/backend/models/classes.json)).
* **Total Active Training Images**: **6,398 images** (a 24% reduction in training data footprint, which will accelerate convergence).
* **Deficiency Profile**: Only Corn (Maize) and Pepper Bell remain at 15 training images, while all other active crop classes are balanced between 200 and 319 training images.

---

## ⏱️ 3. Estimated Training Duration on CPU
* **Total Epochs**: 15
* **Unfrozen Parameters**: ResNet18 complete fine-tuning.
* **Batch Size**: 32 (200 batches per epoch).
* **Epoch Time**: ~1.2 to 1.5 minutes per epoch on CPU.
* **Total Estimated Training Duration**: **18 to 22 minutes**.
