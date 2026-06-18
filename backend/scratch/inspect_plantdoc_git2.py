import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://api.github.com/repos/pratikkayal/PlantDoc-Dataset/contents/train"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
        metadata = json.loads(response.read().decode('utf-8'))
        for item in metadata:
            print(item['name'])
except Exception as e:
    print("Error:", e)
