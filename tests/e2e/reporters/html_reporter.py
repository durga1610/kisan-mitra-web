import os
from datetime import datetime

def generate_html_report(test_results, output_path):
    """Generates a responsive, premium HTML test execution report."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    total = len(test_results)
    passed = sum(1 for r in test_results if r["status"] == "passed")
    failed = sum(1 for r in test_results if r["status"] == "failed")
    skipped = sum(1 for r in test_results if r["status"] == "skipped")
    pass_pct = (passed / total * 100) if total > 0 else 0
    
    # HTML Content
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kisan Mitra - Automation E2E Test Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
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
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 24px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            margin-bottom: 32px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 24px;
        }}
        
        h1 {{
            margin: 0 0 8px 0;
            font-weight: 700;
            font-size: 28px;
            letter-spacing: -0.5px;
        }}
        
        .meta {{
            font-size: 14px;
            color: var(--text-muted);
        }}
        
        .meta a {{
            color: var(--primary);
            text-decoration: none;
        }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }}
        
        .card {{
            background-color: var(--card-bg);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
        }}
        
        .card-title {{
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .card-value {{
            font-size: 32px;
            font-weight: 700;
        }}
        
        .card.success {{ border-left: 4px solid var(--success); }}
        .card.error {{ border-left: 4px solid var(--error); }}
        .card.warning {{ border-left: 4px solid var(--warning); }}
        
        .card-value.success {{ color: var(--success); }}
        .card-value.error {{ color: var(--error); }}
        .card-value.warning {{ color: var(--warning); }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: var(--card-bg);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}
        
        th, td {{
            padding: 16px 20px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        th {{
            background-color: rgba(255, 255, 255, 0.02);
            font-weight: 600;
            color: var(--text-muted);
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .badge.passed {{
            background-color: rgba(16, 185, 129, 0.1);
            color: var(--success);
        }}
        
        .badge.failed {{
            background-color: rgba(239, 68, 68, 0.1);
            color: var(--error);
        }}
        
        .badge.skipped {{
            background-color: rgba(245, 158, 11, 0.1);
            color: var(--warning);
        }}
        
        .error-log {{
            font-family: monospace;
            background-color: rgba(0, 0, 0, 0.2);
            padding: 12px;
            border-radius: 8px;
            margin-top: 8px;
            color: #FDA4AF;
            font-size: 12px;
            max-width: 500px;
            word-wrap: break-word;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Kisan Mitra E2E Test Report</h1>
            <div class="meta">
                Run Date: <strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</strong> &nbsp;|&nbsp; 
                Target URL: <strong><a href="{os.getenv("BASE_URL", "https://durga1610.github.io/kisan-mitra-web/")}" target="_blank">{os.getenv("BASE_URL", "https://durga1610.github.io/kisan-mitra-web/")}</a></strong> &nbsp;|&nbsp; 
                Platform: <strong>GitHub Pages (CI/CD)</strong>
            </div>
        </header>
        
        <div class="dashboard">
            <div class="card">
                <div class="card-title">Total Run</div>
                <div class="card-value">{total}</div>
            </div>
            <div class="card success">
                <div class="card-title">Passed</div>
                <div class="card-value success">{passed}</div>
            </div>
            <div class="card error">
                <div class="card-title">Failed</div>
                <div class="card-value error">{failed}</div>
            </div>
            <div class="card warning">
                <div class="card-title">Skipped</div>
                <div class="card-value warning">{skipped}</div>
            </div>
            <div class="card">
                <div class="card-title">Pass Rate</div>
                <div class="card-value {'success' if pass_pct >= 80 else 'error'}">{pass_pct:.1f}%</div>
            </div>
        </div>
        
        <h2>Execution Details</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Test Suite</th>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Timestamp</th>
                    <th>Reason / Details</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for idx, r in enumerate(test_results, 1):
        status = r["status"].lower()
        err_section = f'<div class="error-log">{r["error"]}</div>' if r.get("error") else ""
        html += f"""                <tr>
                    <td>{idx}</td>
                    <td style="font-weight: 600;">{r["suite"]}</td>
                    <td>{r["name"]}</td>
                    <td><span class="badge {status}">{status}</span></td>
                    <td>{r["duration"]:.2f}s</td>
                    <td>{r["timestamp"]}</td>
                    <td>{err_section}</td>
                </tr>
"""
        
    html += """            </tbody>
        </table>
    </div>
</body>
</html>
"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"[HTMLReporter] Report saved successfully to {output_path}")
