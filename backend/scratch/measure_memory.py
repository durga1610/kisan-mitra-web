import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gc
import time

def get_memory_use_mb():
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    except ImportError:
        # Fallback to reading from OS if on linux
        try:
            with open('/proc/self/status') as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        return float(line.split()[1]) / 1024
        except Exception:
            pass
        return 0.0

def main():
    print("--- Starting Kisan Mitra Memory Profiler ---")
    log_lines = []
    
    # 1. Baseline Memory
    baseline = get_memory_use_mb()
    log_lines.append(f"| Baseline Start | {baseline:.2f} MB | Initial process startup, standard libraries only. |")
    print(f"Baseline: {baseline:.2f} MB")
    
    # 2. Import PyTorch
    t0 = time.time()
    import torch
    t_import_torch = time.time() - t0
    mem_torch = get_memory_use_mb()
    log_lines.append(f"| PyTorch Imported | {mem_torch:.2f} MB | Imported `torch` library. Duration: {t_import_torch:.2f}s |")
    print(f"After torch import: {mem_torch:.2f} MB")
    
    # 3. Setup Database and config imports
    t0 = time.time()
    from config import DB_PATH
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.close()
    t_db = time.time() - t0
    mem_db = get_memory_use_mb()
    log_lines.append(f"| Config & DB Init | {mem_db:.2f} MB | Config files and DB connection check. Duration: {t_db:.2f}s |")
    print(f"After DB Init: {mem_db:.2f} MB")
    
    # 4. Import Advisory Engine & SentenceTransformer
    t0 = time.time()
    # SentenceTransformer is imported/initialized via advisory_engine resource init
    # Let's import advisory_engine first
    import advisory_engine
    mem_adv_import = get_memory_use_mb()
    print(f"After Advisory Engine import: {mem_adv_import:.2f} MB")
    
    # Run advisory engine resource init (loads sentence transformer models)
    advisory_engine.init_resources()
    t_adv_resources = time.time() - t0
    mem_adv_resources = get_memory_use_mb()
    log_lines.append(f"| SentenceTransformer Load | {mem_adv_resources:.2f} MB | Loaded text embeds model in RAG engine. Duration: {t_adv_resources:.2f}s |")
    print(f"After Advisory Engine Resource Init: {mem_adv_resources:.2f} MB")
    
    # 5. Load Fallback ResNet18 (default primary CNN)
    t0 = time.time()
    # We will import main to see fallback_resnet execution
    import main
    # Wait, importing main triggers init_disease_model, which loads fallback_resnet (since crop_model.pt doesn't exist)
    mem_main_import = get_memory_use_mb()
    t_main_import = time.time() - t0
    log_lines.append(f"| Default ResNet18 Load | {mem_main_import:.2f} MB | Loaded default ResNet18 CNN model. Duration: {t_main_import:.2f}s |")
    print(f"After main import (Default ResNet18): {mem_main_import:.2f} MB")
    
    # 6. Load Legacy ResNet18 Model (On-demand)
    t0 = time.time()
    main.init_legacy_model()
    t_legacy_load = time.time() - t0
    mem_legacy = get_memory_use_mb()
    log_lines.append(f"| Legacy ResNet18 Load | {mem_legacy:.2f} MB | Loaded legacy ResNet18 model on-demand. Duration: {t_legacy_load:.2f}s |")
    print(f"After Legacy ResNet18: {mem_legacy:.2f} MB")
    
    # Generate report
    report_content = f"""# Render Memory Audit Report

This report outlines the memory consumption profile of the Kisan Mitra backend startup and model-loading sequence, focusing on staying under the Render Free Tier limit (512MB RAM).

## Memory Consumption Timeline

| Initialization Phase | Memory (RSS) | Description |
| :--- | :--- | :--- |
{os.linesep.join(log_lines)}

## Key Findings

1. **PyTorch Overhead**: Importing PyTorch alone allocates a significant portion of memory.
2. **Dynamic Legacy Model Loading**: By deferring the legacy ResNet18 model weight loading, we save **~{mem_legacy - mem_main_import:.1f} MB** of RAM at startup. It is only allocated if a legacy crop request (e.g. apple, peach, cherry) is received.
3. **Total Idle Footprint**: The idle startup memory of the server is **{mem_main_import:.1f} MB**, leaving **~{512.0 - mem_main_import:.1f} MB** of free headspace on the Render 512MB limit, ensuring stable runtime execution.

## Recommendations
* Keep `USE_TWO_STAGE_MODEL` set to `0` (default) on Render to prevent loading the heavy two-stage EfficientNet models.
* Dynamic legacy loading is critical to prevent out-of-memory (OOM) restarts on Render.
"""
    
    artifact_dir = r"C:\Users\durga\.gemini\antigravity-ide\brain\ffa2701b-34c2-4911-b6a3-3afe2b289ce5"
    os.makedirs(artifact_dir, exist_ok=True)
    report_path = os.path.join(artifact_dir, "render_memory_audit.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"Memory audit report successfully written to {report_path}")

if __name__ == "__main__":
    main()
