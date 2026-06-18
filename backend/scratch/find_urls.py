import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://data.mendeley.com/public-api/datasets/b3jy2p6k8w"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        body = response.read()
        data = json.loads(body.decode('utf-8'))
        print("Root keys:", list(data.keys()))
        # print first item of files list keys
        if "files" in data and len(data["files"]) > 0:
            print("File 0 keys:", list(data["files"][0].keys()))
            print("File 0 data:", data["files"][0])
            print("File 1 data:", data["files"][1])
except Exception as e:
    print("Error:", e)
