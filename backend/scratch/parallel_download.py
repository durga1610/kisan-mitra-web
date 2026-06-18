import os
import sys
import threading
import urllib.request
import time

URL = "https://prod-dcd-datasets-public-files-eu-west-1.s3.eu-west-1.amazonaws.com/31ba9629-b8af-49de-a0dc-de592ca903f9"
FILE_SIZE = 270591498
NUM_THREADS = 32
DEST_PATH = r"c:\Users\durga\kisan_mitra\backend\scratch\cotton_val.zip"

class DownloaderThread(threading.Thread):
    def __init__(self, url, start_byte, end_byte, thread_id, dest_file):
        threading.Thread.__init__(self)
        self.url = url
        self.start_byte = start_byte
        self.end_byte = end_byte
        self.thread_id = thread_id
        self.dest_file = dest_file
        self.downloaded = 0
        self.completed = False
        self.error = None

    def run(self):
        req = urllib.request.Request(self.url)
        req.add_header("Range", f"bytes={self.start_byte}-{self.end_byte}")
        req.add_header("User-Agent", "Mozilla/5.0")
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                # Open dest file and seek to start_byte
                with open(self.dest_file, "r+b") as f:
                    f.seek(self.start_byte)
                    chunk_size = 1024 * 1024 # 1MB chunks
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        self.downloaded += len(chunk)
            self.completed = True
        except Exception as e:
            self.error = e

def main():
    print(f"Pre-allocating file of size {FILE_SIZE} bytes...")
    # Pre-allocate empty file
    with open(DEST_PATH, "wb") as f:
        f.truncate(FILE_SIZE)

    chunk_size = FILE_SIZE // NUM_THREADS
    threads = []
    
    print(f"Launching {NUM_THREADS} download threads...")
    start_time = time.time()
    
    for i in range(NUM_THREADS):
        start_byte = i * chunk_size
        # Last thread takes any remainder
        end_byte = (i + 1) * chunk_size - 1 if i < NUM_THREADS - 1 else FILE_SIZE - 1
        
        t = DownloaderThread(URL, start_byte, end_byte, i, DEST_PATH)
        threads.append(t)
        t.start()

    while any(t.is_alive() for t in threads):
        total_downloaded = sum(t.downloaded for t in threads)
        percent = (total_downloaded / FILE_SIZE) * 100
        elapsed = time.time() - start_time
        speed = (total_downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        print(f"Progress: {percent:.1f}% ({total_downloaded / (1024*1024):.1f} MB / {FILE_SIZE / (1024*1024):.1f} MB) | Speed: {speed:.2f} MB/s", end="\r", flush=True)
        time.sleep(1)

    print("\nAll threads finished. Checking for errors...")
    success = True
    for t in threads:
        if not t.completed:
            print(f"Thread {t.thread_id} failed: {t.error}")
            success = False

    if success:
        print(f"Download complete in {time.time() - start_time:.2f} seconds!")
        sys.exit(0)
    else:
        print("Download failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
