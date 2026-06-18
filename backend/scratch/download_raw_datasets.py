import os
import urllib.request
import zipfile
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

temp_dir = r"c:\Users\durga\kisan_mitra\dataset_temp"
os.makedirs(temp_dir, exist_ok=True)

# 1. Download Rice
rice_url = "https://github.com/AveyBD/rice-leaf-diseases-detection/raw/master/rice-leaf.zip"
rice_zip = os.path.join(temp_dir, "rice.zip")
print("Downloading Rice dataset...")
try:
    urllib.request.urlretrieve(rice_url, rice_zip)
    print("Rice downloaded. Extracting...")
    with zipfile.ZipFile(rice_zip, 'r') as zip_ref:
        zip_ref.extractall(os.path.join(temp_dir, "rice_extracted"))
    print("Rice extracted.")
    print("Rice extracted folders:", os.listdir(os.path.join(temp_dir, "rice_extracted")))
except Exception as e:
    print("Error with Rice:", e)

# 2. Download Cotton
cotton_url = "https://data.mendeley.com/public-files/datasets/b3jy2p6k8w/files/9a365367-8a96-4c15-8bcc-a533ab79c7d6/file_downloaded"
cotton_zip = os.path.join(temp_dir, "cotton.zip")
print("\nDownloading Cotton dataset (270MB)...")
try:
    req = urllib.request.Request(cotton_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx) as response:
        with open(cotton_zip, "wb") as f:
            f.write(response.read())
    print("Cotton downloaded. Extracting...")
    with zipfile.ZipFile(cotton_zip, 'r') as zip_ref:
        zip_ref.extractall(os.path.join(temp_dir, "cotton_extracted"))
    print("Cotton extracted.")
    print("Cotton extracted folders:", os.listdir(os.path.join(temp_dir, "cotton_extracted")))
except Exception as e:
    print("Error with Cotton:", e)
