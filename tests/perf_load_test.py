import asyncio
import time
import httpx
import numpy as np
import sys
import os

# Target URL can be overridden by env var or arg
TARGET_URL = os.getenv("LOAD_TEST_URL", "http://127.0.0.1:8000/")
CONCURRENCY = int(os.getenv("LOAD_TEST_CONCURRENCY", "100"))
DURATION = int(os.getenv("LOAD_TEST_DURATION", "60")) # seconds

async def worker(client, url, latencies, status_codes, stop_event):
    while not stop_event.is_set():
        start_time = time.perf_counter()
        try:
            response = await client.get(url, timeout=10.0)
            latency = (time.perf_counter() - start_time) * 1000 # ms
            latencies.append(latency)
            status_codes.append(response.status_code)
        except httpx.RequestError as e:
            latency = (time.perf_counter() - start_time) * 1000 # ms
            latencies.append(latency)
            status_codes.append(-1) # network error
        # Yield to event loop to avoid starvation and ensure concurrent scheduling
        await asyncio.sleep(0.001)

async def main():
    print("=" * 60)
    print(f" Kisan Mitra Baseline Load Testing ")
    print(f" Target URL: {TARGET_URL}")
    print(f" Concurrency: {CONCURRENCY} virtual users")
    print(f" Duration: {DURATION} seconds")
    print("=" * 60)
    
    latencies = []
    status_codes = []
    stop_event = asyncio.Event()
    
    # Pre-warm client connection pool
    limits = httpx.Limits(max_keepalive_connections=CONCURRENCY, max_connections=CONCURRENCY)
    async with httpx.AsyncClient(limits=limits, timeout=10.0) as client:
        # Create tasks for all virtual users
        tasks = [
            asyncio.create_task(worker(client, TARGET_URL, latencies, status_codes, stop_event))
            for _ in range(CONCURRENCY)
        ]
        
        start_time = time.time()
        print(f"[INFO] Started load test...")
        
        # Periodic progress updates
        for elapsed in range(10, DURATION + 1, 10):
            await asyncio.sleep(10)
            current_reqs = len(latencies)
            current_rps = current_reqs / elapsed
            print(f"[PROGRESS] {elapsed}s / {DURATION}s: {current_reqs} requests sent ({current_rps:.1f} RPS)")
            
        stop_event.set()
        await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
    # Analyze results
    total_reqs = len(latencies)
    if total_reqs == 0:
        print("[ERROR] No requests completed.")
        return
        
    status_counts = {}
    for code in status_codes:
        status_counts[code] = status_counts.get(code, 0) + 1
        
    successful = status_counts.get(200, 0)
    failed = total_reqs - successful
    rps = total_reqs / total_time
    
    avg_latency = np.mean(latencies)
    min_latency = np.min(latencies)
    max_latency = np.max(latencies)
    
    p50 = np.percentile(latencies, 50)
    p90 = np.percentile(latencies, 90)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)
    
    print("\n" + "=" * 60)
    print(" LOAD TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Duration:        {total_time:.2f} seconds")
    print(f"Total Requests:        {total_reqs}")
    print(f"Successful (200):      {successful} ({successful/total_reqs*100:.1f}%)")
    print(f"Failed (non-200/err):  {failed} ({failed/total_reqs*100:.1f}%)")
    print(f"Requests per Second:   {rps:.2f} RPS")
    print("-" * 60)
    print("Response Times (Latency):")
    print(f"  Minimum:             {min_latency:.2f} ms")
    print(f"  Average:             {avg_latency:.2f} ms")
    print(f"  Maximum:             {max_latency:.2f} ms")
    print(f"  50th Percentile:     {p50:.2f} ms")
    print(f"  90th Percentile:     {p90:.2f} ms")
    print(f"  95th Percentile:     {p95:.2f} ms")
    print(f"  99th Percentile:     {p99:.2f} ms")
    print("=" * 60)
    
    # Save a report file
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Vulnerability Test Results")
    os.makedirs(results_dir, exist_ok=True)
    report_path = os.path.join(results_dir, "load-test-report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Baseline Load Testing Report — Kisan Mitra AI\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Target URL:** `{TARGET_URL}`\n")
        f.write(f"**Concurrency:** {CONCURRENCY} virtual users\n")
        f.write(f"**Target Duration:** {DURATION} seconds\n\n")
        f.write(f"## Metrics Summary\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|---|---|\n")
        f.write(f"| **Total Requests Sent** | {total_reqs} |\n")
        f.write(f"| **Successful Requests (HTTP 200)** | {successful} ({successful/total_reqs*100:.1f}%) |\n")
        f.write(f"| **Failed Requests** | {failed} ({failed/total_reqs*100:.1f}%) |\n")
        f.write(f"| **Requests Per Second (RPS)** | **{rps:.2f} RPS** |\n")
        f.write(f"| **Min Latency** | {min_latency:.2f} ms |\n")
        f.write(f"| **Average Latency** | {avg_latency:.2f} ms |\n")
        f.write(f"| **Max Latency** | {max_latency:.2f} ms |\n")
        f.write(f"| **50th Percentile (Median)** | {p50:.2f} ms |\n")
        f.write(f"| **90th Percentile** | {p90:.2f} ms |\n")
        f.write(f"| **95th Percentile** | {p95:.2f} ms |\n")
        f.write(f"| **99th Percentile** | {p99:.2f} ms |\n\n")
        f.write(f"## Status Code Distribution\n\n")
        f.write(f"| Status Code | Count | Percentage |\n")
        f.write(f"|---|---|---|\n")
        for code, count in sorted(status_counts.items()):
            label = "HTTP " + str(code) if code > 0 else "Network Error"
            f.write(f"| {label} | {count} | {count/total_reqs*100:.1f}% |\n")
            
    print(f"\n[SUCCESS] Performance report written to {report_path}")

if __name__ == "__main__":
    asyncio.run(main())
