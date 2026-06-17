import os
import json
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.ensemble import RandomForestClassifier

# Paths
DATA_PATH = "dataset/crop_suitability.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "crop_suitability_model.pkl")
PREPROCESSORS_PATH = os.path.join(MODEL_DIR, "crop_suitability_preprocessors.pkl")
METRICS_PATH = "training_metrics.json"
IMPORTANCE_PATH = "feature_importance.csv"
CONF_MATRIX_PATH = "confusion_matrix.png"
REPORT_PATH = "suitability_training_report.md"

def train_and_evaluate():
    print("--------------------------------------------------")
    print("Training Crop Suitability Validation Model")
    print("--------------------------------------------------")
    
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}. Run generate_suitability_data.py first.")
        
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded dataset with {len(df)} rows.")
    print(f"Class distribution:\n{df['suitable'].value_counts(normalize=True)}")
    
    categorical_cols = ["soil_type", "state", "district", "season", "water_availability", "previous_crop", "target_crop"]
    numeric_cols = ["rainfall", "temperature", "humidity", "farm_size"]
    target_col = "suitable"
    
    # Preprocessing categorical features
    label_encoders = {}
    X_encoded = pd.DataFrame()
    for col in categorical_cols:
        le = LabelEncoder()
        unique_vals = list(df[col].unique())
        if "<unknown>" not in unique_vals:
            unique_vals.append("<unknown>")
        le.fit(unique_vals)
        label_encoders[col] = le
        
        # Map values
        X_encoded[col] = df[col].map(lambda s: s if s in le.classes_ else "<unknown>")
        X_encoded[col] = le.transform(X_encoded[col])
        
    # Scale numeric features
    scaler = StandardScaler()
    X_numeric = pd.DataFrame(scaler.fit_transform(df[numeric_cols]), columns=numeric_cols)
    
    # Combine processed features
    X = pd.concat([X_encoded, X_numeric], axis=1)
    y = df[target_col]
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # Preprocessor save container
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(PREPROCESSORS_PATH, "wb") as f:
        pickle.dump({"label_encoders": label_encoders, "scaler": scaler}, f)
    print(f"Saved preprocessors to {PREPROCESSORS_PATH}")
    
    # Model evaluation dict
    model_results = {}
    trained_models = {}
    
    # 1. Random Forest
    print("\nTraining RandomForestClassifier...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    trained_models["RandomForest"] = rf
    
    # 2. XGBoost (try-except import)
    try:
        from xgboost import XGBClassifier
        print("Training XGBClassifier...")
        xgb = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
        xgb.fit(X_train, y_train)
        trained_models["XGBoost"] = xgb
    except ImportError:
        print("XGBoost is not installed or import failed. Skipping.")
        
    # 3. LightGBM (try-except import)
    try:
        from lightgbm import LGBMClassifier
        print("Training LGBMClassifier...")
        lgbm = LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1, verbose=-1)
        lgbm.fit(X_train, y_train)
        trained_models["LightGBM"] = lgbm
    except ImportError:
        print("LightGBM is not installed or import failed. Skipping.")
        
    # 4. CatBoost (try-except import)
    try:
        from catboost import CatBoostClassifier
        print("Training CatBoostClassifier...")
        cat = CatBoostClassifier(iterations=100, depth=6, learning_rate=0.1, random_seed=42, verbose=0)
        cat.fit(X_train, y_train)
        trained_models["CatBoost"] = cat
    except ImportError:
        print("CatBoost is not installed or import failed. Skipping.")
        
    # Evaluate all trained models
    best_f1 = -1
    best_model_name = None
    best_model = None
    
    for name, model in trained_models.items():
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)
        
        print(f"{name} Results - Acc: {acc:.4f}, Prec: {prec:.4f}, Rec: {rec:.4f}, F1: {f1:.4f}")
        
        model_results[name] = {
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1_score": float(f1)
        }
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model = model
            
    print(f"\nBest model selected: {best_model_name} with F1-score {best_f1:.4f}")
    
    # Save best model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(best_model, f)
    print(f"Saved best model to {MODEL_PATH}")
    
    # Save metrics JSON
    metrics_data = {
        "best_model": best_model_name,
        "results": model_results
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"Saved metrics to {METRICS_PATH}")
    
    # Feature Importances (using RandomForest or tree models)
    importances = None
    if hasattr(best_model, "feature_importances_"):
        importances = best_model.feature_importances_
    elif hasattr(best_model, "get_feature_importance"):
        importances = best_model.get_feature_importance()
        
    if importances is not None:
        importance_df = pd.DataFrame({
            "feature": X.columns,
            "importance": importances
        }).sort_values("importance", ascending=False)
        importance_df.to_csv(IMPORTANCE_PATH, index=False)
        print(f"Saved feature importances to {IMPORTANCE_PATH}")
    else:
        importance_df = pd.DataFrame()
        
    # Generate Confusion Matrix Plot
    preds = best_model.predict(X_test)
    cm = confusion_matrix(y_test, preds)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Unsuitable", "Suitable"])
    disp.plot(cmap=plt.cm.Blues)
    plt.title(f"Confusion Matrix ({best_model_name})")
    plt.savefig(CONF_MATRIX_PATH)
    plt.close()
    print(f"Saved confusion matrix plot to {CONF_MATRIX_PATH}")
    
    # Create suitability_training_report.md
    create_report(best_model_name, model_results, importance_df)
    print(f"Generated training report at {REPORT_PATH}")

def create_report(best_name, results, importance_df):
    report_content = f"""# Crop Suitability Model Training Report

This report outlines the training and evaluation metrics for the **AI Crop Suitability Validation Model** in Kisan Mitra.

## 1. Model Comparisons

We compared multiple classification algorithms to determine the best model for validating custom crops before planting:

| Model Name | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|
"""
    for name, metrics in results.items():
        report_content += f"| {name} | {metrics['accuracy']:.4f} | {metrics['precision']:.4f} | {metrics['recall']:.4f} | {metrics['f1_score']:.4f} |\n"
        
    report_content += f"""
**Selected Model:** `{best_name}`

---

## 2. Feature Importances

The feature importance contribution from the selected model `{best_name}`:

| Rank | Feature | Importance |
|---|---|---|
"""
    if not importance_df.empty:
        for i, row in enumerate(importance_df.itertuples(), 1):
            report_content += f"| {i} | {row.feature} | {row.importance:.4f} |\n"
    else:
        report_content += "| - | No feature importances available | - |\n"
        
    report_content += f"""
---

## 3. Confusion Matrix

The confusion matrix for the test partition is visualized below:

![Confusion Matrix](file:///{os.path.abspath(CONF_MATRIX_PATH).replace('\\', '/')})
"""
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)

if __name__ == "__main__":
    train_and_evaluate()
