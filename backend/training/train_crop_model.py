import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

# Classifiers
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


def load_dataset(dataset_path: str) -> pd.DataFrame:
    """Loads CSV dataset from disk."""
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at: {dataset_path}")
    df = pd.read_csv(dataset_path)
    return df


def analyze_dataset(df: pd.DataFrame) -> dict:
    """Performs exploratory data analysis on the dataset."""
    print("=" * 60)
    print(" STEP 1: DATASET ANALYSIS & INSPECTION")
    print("=" * 60)
    
    shape = df.shape
    columns = list(df.columns)
    dtypes = df.dtypes.to_dict()
    missing_values = df.isnull().sum().to_dict()
    total_missing = sum(missing_values.values())
    duplicates = int(df.duplicated().sum())
    
    print(f"* Dataset Shape: {shape[0]} rows, {shape[1]} columns")
    print(f"* Features ({len(columns)-1}): {[c for c in columns if c != 'label']}")
    print(f"* Target Column: 'label'")
    print(f"* Missing Values Total: {total_missing}")
    print(f"* Duplicate Rows: {duplicates}")
    
    print("\n--- Summary Statistics ---")
    summary = df.describe().T[['mean', 'std', 'min', '50%', 'max']].rename(columns={'50%': 'median'})
    print(summary.to_string())
    
    class_counts = df['label'].value_counts().to_dict()
    num_classes = len(class_counts)
    print(f"\n--- Class Distribution ({num_classes} Crop Classes) ---")
    for crop, count in class_counts.items():
        print(f"  - {crop:15s}: {count} samples")
        
    correlation_matrix = df.drop(columns=['label']).corr().to_dict()
    
    return {
        "shape": shape,
        "columns": columns,
        "dtypes": {k: str(v) for k, v in dtypes.items()},
        "missing_values": missing_values,
        "total_missing": total_missing,
        "duplicates": duplicates,
        "class_counts": class_counts,
        "num_classes": num_classes,
        "summary": summary.to_dict(),
        "correlation": correlation_matrix,
    }


def preprocess_data(df: pd.DataFrame, test_size: float = 0.20, random_state: int = 42):
    """Preprocesses features, encodes target labels, and splits train/test sets."""
    print("\n" + "=" * 60)
    print(" STEP 2: DATA PREPROCESSING")
    print("=" * 60)
    
    feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    X = df[feature_cols].copy()
    y_raw = df['label'].copy()
    
    # Label Encoding
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    
    # Train / Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    print(f"* Feature Matrix Shape: {X.shape}")
    print(f"* Training Set: {X_train.shape[0]} samples ({100*(1-test_size):.0f}%)")
    print(f"* Testing Set:  {X_test.shape[0]} samples ({100*test_size:.0f}%)")
    print(f"* Encoded Classes: {len(label_encoder.classes_)} unique crops")
    
    return X_train, X_test, y_train, y_test, label_encoder, feature_cols


def train_and_evaluate_models(X_train, X_test, y_train, y_test, random_state: int = 42):
    """Trains multiple classifiers, evaluates performance, and selects the best model."""
    print("\n" + "=" * 60)
    print(" STEP 3: MODEL TRAINING & EVALUATION")
    print("=" * 60)
    
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=random_state),
        "Decision Tree": DecisionTreeClassifier(random_state=random_state),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
    }
    
    if XGBOOST_AVAILABLE:
        models["XGBoost"] = XGBClassifier(
            eval_metric="mlogloss", random_state=random_state
        )
    else:
        print("[Notice] XGBoost is not installed in the Python environment. Skipping XGBoost model.")
        
    results = {}
    best_model_name = None
    best_f1 = -1.0
    best_model_obj = None
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted")
        rec = recall_score(y_test, y_pred, average="weighted")
        f1 = f1_score(y_test, y_pred, average="weighted")
        
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        cm = confusion_matrix(y_test, y_pred)
        
        results[name] = {
            "model": model,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "cv_mean": cv_mean,
            "cv_std": cv_std,
            "confusion_matrix": cm,
            "predictions": y_pred,
        }
        
        print(f"  |- Accuracy:     {acc * 100:.2f}%")
        print(f"  |- Precision:    {prec * 100:.2f}%")
        print(f"  |- Recall:       {rec * 100:.2f}%")
        print(f"  |- F1 Score:     {f1 * 100:.2f}%")
        print(f"  |- 5-Fold CV:    {cv_mean * 100:.2f}% (+/- {cv_std * 100:.2f}%)")
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model_obj = model
            
    print("\n" + "-" * 60)
    print(f" BEST MODEL SELECTED: {best_model_name} (F1 Score: {best_f1 * 100:.2f}%)")
    print("-" * 60)
    
    return results, best_model_name, best_model_obj


def analyze_feature_importance(model, feature_names):
    """Computes feature importance if supported by the best model."""
    print("\n" + "=" * 60)
    print(" STEP 4: FEATURE IMPORTANCE ANALYSIS")
    print("=" * 60)
    
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        feature_importance_dict = dict(zip(feature_names, importances))
        sorted_importance = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)
        
        print(f"{'Feature':15s} | {'Importance Score':18s} | {'Percentage':10s}")
        print("-" * 50)
        for feat, imp in sorted_importance:
            print(f"{feat:15s} | {imp:18.6f} | {imp*100:6.2f}%")
            
        return dict(sorted_importance)
    else:
        print(f"[Notice] Model {type(model).__name__} does not expose feature_importances_.")
        return {}


def save_artifacts(model, label_encoder, output_dir: str):
    """Saves the trained model and label encoder as joblib pkl files."""
    print("\n" + "=" * 60)
    print(" STEP 5: SAVING MODEL & LABEL ENCODER ARTIFACTS")
    print("=" * 60)
    
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, "crop_recommendation_model.pkl")
    encoder_path = os.path.join(output_dir, "label_encoder.pkl")
    
    joblib.dump(model, model_path)
    joblib.dump(label_encoder, encoder_path)
    
    print(f" Saved Model:         {model_path} ({os.path.getsize(model_path) / 1024:.2f} KB)")
    print(f" Saved Label Encoder: {encoder_path} ({os.path.getsize(encoder_path) / 1024:.2f} KB)")


def run_pipeline():
    # Paths setup
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_path = os.path.join(base_dir, "dataset", "Crop_recommendation.csv")
    output_dir = os.path.join(base_dir, "models")
    
    print("Starting Kisan Mitra Crop Recommendation ML Pipeline...")
    print(f"Dataset Path: {dataset_path}")
    print(f"Output Models Directory: {output_dir}")
    
    # 1. Analysis
    df = load_dataset(dataset_path)
    analysis_stats = analyze_dataset(df)
    
    # 2. Preprocessing
    X_train, X_test, y_train, y_test, label_encoder, feature_names = preprocess_data(df)
    
    # 3. Model Training
    results, best_model_name, best_model_obj = train_and_evaluate_models(X_train, X_test, y_train, y_test)
    
    # 4. Feature Importance
    feature_importances = analyze_feature_importance(best_model_obj, feature_names)
    
    # 5. Save Artifacts
    save_artifacts(best_model_obj, label_encoder, output_dir)
    
    # 6. Detailed Classification Report for Best Model
    best_results = results[best_model_name]
    y_pred_best = best_results["predictions"]
    report_text = classification_report(y_test, y_pred_best, target_names=label_encoder.classes_)
    
    print("\n" + "=" * 60)
    print(f" CLASSIFICATION REPORT FOR BEST MODEL ({best_model_name})")
    print("=" * 60)
    print(report_text)
    
    print("\nML Pipeline executed successfully!")
    return {
        "analysis": analysis_stats,
        "results": results,
        "best_model_name": best_model_name,
        "feature_importances": feature_importances,
        "classification_report": report_text,
    }


if __name__ == "__main__":
    run_pipeline()
