import urllib.request
import urllib.error
import json
import ssl

def main():
    # URL template
    base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    
    # We will try a few requests to diagnose:
    # 1. No API key
    # 2. Dummy API key
    # 3. Check if we can find any other endpoint ID
    
    urls = [
        ("No Key", f"{base_url}?format=json&limit=5"),
        ("Dummy Key", f"{base_url}?api-key=dummy_key&format=json&limit=5")
    ]
    
    # Bypass SSL verification if needed for government APIs
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for label, url in urls:
        print(f"\n--- Testing: {label} ---")
        print(f"URL: {url}")
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                code = response.getcode()
                body = response.read().decode('utf-8')
                print(f"Status Code: {code}")
                print(f"Headers: {dict(response.headers)}")
                print(f"Body (truncated): {body[:500]}")
        except urllib.error.HTTPError as e:
            print(f"HTTPError Status Code: {e.code}")
            print(f"HTTPError Headers: {dict(e.headers)}")
            try:
                body = e.read().decode('utf-8')
                print(f"HTTPError Body: {body}")
            except Exception:
                print("Could not read error body")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    main()
