# 📊 Kisan Mitra Class Distribution & Balance Report
This report documents the final distribution of real-world and synthetic images across all 45 classes.
## Image Counts per Class
| Class Name | Real Image Count | Synthetic Image Count | Total Image Count | Status |
| :--- | :---: | :---: | :---: | :--- |
| Apple___Black_Rot | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Apple___Cedar_Apple_Rust | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Apple___Healthy | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Apple___Scab | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Blueberry___Healthy | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Cherry___Healthy | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Cherry___Powdery_Mildew | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Corn___Common_Rust | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Corn___Gray_Leaf_Spot | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Corn___Healthy | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Corn___Northern_Leaf_Blight | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Cotton___Bacterial_Blight | 250 | 0 | 250 | 💚 Rebuilt (100% Real/Aug-Real) |
| Cotton___Healthy | 255 | 0 | 255 | 💚 Rebuilt (100% Real/Aug-Real) |
| Cotton___Leaf_Curl | 431 | 0 | 431 | 💚 Rebuilt (100% Real/Aug-Real) |
| Grape___Black_Rot | 993 | 0 | 993 | 💚 Rebuilt (100% Real/Aug-Real) |
| Grape___Esca | 1111 | 0 | 1111 | 💚 Rebuilt (100% Real/Aug-Real) |
| Grape___Healthy | 340 | 0 | 340 | 💚 Rebuilt (100% Real/Aug-Real) |
| Grape___Leaf_Blight | 1052 | 0 | 1052 | 💚 Rebuilt (100% Real/Aug-Real) |
| Orange___Haunglongbing | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Peach___Bacterial_Spot | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Peach___Healthy | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Pepper_Bell___Bacterial_Spot | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Pepper_Bell___Healthy | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Potato___Early_Blight | 998 | 0 | 998 | 💚 Rebuilt (100% Real/Aug-Real) |
| Potato___Healthy | 250 | 0 | 250 | 💚 Rebuilt (100% Real/Aug-Real) |
| Potato___Late_Blight | 963 | 0 | 963 | 💚 Rebuilt (100% Real/Aug-Real) |
| Raspberry___Healthy | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Rice___Bacterial_Leaf_Blight | 250 | 0 | 250 | 💚 Rebuilt (100% Real/Aug-Real) |
| Rice___Blast | 357 | 0 | 357 | 💚 Rebuilt (100% Real/Aug-Real) |
| Rice___Brown_Spot | 374 | 0 | 374 | 💚 Rebuilt (100% Real/Aug-Real) |
| Rice___Healthy | 344 | 0 | 344 | 💚 Rebuilt (100% Real/Aug-Real) |
| Soybean___Healthy | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Squash___Powdery_Mildew | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Strawberry___Healthy | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Strawberry___Leaf_Scorch | 0 | 25 | 25 | ⬜ Unchanged (Legacy Blend) |
| Tomato___Bacterial_Spot | 1728 | 0 | 1728 | 💚 Rebuilt (100% Real/Aug-Real) |
| Tomato___Early_Blight | 975 | 0 | 975 | 💚 Rebuilt (100% Real/Aug-Real) |
| Tomato___Healthy | 1312 | 0 | 1312 | 💚 Rebuilt (100% Real/Aug-Real) |
| Tomato___Late_Blight | 1799 | 0 | 1799 | 💚 Rebuilt (100% Real/Aug-Real) |
| Tomato___Leaf_Mold | 875 | 0 | 875 | 💚 Rebuilt (100% Real/Aug-Real) |
| Tomato___Mosaic_Virus | 352 | 0 | 352 | 💚 Rebuilt (100% Real/Aug-Real) |
| Tomato___Septoria_Leaf_Spot | 1725 | 0 | 1725 | 💚 Rebuilt (100% Real/Aug-Real) |
| Tomato___Spider_Mites | 1316 | 0 | 1316 | 💚 Rebuilt (100% Real/Aug-Real) |
| Tomato___Target_Spot | 1294 | 0 | 1294 | 💚 Rebuilt (100% Real/Aug-Real) |
| Tomato___Yellow_Leaf_Curl_Virus | 4721 | 0 | 4721 | 💚 Rebuilt (100% Real/Aug-Real) |

## Balance Targets Verification
- **Priority Crops Minimums**: All priority crop classes must have >= 200 train and >= 50 validation real images. Verified.
- **Synthetic Dependence Removal**: All priority crop classes now have exactly 0 synthetic images. Verified.
