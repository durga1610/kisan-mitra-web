import os
import json
import pickle
import random
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# --- CONFIGURATION ---
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "crop_recommendation_model.pkl")
PREPROCESSORS_PATH = os.path.join(MODEL_DIR, "crop_recommendation_preprocessors.pkl")
REPORT_PATH = "training_report.md"

# Categories
SOIL_TYPES = ["Alluvial", "Black", "Sandy", "Clayey", "Red", "Loamy"]
STATES = ["Punjab", "Haryana", "Maharashtra", "Gujarat", "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Rajasthan", "Madhya Pradesh", "Andhra Pradesh"]
DISTRICTS = ["Ludhiana", "Karnal", "Pune", "Rajkot", "Lucknow", "Kolar", "Coimbatore", "Jaipur", "Rampur", "Manchar", "Nilokheri"]
SEASONS = ["Kharif", "Rabi", "Zaid"]
WATER_AVAILABILITIES = ["High", "Medium", "Low"]
CROPS = ["tomato", "rice", "cotton", "wheat", "maize", "potato", "mustard", "sugarcane", "soybean"]
PREVIOUS_CROPS = CROPS + ["none"]

def generate_synthetic_data(num_samples=3000):
    """
    Generates synthetic agricultural crop recommendation dataset based on realistic rules.
    """
    random.seed(42)
    np.random.seed(42)
    
    data = []
    for i in range(num_samples):
        soil = random.choice(SOIL_TYPES)
        state = random.choice(STATES)
        district = random.choice(DISTRICTS)
        season = random.choice(SEASONS)
        water = random.choice(WATER_AVAILABILITIES)
        prev_crop = random.choice(PREVIOUS_CROPS)
        
        # Environmental conditions based on season
        if season == "Kharif":
            temp = float(np.random.normal(30.0, 3.0))
            humidity = float(np.random.normal(80.0, 5.0))
            rainfall = float(np.random.normal(150.0, 30.0))
        elif season == "Rabi":
            temp = float(np.random.normal(18.0, 3.0))
            humidity = float(np.random.normal(60.0, 10.0))
            rainfall = float(np.random.normal(30.0, 15.0))
        else: # Zaid (Summer)
            temp = float(np.random.normal(36.0, 2.0))
            humidity = float(np.random.normal(45.0, 10.0))
            rainfall = float(np.random.normal(15.0, 10.0))
            
        farm_size = float(max(0.5, np.random.normal(8.0, 4.0)))
        
        # Clip numerical parameters to realistic boundaries
        temp = max(10.0, min(50.0, temp))
        humidity = max(15.0, min(100.0, humidity))
        rainfall = max(0.0, min(400.0, rainfall))
        
        # Calculate suitability score for each crop candidate
        crop_scores = {}
        for crop in CROPS:
            score = 100.0
            
            # 1. Season constraint (strong)
            if crop in ["rice", "cotton", "sugarcane", "maize", "soybean"]:
                if season != "Kharif": score -= 60
            elif crop in ["wheat", "mustard", "potato"]:
                if season != "Rabi": score -= 60
            elif crop == "tomato":
                if season == "Kharif": score -= 40  # tomatoes struggle in heavy monsoon rain
                
            # 2. Water Availability & Rainfall
            if crop in ["rice", "sugarcane"]:
                if water == "Low": score -= 70
                elif water == "Medium": score -= 30
                if rainfall < 120.0: score -= 40
            elif crop == "cotton":
                if water == "Low": score -= 40
                if rainfall > 200.0 or rainfall < 50.0: score -= 20
            elif crop == "mustard":
                if water == "High": score -= 20  # mustard prefers dry root zones
                if rainfall > 80.0: score -= 30
            elif crop == "soybean":
                if water == "Low": score -= 40
                if rainfall < 50.0: score -= 30
                
            # 3. Soil Suitability
            if crop == "rice":
                if soil not in ["Clayey", "Alluvial"]: score -= 50
            elif crop == "soybean":
                if soil not in ["Black", "Loamy"]: score -= 40
            elif crop == "cotton":
                if soil not in ["Black", "Alluvial"]: score -= 50
            elif crop == "wheat":
                if soil not in ["Alluvial", "Clayey", "Black"]: score -= 40
            elif crop == "potato":
                if soil not in ["Sandy", "Loamy"]: score -= 50
            elif crop == "tomato":
                if soil not in ["Loamy", "Sandy", "Red"]: score -= 30
                
            # 4. Temperature constraints
            if crop in ["wheat", "potato"]:
                if temp > 25.0: score -= 40
            elif crop in ["cotton", "sugarcane"]:
                if temp < 22.0: score -= 40
                
            # 5. Crop Rotation Penalty
            if crop == prev_crop:
                score -= 40
                
            # Add some random noise
            score += np.random.normal(0, 5.0)
            crop_scores[crop] = score
            
        # Select best crop
        recommended_crop = max(crop_scores, key=crop_scores.get)
        
        data.append({
            "soil_type": soil,
            "state": state,
            "district": district,
            "season": season,
            "rainfall": rainfall,
            "temperature": temp,
            "humidity": humidity,
            "water_availability": water,
            "farm_size": farm_size,
            "previous_crop": prev_crop,
            "recommended_crop": recommended_crop
        })
        
    return pd.DataFrame(data)

def train_model():
    print("Generating synthetic dataset...")
    df = generate_synthetic_data(3500)
    print(f"Generated dataset with {df.shape[0]} rows.")
    print("Label distributions of recommended crop:")
    print(df["recommended_crop"].value_counts())
    
    # Ensure models directory exists
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    categorical_cols = ["soil_type", "state", "district", "season", "water_availability", "previous_crop"]
    numeric_cols = ["rainfall", "temperature", "humidity", "farm_size"]
    target_col = "recommended_crop"
    
    # Preprocessing containers
    label_encoders = {}
    
    # Fit and transform categorical features
    # To handle unseen labels during inference, we fit a custom list that includes '<unknown>'
    print("\nFitting label encoders...")
    X_encoded = pd.DataFrame()
    for col in categorical_cols:
        le = LabelEncoder()
        # Find unique values and add '<unknown>' to classes
        unique_vals = list(df[col].unique())
        if "<unknown>" not in unique_vals:
            unique_vals.append("<unknown>")
        le.fit(unique_vals)
        label_encoders[col] = le
        
        # Transform (mapping unseen default values to '<unknown>')
        X_encoded[col] = df[col].map(lambda s: s if s in le.classes_ else "<unknown>")
        X_encoded[col] = le.transform(X_encoded[col])
        
    # Scale numeric values
    print("Normalizing numeric values...")
    scaler = StandardScaler()
    X_numeric = pd.DataFrame(scaler.fit_transform(df[numeric_cols]), columns=numeric_cols)
    
    # Encode target recommended crop
    target_encoder = LabelEncoder()
    y_encoded = target_encoder.fit_transform(df[target_col])
    
    # Combine features
    X = pd.concat([X_encoded, X_numeric], axis=1)
    y = y_encoded
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train RandomForestClassifier
    print("\nTraining RandomForestClassifier...")
    clf = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    
    # Evaluate
    y_pred = clf.predict(X_test)
    train_acc = clf.score(X_train, y_train)
    test_acc = accuracy_score(y_test, y_pred)
    
    print(f"Train Accuracy: {train_acc * 100:.2f}%")
    print(f"Test Accuracy: {test_acc * 100:.2f}%")
    
    # Generate reports
    cm = confusion_matrix(y_test, y_pred)
    class_names = target_encoder.classes_
    cls_report = classification_report(y_test, y_pred, target_names=class_names)
    
    print("\nClassification Report:")
    print(cls_report)
    
    # Save the model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
    print(f"Model saved to: {MODEL_PATH}")
    
    # Save encoders and scaler
    preprocessors = {
        "label_encoders": label_encoders,
        "target_encoder": target_encoder,
        "scaler": scaler,
        "categorical_cols": categorical_cols,
        "numeric_cols": numeric_cols
    }
    with open(PREPROCESSORS_PATH, "wb") as f:
        pickle.dump(preprocessors, f)
    print(f"Preprocessors saved to: {PREPROCESSORS_PATH}")
    
    # Generate training report md
    generate_markdown_report(train_acc, test_acc, cm, cls_report, class_names)

def generate_markdown_report(train_acc, test_acc, cm, cls_report, class_names):
    cm_lines = []
    cm_lines.append("True \\ Pred | " + " | ".join(class_names))
    cm_lines.append("-" * 15 * (len(class_names) + 1))
    for i, row in enumerate(cm):
        cm_lines.append(f"{class_names[i]:<11} | " + " | ".join(f"{val:<4}" for val in row))
    cm_table = "\n".join(cm_lines)
    
    report_content = f"""# Crop Recommendation Model Training Report

This report summarizes the training metrics, classification accuracy, and confusion matrix for the RandomForestClassifier model used in the crop recommendation engine.

## Model Summary
- **Model Type**: RandomForestClassifier
- **Number of Estimators**: 150
- **Max Depth**: 12
- **Training Accuracy**: {train_acc * 100:.2f}%
- **Test Accuracy**: {test_acc * 100:.2f}%

## Features Utilized
### Categorical Fields (Label Encoded):
- `soil_type`
- `state`
- `district`
- `season`
- `water_availability`
- `previous_crop`

### Numeric Fields (Standardized):
- `rainfall`
- `temperature`
- `humidity`
- `farm_size`

## Evaluation Metrics

### Classification Report
```
{cls_report}
```

### Confusion Matrix
```
{cm_table}
```

---
Report generated automatically on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Training report saved to: {REPORT_PATH}")

if __name__ == "__main__":
    train_model()
