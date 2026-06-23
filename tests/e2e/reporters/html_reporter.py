import os
import json
from datetime import datetime

# Load test case metadata for lookup
def load_metadata_map():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "test_cases.json")
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                tcs = json.load(f)
                return {tc["id"]: tc for tc in tcs}
        except Exception:
            pass
    return {}

def enrich_results(test_results):
    tc_map = load_metadata_map()
    enriched = []
    for idx, r in enumerate(test_results, 1):
        name = r["name"]
        test_id = f"TC_GEN_{idx:03}"
        
        if "[" in name and "]" in name:
            extracted_id = name.split("[")[-1].split("]")[0]
            if extracted_id in tc_map:
                test_id = extracted_id
                
        meta = tc_map.get(test_id, {})
        enriched.append({
            "id": test_id,
            "module": meta.get("module", "General"),
            "name": meta.get("name", name),
            "priority": meta.get("priority", "Medium"),
            "status": r["status"].lower(),
            "execution_time": r["duration"],
            "timestamp": r["timestamp"],
            "error": r.get("error", "")
        })
    return enriched

def generate_html_report(test_results, output_path):
    """Generates execution-report.html (Detailed test grid list)."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    enriched = enrich_results(test_results)
    
    total = len(enriched)
    passed = sum(1 for r in enriched if r["status"] == "passed")
    failed = sum(1 for r in enriched if r["status"] == "failed")
    skipped = sum(1 for r in enriched if r["status"] == "skipped")
    pass_pct = (passed / total * 100) if total > 0 else 0
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kisan Mitra Web - Execution Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0F172A;
            --card-bg: #1E293B;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --primary: #3B82F6;
            --success: #10B981;
            --error: #EF4444;
            --warning: #F59E0B;
            --border-color: #334155;
        }}
        
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Outfit', sans-serif;
            margin: 0;
            padding: 24px;
        }}
        
        .container {{
            max-width: 1300px;
            margin: 0 auto;
        }}
        
        header {{
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        h1 {{
            margin: 0 0 4px 0;
            font-size: 24px;
            color: var(--primary);
        }}
        
        .meta {{
            font-size: 13px;
            color: var(--text-muted);
        }}
        
        .meta a {{
            color: var(--primary);
            text-decoration: none;
        }}
        
        .nav-links a {{
            color: var(--text-muted);
            text-decoration: none;
            margin-left: 16px;
            font-weight: 600;
            font-size: 14px;
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }}
        
        .nav-links a:hover, .nav-links a.active {{
            color: var(--text-main);
            background-color: var(--border-color);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}
        
        .stat-card {{
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid var(--border-color);
            text-align: center;
        }}
        
        .stat-label {{
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        
        .stat-val {{
            font-size: 24px;
            font-weight: 700;
        }}
        
        .stat-val.passed {{ color: var(--success); }}
        .stat-val.failed {{ color: var(--error); }}
        .stat-val.skipped {{ color: var(--warning); }}
        
        .filter-section {{
            margin-bottom: 16px;
            display: flex;
            gap: 12px;
        }}
        
        .filter-btn {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-family: inherit;
        }}
        
        .filter-btn.active {{
            background-color: var(--primary);
            color: var(--text-main);
            font-weight: 600;
            border-color: var(--primary);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}
        
        th, td {{
            padding: 12px 16px;
            font-size: 13px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        th {{
            background-color: rgba(255, 255, 255, 0.02);
            color: var(--text-muted);
            font-weight: 600;
        }}
        
        tr:hover td {{
            background-color: rgba(255, 255, 255, 0.01);
        }}
        
        .badge {{
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        
        .badge.passed {{ background-color: rgba(52, 211, 153, 0.1); color: var(--success); }}
        .badge.failed {{ background-color: rgba(248, 113, 113, 0.1); color: var(--error); }}
        .badge.skipped {{ background-color: rgba(251, 191, 36, 0.1); color: var(--warning); }}
        
        .error-log {{
            font-family: monospace;
            background-color: #0F172A;
            padding: 10px;
            border-radius: 6px;
            color: #FECACA;
            font-size: 11px;
            max-width: 400px;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Kisan Mitra Web Selenium E2E Execution Details</h1>
                <div class="meta">Run Date: <strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</strong> | Build: <strong>#{os.getenv("GITHUB_RUN_NUMBER", "1")}</strong></div>
            </div>
            <div class="nav-links">
                <a href="execution-report.html" class="active">Grid View</a>
                <a href="dashboard.html">Dashboard</a>
            </div>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">Total</div><div class="stat-val">{total}</div></div>
            <div class="stat-card"><div class="stat-label">Passed</div><div class="stat-val passed">{passed}</div></div>
            <div class="stat-card"><div class="stat-label">Failed</div><div class="stat-val failed">{failed}</div></div>
            <div class="stat-card"><div class="stat-label">Skipped</div><div class="stat-val skipped">{skipped}</div></div>
            <div class="stat-card"><div class="stat-label">Pass Rate</div><div class="stat-val">{pass_pct:.1f}%</div></div>
        </div>
        
        <div class="filter-section">
            <button class="filter-btn active" onclick="filterTable('all', this)">All</button>
            <button class="filter-btn" onclick="filterTable('passed', this)">Passed</button>
            <button class="filter-btn" onclick="filterTable('failed', this)">Failed</button>
            <button class="filter-btn" onclick="filterTable('skipped', this)">Skipped</button>
        </div>
        
        <table id="test-table">
            <thead>
                <tr>
                    <th>Test ID</th>
                    <th>Module</th>
                    <th>Name</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Timestamp</th>
                    <th>Console Trace Log</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for r in enriched:
        err_div = f'<div class="error-log">{r["error"]}</div>' if r["error"] else ""
        html += f"""                <tr class="test-row {r['status']}">
                    <td><strong>{r['id']}</strong></td>
                    <td>{r['module']}</td>
                    <td>{r['name']}</td>
                    <td>{r['priority']}</td>
                    <td><span class="badge {r['status']}">{r['status']}</span></td>
                    <td>{r['execution_time']:.2f}s</td>
                    <td>{r['timestamp']}</td>
                    <td>{err_div}</td>
                </tr>
"""
        
    html += """            </tbody>
        </table>
    </div>
    
    <script>
        function filterTable(status, btn) {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            document.querySelectorAll('.test-row').forEach(row => {
                if (status === 'all') {
                    row.style.display = '';
                } else if (row.classList.contains(status)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[HTMLReporter] execution-report.html compiled.")

def generate_dashboard_report(test_results, output_path):
    """Generates dashboard.html (Visual charts)."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    enriched = enrich_results(test_results)
    
    total = len(enriched)
    passed = sum(1 for r in enriched if r["status"] == "passed")
    failed = sum(1 for r in enriched if r["status"] == "failed")
    skipped = sum(1 for r in enriched if r["status"] == "skipped")
    
    pass_pct = (passed / total * 100) if total > 0 else 0
    fail_pct = (failed / total * 100) if total > 0 else 0
    skip_pct = (skipped / total * 100) if total > 0 else 0
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kisan Mitra Web - Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0F172A;
            --card-bg: #1E293B;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --primary: #3B82F6;
            --success: #10B981;
            --error: #EF4444;
            --warning: #F59E0B;
            --border-color: #334155;
        }}
        
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Outfit', sans-serif;
            margin: 0;
            padding: 24px;
        }}
        
        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        
        header {{
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        h1 {{
            margin: 0;
            font-size: 24px;
            color: var(--primary);
        }}
        
        .nav-links a {{
            color: var(--text-muted);
            text-decoration: none;
            margin-left: 16px;
            font-weight: 600;
            font-size: 14px;
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }}
        
        .nav-links a:hover, .nav-links a.active {{
            color: var(--text-main);
            background-color: var(--border-color);
        }}
        
        .main-layout {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }}
        
        .panel {{
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 24px;
            border: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        
        .panel h2 {{
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 18px;
            align-self: flex-start;
        }}
        
        .pie-chart {{
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: conic-gradient(
                var(--success) 0.0% {pass_pct}%,
                var(--error) {pass_pct}% {pass_pct + fail_pct}%,
                var(--warning) {pass_pct + fail_pct}% 100%
            );
            margin-bottom: 20px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        }}
        
        .chart-legend {{
            display: flex;
            gap: 20px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            font-size: 13px;
        }}
        
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 6px;
        }}
        
        .stat-details {{
            width: 100%;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }}
        
        .info-box {{
            background-color: rgba(255,255,255,0.02);
            border-radius: 8px;
            padding: 16px;
            border: 1px solid var(--border-color);
        }}
        
        .info-label {{
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        
        .info-val {{
            font-size: 20px;
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Kisan Mitra E2E Web Dashboard</h1>
            <div class="nav-links">
                <a href="execution-report.html">Grid View</a>
                <a href="dashboard.html" class="active">Dashboard</a>
            </div>
        </header>
        
        <div class="main-layout">
            <div class="panel">
                <h2>Execution Ratio</h2>
                <div class="pie-chart"></div>
                <div class="chart-legend">
                    <div class="legend-item"><div class="legend-dot" style="background-color: var(--success)"></div>Passed ({pass_pct:.1f}%)</div>
                    <div class="legend-item"><div class="legend-dot" style="background-color: var(--error)"></div>Failed ({fail_pct:.1f}%)</div>
                    <div class="legend-item"><div class="legend-dot" style="background-color: var(--warning)"></div>Skipped ({skip_pct:.1f}%)</div>
                </div>
            </div>
            
            <div class="panel" style="justify-content: flex-start;">
                <h2>Metrics Summary</h2>
                <div class="stat-details">
                    <div class="info-box"><div class="info-label">Total Executed</div><div class="info-val">{total}</div></div>
                    <div class="info-box"><div class="info-label">Environment</div><div class="info-val" style="font-size:14px;">Chrome Headless (Ubuntu)</div></div>
                    <div class="info-box"><div class="info-label">Pass Percentage</div><div class="info-val" style="color: var(--success);">{pass_pct:.1f}%</div></div>
                    <div class="info-box"><div class="info-label">Build ID</div><div class="info-val">#{os.getenv("GITHUB_RUN_NUMBER", "1")}</div></div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[HTMLReporter] dashboard.html compiled.")
