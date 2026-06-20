import sys
import os
import io
import json
import numpy as np
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app, verify_token

app.dependency_overrides[verify_token] = lambda: {
    "uid": "validation_test_user",
    "email": "testfarmer@example.com",
    "name": "Validation Farmer"
}
app.state.limiter.enabled = False

client = TestClient(app)

img_np = np.random.randint(50, 150, (256, 256, 3), dtype=np.uint8)
img_np[:, :, 1] = 200
img = Image.fromarray(img_np)
img_bytes = io.BytesIO()
img.save(img_bytes, format="PNG")
img_data = img_bytes.getvalue()

res = client.post(
    "/api/v1/disease/detect",
    files={"file": ("spinach_leaf.png", img_data, "image/png")},
    data={"crop": "spinach", "language": "en"},
    headers={"Authorization": "Bearer dummy_token"}
)

print("Status code:", res.status_code)
res_data = res.json()
print("Response keys:", list(res_data.keys()))

# Check which value has "n/a"
for k, v in res_data.items():
    if isinstance(v, str) and "n/a" in v.lower():
        print(f"Key '{k}' contains 'n/a': {v[:100]}...")
