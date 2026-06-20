import subprocess
import urllib.request
import re

def get_listening_ports():
    ports = []
    try:
        output = subprocess.check_output("netstat -ano", shell=True).decode()
        for line in output.splitlines():
            if "LISTENING" in line:
                match = re.search(r"127\.0\.0\.1:(\d+)", line)
                if match:
                    ports.append(int(match.group(1)))
                match_any = re.search(r"0\.0\.0\.0:(\d+)", line)
                if match_any:
                    ports.append(int(match_any.group(1)))
    except Exception as e:
        print("Error:", e)
    return sorted(list(set(ports)))

def main():
    ports = get_listening_ports()
    print("Testing ports:", ports)
    for p in ports:
        if p in [135, 445, 3306, 33060]: # Skip standard system/db ports to avoid hangs
            continue
        try:
            url = f"http://127.0.0.1:{p}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=1) as resp:
                print(f"Port {p} responded with HTTP {resp.getcode()}")
                html = resp.read().decode('utf-8', errors='ignore')
                print(f"  Snippet: {html[:150]}")
        except urllib.error.HTTPError as e:
            print(f"Port {p} responded with HTTPError {e.code}")
        except Exception as e:
            pass

if __name__ == "__main__":
    main()
