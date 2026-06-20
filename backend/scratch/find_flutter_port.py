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
                match_ipv6 = re.search(r"\[::1\]:(\d+)", line)
                if match_ipv6:
                    ports.append(int(match_ipv6.group(1)))
                match_any = re.search(r"0\.0\.0\.0:(\d+)", line)
                if match_any:
                    ports.append(int(match_any.group(1)))
    except Exception as e:
        print("Error getting ports:", e)
    return sorted(list(set(ports)))

def check_port(port):
    url = f"http://127.0.0.1:{port}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=1) as response:
            html = response.read().decode('utf-8', errors='ignore')
            if "kisan" in html.lower() or "flutter" in html.lower():
                print(f"FOUND Flutter Web on Port: {port}")
                print(f"Content: {html[:300]}")
                return True
    except Exception:
        pass
    return False

def main():
    ports = get_listening_ports()
    print("Scanning ports:", ports)
    for p in ports:
        if check_port(p):
            return
    print("Finished scanning all listening ports.")

if __name__ == "__main__":
    main()
