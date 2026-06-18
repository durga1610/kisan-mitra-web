import os
import subprocess
import shutil

temp_dir = r"c:\Users\durga\kisan_mitra\dataset_temp"
pv_git_dir = os.path.join(temp_dir, "plantvillage_git")

if os.path.exists(pv_git_dir):
    shutil.rmtree(pv_git_dir)
os.makedirs(pv_git_dir, exist_ok=True)

print("Initializing git repo for PlantVillage sparse-checkout...")
try:
    # Git init
    subprocess.run(["git", "init"], cwd=pv_git_dir, check=True)
    # Add remote
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/spMohanty/PlantVillage-Dataset.git"], cwd=pv_git_dir, check=True)
    # Enable sparse checkout
    subprocess.run(["git", "config", "core.sparseCheckout", "true"], cwd=pv_git_dir, check=True)
    
    # Write sparse checkout patterns
    sparse_file = os.path.join(pv_git_dir, ".git", "info", "sparse-checkout")
    with open(sparse_file, "w") as f:
        f.write("raw/color/Grape*\n")
        f.write("raw/color/Tomato*\n")
        f.write("raw/color/Potato*\n")
        
    print("Pulling Grape, Tomato, Potato color images (sparse, depth 1)...")
    subprocess.run(["git", "pull", "--depth", "1", "origin", "master"], cwd=pv_git_dir, check=True)
    print("PlantVillage download complete.")
    
    # List the downloaded folders
    color_dir = os.path.join(pv_git_dir, "raw", "color")
    if os.path.exists(color_dir):
        print("Downloaded folders:")
        for folder in sorted(os.listdir(color_dir)):
            print(f"- {folder}: {len(os.listdir(os.path.join(color_dir, folder)))} files")
    else:
        print("Error: raw/color directory not found!")
except Exception as e:
    print("Error during sparse checkout:", e)
