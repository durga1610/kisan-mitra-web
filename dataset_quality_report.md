# 🛡️ Kisan Mitra Dataset Quality Audit Report
This report documents the filtering, cleaning, and quality checks performed during the dataset rebuild for priority crops.
## Cleaning Summary
| Crop Class | Initial Files | Corrupt Removed | Exact Duplicates (MD5) | Near Duplicates (aHash) | Clean Unique Real |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Cotton___Bacterial_Blight | 250 | 0 | 0 | 4 | 246 |
| Cotton___Healthy | 257 | 0 | 0 | 2 | 255 |
| Cotton___Leaf_Curl | 431 | 0 | 0 | 0 | 431 |
| Grape___Black_Rot | 1180 | 0 | 0 | 187 | 993 |
| Grape___Esca | 1383 | 0 | 0 | 272 | 1111 |
| Grape___Healthy | 423 | 0 | 0 | 83 | 340 |
| Grape___Leaf_Blight | 1076 | 0 | 0 | 24 | 1052 |
| Potato___Early_Blight | 1000 | 0 | 0 | 2 | 998 |
| Potato___Healthy | 152 | 0 | 0 | 5 | 147 |
| Potato___Late_Blight | 1000 | 0 | 0 | 37 | 963 |
| Rice___Bacterial_Leaf_Blight | 96 | 0 | 19 | 1 | 76 |
| Rice___Blast | 523 | 0 | 0 | 166 | 357 |
| Rice___Brown_Spot | 523 | 0 | 0 | 149 | 374 |
| Rice___Healthy | 523 | 0 | 0 | 179 | 344 |
| Tomato___Bacterial_Spot | 2127 | 0 | 0 | 399 | 1728 |
| Tomato___Early_Blight | 1000 | 0 | 0 | 25 | 975 |
| Tomato___Healthy | 1591 | 0 | 4 | 275 | 1312 |
| Tomato___Late_Blight | 1909 | 0 | 8 | 102 | 1799 |
| Tomato___Leaf_Mold | 952 | 0 | 0 | 77 | 875 |
| Tomato___Mosaic_Virus | 373 | 0 | 0 | 21 | 352 |
| Tomato___Septoria_Leaf_Spot | 1771 | 0 | 0 | 46 | 1725 |
| Tomato___Spider_Mites | 1676 | 0 | 0 | 360 | 1316 |
| Tomato___Target_Spot | 1404 | 0 | 0 | 110 | 1294 |
| Tomato___Yellow_Leaf_Curl_Virus | 5357 | 0 | 0 | 636 | 4721 |

## Duplicate Detection Methodology
- **Exact Duplicates**: Identified via MD5 hashing on the file content.
- **Near Duplicates**: Identified via average hashing (aHash) by converting images to 8x8 grayscale and filtering matches with a Hamming distance of <= 2.
- **Corruption Checks**: Verified both PIL file metadata open (`verify()`) and pixel buffer load (`load()`).
