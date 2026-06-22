import os
from datetime import datetime

def generate_html_report(test_results, output_path):
    """Generates a responsive, premium HTML test execution report for Appium mobile E2E."""
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
    <title>Kisan Mitra - Android Appium E2E Test Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0B0F19;
            --card-bg: #151D30;
            --text-main: #F1F5F9;
            --text-muted: #64748B;
            --primary: #10B981;
            --success: #34D399;
            --error: #F87171;
            --warning: #FBBF24;
            --border-color: #1E293B;
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
            color: var(--primary);
        }}
        
        .meta {{
            font-size: 14px;
            color: var(--text-muted);
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
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
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
            background-color: rgba(52, 211, 153, 0.1);
            color: var(--success);
        }}
        
        .badge.failed {{
            background-color: rgba(248, 113, 113, 0.1);
            color: var(--error);
        }}
        
        .badge.skipped {{
            background-color: rgba(251, 191, 36, 0.1);
            color: var(--warning);
        }}
        
        .error-log {{
            font-family: monospace;
            background-color: rgba(0, 0, 0, 0.3);
            padding: 12px;
            border-radius: 8px;
            margin-top: 8px;
            color: #FECACA;
            font-size: 12px;
            max-width: 500px;
            word-wrap: break-word;
            white-space: pre-wrap;
        }}

        .gallery-title {{
            margin-top: 40px;
            margin-bottom: 16px;
            font-weight: 600;
            font-size: 20px;
            color: var(--primary);
        }}

        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 48px;
        }}
        
        .gallery-item {{
            background-color: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }}
        
        .gallery-item:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 20px rgba(0, 0, 0, 0.4);
            border-color: var(--primary);
        }}
        
        .gallery-item img {{
            width: 100%;
            height: 180px;
            object-fit: contain;
            background-color: #0d131f;
            display: block;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .gallery-caption {{
            padding: 12px;
            font-size: 12px;
            font-weight: 600;
            text-align: center;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .lightbox {{
            display: none;
            position: fixed;
            z-index: 9999;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(11, 15, 25, 0.95);
            align-items: center;
            justify-content: center;
        }}
        
        .lightbox img {{
            max-width: 90%;
            max-height: 90%;
            border-radius: 8px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            border: 1px solid var(--border-color);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Kisan Mitra Android Appium E2E Test Report</h1>
            <div class="meta">
                Run Date: <strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</strong> &nbsp;|&nbsp; 
                Target Platform: <strong>Android Emulator (KVM)</strong> &nbsp;|&nbsp; 
                Build Number: <strong>#{os.getenv("GITHUB_RUN_NUMBER", "Local")}</strong>
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
                    <th>Failure Reason</th>
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
"""

    # Scan for screenshots to embed in the gallery
    screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(output_path)), "Screenshots")
    if os.path.exists(screenshots_dir):
        files = [f for f in os.listdir(screenshots_dir) if f.lower().endswith('.png')]
        files.sort()
        if files:
            html += """
        <h2 class="gallery-title">Execution Screenshots</h2>
        <div class="gallery">
"""
            for file in files:
                name = os.path.splitext(file)[0].replace("_", " ").replace("-", " ").title()
                html += f"""            <div class="gallery-item" onclick="openLightbox('Screenshots/{file}')">
                <img src="Screenshots/{file}" alt="{name}">
                <div class="gallery-caption">{name}</div>
            </div>
"""
            html += "        </div>\n"

    html += """    </div>

    <div id="lightbox" class="lightbox" onclick="this.style.display='none'">
        <img id="lightbox-img" src="" alt="Screenshot Large">
    </div>

    <script>
        function openLightbox(src) {
            document.getElementById('lightbox-img').src = src;
            document.getElementById('lightbox').style.display = 'flex';
        }
    </script>
</body>
</html>
"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    print(f"[MobileHTMLReporter] Report saved successfully to {output_path}")
