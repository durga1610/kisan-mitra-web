import os
import sys
import json

# Ensure backend directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app, verify_token

# Override authentication dependency
app.dependency_overrides[verify_token] = lambda: {
    "uid": "test_mandi_user",
    "email": "test@kisanmitra.org",
    "name": "Mandi Auditor"
}

app.state.limiter.enabled = False
client = TestClient(app)

def test_crops():
    crops_to_check = ["Tomato", "Potato", "Onion", "Rice", "Cotton"]
    print("Running Market Prices Proxy Validation...")
    
    # 1. Fetch all crops
    res = client.get("/api/v1/market/prices")
    if res.status_code != 200:
        print(f"FAILED: Status Code: {res.status_code}")
        print(res.text)
        return
        
    data = res.json()
    print("\n--- GENERAL RESPONSE METADATA ---")
    print(f"Status Code: {res.status_code}")
    print(f"isFallback: {data.get('isFallback')}")
    print(f"lastUpdated: {data.get('lastUpdated')}")
    print(f"Total records returned: {len(data.get('records', []))}")
    
    # 2. Fetch specific crops
    crops_param = "Tomato,Potato,Onion,Rice,Cotton"
    res_filtered = client.get(f"/api/v1/market/prices?crops={crops_param}")
    data_filtered = res_filtered.json()
    
    print("\n--- SPECIFIC CROPS AUDIT ---")
    records = data_filtered.get("records", [])
    
    found_commodities = {}
    for r in records:
        comm = r.get("commodity")
        if comm not in found_commodities:
            found_commodities[comm] = []
        found_commodities[comm].append(r)
        
    for crop in crops_to_check:
        print(f"\nCrop: {crop}")
        matched = []
        for comm, recs in found_commodities.items():
            # Check commodity matches crop
            if crop.lower() in comm.lower() or (crop.lower() == "rice" and "paddy" in comm.lower()):
                matched.extend(recs)
                
        if matched:
            print(f"  API Response Status: {res_filtered.status_code}")
            print(f"  Data Source: {'Live API' if not data_filtered.get('isFallback') else 'Cached Fallback'}")
            for r in matched[:2]: # Show up to 2 records per crop
                print(f"  - Market: {r.get('market')}, District: {r.get('district')}, State: {r.get('state')}")
                print(f"    Min Price: Rs. {r.get('min_price')}")
                print(f"    Max Price: Rs. {r.get('max_price')}")
                print(f"    Modal Price: Rs. {r.get('modal_price')}")
                print(f"    Date: {r.get('arrival_date')}")
        else:
            print("  FAIL: No records found in fallback data")

if __name__ == "__main__":
    test_crops()
