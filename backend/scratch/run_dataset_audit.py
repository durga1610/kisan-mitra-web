"""
Disease Dataset Audit Script
Counts images per class across train/val/test splits,
detects synthetic vs real, computes imbalance ratios.
"""
import os
import json
import re
from collections import defaultdict

DATASET_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dataset")
SPLITS = ["train", "val", "test"]

# Patterns that indicate synthetic/augmented images
SYNTH_PATTERNS = [
    r"synth",
    r"_aug_",
    r"augmented",
    r"generated",
    r"fake",
    r"_flip",
    r"_rot",
    r"_bright",
    r"_contrast",
    r"_zoom",
]

def is_synthetic(filename):
    name = filename.lower()
    return any(re.search(p, name) for p in SYNTH_PATTERNS)

def audit_dataset():
    report = {}
    all_classes = set()

    for split in SPLITS:
        split_dir = os.path.join(DATASET_ROOT, split)
        if not os.path.exists(split_dir):
            print(f"[WARN] Split dir not found: {split_dir}")
            continue

        split_report = {}
        for cls in sorted(os.listdir(split_dir)):
            cls_dir = os.path.join(split_dir, cls)
            if not os.path.isdir(cls_dir):
                continue
            all_classes.add(cls)
            files = [f for f in os.listdir(cls_dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
            synth = [f for f in files if is_synthetic(f)]
            real = [f for f in files if not is_synthetic(f)]
            split_report[cls] = {
                "total": len(files),
                "real": len(real),
                "synthetic": len(synth),
                "synth_pct": round(len(synth) / len(files) * 100, 1) if files else 0.0,
            }

        report[split] = split_report

    # ─── Cross-split analysis ────────────────────────────────────────────
    cross = {}
    for cls in sorted(all_classes):
        total = sum(report[s].get(cls, {}).get("total", 0) for s in SPLITS)
        real  = sum(report[s].get(cls, {}).get("real", 0) for s in SPLITS)
        synth = sum(report[s].get(cls, {}).get("synthetic", 0) for s in SPLITS)
        cross[cls] = {
            "total": total,
            "real": real,
            "synthetic": synth,
            "synth_pct": round(synth / total * 100, 1) if total else 0.0,
        }

    # ─── Crop-level grouping ─────────────────────────────────────────────
    crop_totals = defaultdict(int)
    crop_diseased = defaultdict(int)
    crop_healthy  = defaultdict(int)
    for cls, info in cross.items():
        crop = cls.split("___")[0]
        crop_totals[crop] += info["total"]
        if "Healthy" in cls or "Plant_Healthy" == cls:
            crop_healthy[crop] += info["total"]
        else:
            crop_diseased[crop] += info["total"]

    # ─── Imbalance metrics ────────────────────────────────────────────────
    class_totals = [(cls, info["total"]) for cls, info in cross.items()]
    class_totals.sort(key=lambda x: x[1], reverse=True)
    max_cls, max_count = class_totals[0]
    min_cls, min_count = class_totals[-1]
    imbalance_ratio = round(max_count / min_count, 2) if min_count > 0 else float("inf")

    # ─── Print summary ────────────────────────────────────────────────────
    print("=" * 80)
    print("  KISAN MITRA DISEASE DATASET AUDIT")
    print("=" * 80)
    print(f"\nTotal unique classes: {len(all_classes)}")
    grand_total = sum(v["total"] for v in cross.values())
    grand_real  = sum(v["real"] for v in cross.values())
    grand_synth = sum(v["synthetic"] for v in cross.values())
    print(f"Grand total images  : {grand_total}")
    print(f"  Real              : {grand_real}")
    print(f"  Synthetic/Aug     : {grand_synth}")
    print(f"  Synth %           : {round(grand_synth/grand_total*100,1) if grand_total else 0}%")
    print(f"\nLargest class : {max_cls} ({max_count})")
    print(f"Smallest class: {min_cls} ({min_count})")
    print(f"Imbalance ratio (max/min): {imbalance_ratio}x")

    print("\n--- Per-class totals (train+val+test) ---")
    print(f"{'Class':<45} {'Total':>6} {'Real':>6} {'Synth':>6} {'S%':>5}")
    print("-" * 75)
    healthy_total = 0
    diseased_total = 0
    for cls, info in sorted(cross.items(), key=lambda x: x[1]["total"], reverse=True):
        marker = " [H]" if "Healthy" in cls else ""
        print(f"{cls:<45} {info['total']:>6} {info['real']:>6} {info['synthetic']:>6} {info['synth_pct']:>4.1f}%{marker}")
        if "Healthy" in cls:
            healthy_total += info["total"]
        else:
            diseased_total += info["total"]

    print(f"\nHealthy images  : {healthy_total}")
    print(f"Diseased images : {diseased_total}")
    if diseased_total > 0:
        print(f"Healthy/Disease ratio: {round(healthy_total/diseased_total,2)}x")

    print("\n--- Crop coverage ---")
    print(f"{'Crop':<25} {'Total':>7} {'Healthy':>8} {'Diseased':>9}")
    print("-" * 55)
    for crop in sorted(crop_totals.keys()):
        print(f"{crop:<25} {crop_totals[crop]:>7} {crop_healthy[crop]:>8} {crop_diseased[crop]:>9}")

    # ─── Build JSON output for report generation ──────────────────────────
    return {
        "per_split": report,
        "cross_split": cross,
        "crop_totals": dict(crop_totals),
        "crop_healthy": dict(crop_healthy),
        "crop_diseased": dict(crop_diseased),
        "summary": {
            "total_classes": len(all_classes),
            "grand_total": grand_total,
            "grand_real": grand_real,
            "grand_synth": grand_synth,
            "synth_pct": round(grand_synth / grand_total * 100, 1) if grand_total else 0.0,
            "healthy_total": healthy_total,
            "diseased_total": diseased_total,
            "largest_class": max_cls,
            "largest_class_count": max_count,
            "smallest_class": min_cls,
            "smallest_class_count": min_count,
            "imbalance_ratio": imbalance_ratio,
        }
    }

if __name__ == "__main__":
    data = audit_dataset()
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_audit_raw.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nRaw data saved to: {out_path}")
