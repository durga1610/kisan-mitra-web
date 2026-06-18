import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://api.github.com/repos/pratikkayal/PlantDoc-Object-Detection-Dataset/contents/TEST"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
        metadata = json.loads(response.read().decode('utf-8'))
        print("Number of items in TEST:", len(metadata))
        print("First 20 items:")
        for item in metadata[:20]:
            print(f"- {item['name']} ({item['type']})")
except Exception as e:
    print("Error:", e)
