"""
Disease Model - Analysis Report Generator
Produces:
  1. Class distribution bar chart
  2. Confusion matrix heatmap (45×45)
  3. Top-20 most confused class pairs
All saved as PNG + printed to console.
"""
import json
import os
import numpy as np

# --- raw confusion matrix rows from evaluation_report.txt -------------------
RAW_CM = [
    # Apple___Black_Rot
    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,2,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Apple___Cedar_Apple_Rust
    [0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Apple___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Apple___Scab
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0],
    # Blueberry___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Cherry___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Cherry___Powdery_Mildew
    [0,0,0,0,0,0,4,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Corn___Common_Rust
    [0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Corn___Gray_Leaf_Spot
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Corn___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Corn___Northern_Leaf_Blight
    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Cotton___Bacterial_Blight
    [0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Cotton___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Cotton___Leaf_Curl
    [0,0,0,0,0,0,4,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Grape___Black_Rot
    [0,0,0,0,0,0,0,0,1,0,2,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Grape___Esca
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0],
    # Grape___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Grape___Leaf_Blight
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Orange___Haunglongbing
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0],
    # Peach___Bacterial_Spot
    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,2,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Peach___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Pepper_Bell___Bacterial_Spot
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
    # Pepper_Bell___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Potato___Early_Blight
    [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Potato___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Potato___Late_Blight
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Raspberry___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Rice___Bacterial_Leaf_Blight
    [0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Rice___Blast
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0],
    # Rice___Brown_Spot
    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
    # Rice___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Soybean___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Squash___Powdery_Mildew
    [0,0,0,0,0,0,4,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Strawberry___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Strawberry___Leaf_Scorch
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0],
    # Tomato___Bacterial_Spot
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,3,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Tomato___Early_Blight
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,2,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Tomato___Healthy
    [0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Tomato___Late_Blight
    [0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Tomato___Leaf_Mold
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0],
    # Tomato___Mosaic_Virus
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0],
    # Tomato___Septoria_Leaf_Spot
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Tomato___Spider_Mites
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
    # Tomato___Target_Spot
    [0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    # Tomato___Yellow_Leaf_Curl_Virus
    [0,0,0,0,0,0,4,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]

CLASSES = [
    "Apple___Black_Rot","Apple___Cedar_Apple_Rust","Apple___Healthy","Apple___Scab",
    "Blueberry___Healthy","Cherry___Healthy","Cherry___Powdery_Mildew",
    "Corn___Common_Rust","Corn___Gray_Leaf_Spot","Corn___Healthy",
    "Corn___Northern_Leaf_Blight","Cotton___Bacterial_Blight","Cotton___Healthy",
    "Cotton___Leaf_Curl","Grape___Black_Rot","Grape___Esca","Grape___Healthy",
    "Grape___Leaf_Blight","Orange___Haunglongbing","Peach___Bacterial_Spot",
    "Peach___Healthy","Pepper_Bell___Bacterial_Spot","Pepper_Bell___Healthy",
    "Potato___Early_Blight","Potato___Healthy","Potato___Late_Blight",
    "Raspberry___Healthy","Rice___Bacterial_Leaf_Blight","Rice___Blast",
    "Rice___Brown_Spot","Rice___Healthy","Soybean___Healthy",
    "Squash___Powdery_Mildew","Strawberry___Healthy","Strawberry___Leaf_Scorch",
    "Tomato___Bacterial_Spot","Tomato___Early_Blight","Tomato___Healthy",
    "Tomato___Late_Blight","Tomato___Leaf_Mold","Tomato___Mosaic_Virus",
    "Tomato___Septoria_Leaf_Spot","Tomato___Spider_Mites","Tomato___Target_Spot",
    "Tomato___Yellow_Leaf_Curl_Virus",
]

# Short labels for axis ticks
SHORT = [c.replace("___", "\n").replace("_", " ") for c in CLASSES]
TICKER = [c.split("___")[0][:4] + "/" + c.split("___")[1][:10] for c in CLASSES]

cm = np.array(RAW_CM)
num_classes = len(CLASSES)
samples_per_class = cm.sum(axis=1)

# --- Per-class metrics -------------------------------------------------------
correct = np.diag(cm)
per_class_acc = np.where(samples_per_class > 0, correct / samples_per_class, 0.0)
overall_acc   = correct.sum() / samples_per_class.sum()

print("="*72)
print("  KISAN MITRA - DISEASE MODEL EVALUATION REPORT")
print("="*72)
print(f"  Overall Accuracy : {overall_acc*100:.2f}%")
print(f"  Total Test Samples: {int(samples_per_class.sum())}  |  Classes: {num_classes}")
print("="*72)

# -----------------------------------------------------------------------------
# 1. CLASS DISTRIBUTION REPORT
# -----------------------------------------------------------------------------
print("\n----------------------------------------------------------------------")
print("  1. CLASS DISTRIBUTION REPORT")
print("----------------------------------------------------------------------")
print(f"  {'Class':<40} {'Samples':>7}  {'Correct':>7}  {'Accuracy':>8}")
print("  " + "-"*68)
for i, cls in enumerate(CLASSES):
    n = int(samples_per_class[i])
    c = int(correct[i])
    a = per_class_acc[i] * 100
    bar = "#" * c + "." * (n - c)
    print(f"  {cls:<40} {n:>7}  {c:>7}  {a:>7.1f}%  {bar}")

# -----------------------------------------------------------------------------
# 2. CONFUSION MATRIX (ASCII heat map in console)
# -----------------------------------------------------------------------------
print("\n----------------------------------------------------------------------")
print("  2. CONFUSION MATRIX HEATMAP  (saved as PNG)")
print("----------------------------------------------------------------------")

try:
    import matplotlib
    matplotlib.use("Agg")          # non-interactive backend for server environments
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    OUT_DIR = os.getcwd()

    # -- 2a. Confusion matrix PNG --------------------------------------------
    fig, ax = plt.subplots(figsize=(22, 20))
    # normalise per row so colours show where each class GOES
    cm_norm = cm.astype(float)
    row_sums = cm_norm.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    cm_pct = cm_norm / row_sums

    im = ax.imshow(cm_pct, cmap="YlOrRd", vmin=0, vmax=1)
    ax.set_xticks(range(num_classes))
    ax.set_yticks(range(num_classes))
    ax.set_xticklabels(TICKER, rotation=90, fontsize=7)
    ax.set_yticklabels(TICKER, fontsize=7)
    ax.set_xlabel("Predicted Class", fontsize=12, labelpad=10)
    ax.set_ylabel("True Class", fontsize=12, labelpad=10)
    ax.set_title("Disease Model - Normalised Confusion Matrix (row = true class)", fontsize=14, pad=15)

    # annotate cells with raw counts (skip zeros for readability)
    for i in range(num_classes):
        for j in range(num_classes):
            v = cm[i, j]
            if v > 0:
                color = "white" if cm_pct[i, j] > 0.55 else "black"
                ax.text(j, i, str(v), ha="center", va="center", fontsize=6, color=color)

    plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02, label="Fraction of true class samples")
    plt.tight_layout()
    cm_path = os.path.join(OUT_DIR, "confusion_matrix_full.png")
    plt.savefig(cm_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {cm_path}")

    # -- 2b. Class distribution bar chart PNG --------------------------------
    fig, ax = plt.subplots(figsize=(18, 8))
    x = np.arange(num_classes)
    bars_total   = ax.bar(x, samples_per_class, color="#dce8f5", edgecolor="#aaaaaa", label="Total samples")
    bars_correct = ax.bar(x, correct,           color="#3a7abf", edgecolor="#2255a0", label="Correctly predicted")
    ax.set_xticks(x)
    ax.set_xticklabels(TICKER, rotation=90, fontsize=7)
    ax.set_ylabel("Number of samples", fontsize=11)
    ax.set_title("Class Distribution & Per-Class Accuracy - Disease Detection Model", fontsize=13)
    ax.legend(fontsize=10)
    ax.set_ylim(0, max(samples_per_class) * 1.25)
    # annotate accuracy %
    for i in range(num_classes):
        ax.text(i, samples_per_class[i] + 0.15, f"{per_class_acc[i]*100:.0f}%",
                ha="center", va="bottom", fontsize=6, color="#cc3300",
                rotation=90 if num_classes > 20 else 0)
    plt.tight_layout()
    dist_path = os.path.join(OUT_DIR, "class_distribution.png")
    plt.savefig(dist_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {dist_path}")

except ImportError:
    print("  matplotlib not available - skipping PNG generation.")

# -----------------------------------------------------------------------------
# 3. TOP-20 MOST CONFUSED PAIRS
# -----------------------------------------------------------------------------
print("\n----------------------------------------------------------------------")
print("  3. TOP-20 MOST CONFUSED CLASS PAIRS  (True -> Predicted, off-diagonal)")
print("----------------------------------------------------------------------")
print(f"  {'#':<3} {'True Class':<40} {'Predicted As':<40} {'Count':>5}  {'% of true':>9}")
print("  " + "-"*100)

confusions = []
for i in range(num_classes):
    for j in range(num_classes):
        if i != j and cm[i, j] > 0:
            pct = cm[i, j] / samples_per_class[i] * 100 if samples_per_class[i] > 0 else 0.0
            confusions.append((cm[i, j], pct, CLASSES[i], CLASSES[j]))

confusions.sort(key=lambda x: (-x[0], -x[1]))

for rank, (count, pct, true_cls, pred_cls) in enumerate(confusions[:20], 1):
    print(f"  {rank:<3} {true_cls:<40} {pred_cls:<40} {int(count):>5}  {pct:>8.1f}%")

# --- Summary recommendations -------------------------------------------------
print("\n----------------------------------------------------------------------")
print("  KEY FINDINGS & RECOMMENDATIONS")
print("----------------------------------------------------------------------")

# most predicted class
pred_counts = cm.sum(axis=0)
top_pred_idx = int(np.argmax(pred_counts))
print(f"  • Model heavily predicts '{CLASSES[top_pred_idx]}' ({int(pred_counts[top_pred_idx])} times out of {int(cm.sum())} total)")
print(f"  • Zero-accuracy classes : ", end="")
zero_acc = [CLASSES[i] for i in range(num_classes) if per_class_acc[i] == 0]
print(f"{len(zero_acc)} classes (e.g. {', '.join(zero_acc[:4])}...)")
perfect_acc = [CLASSES[i] for i in range(num_classes) if per_class_acc[i] == 1.0]
print(f"  • Perfect-accuracy classes: {len(perfect_acc)} ({', '.join(perfect_acc[:4])}...)")
print(f"  • Recommendation: Retrain with larger dataset (10k+ images/class), data augmentation,")
print(f"    and class-balanced sampling. Consider fine-tuning EfficientNet-B4 with unfrozen layers.")
print("="*72)
