#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime

# Configure stdout to use UTF-8 if possible to prevent unicode encode errors on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Define standard stack details
TECH_STACK = [
    {"layer": "**Backend**", "tech": "FastAPI (Python 3.11)", "version": "0.110+", "purpose": "REST API, ML Inference Server"},
    {"layer": "**Frontend**", "tech": "Flutter Web", "version": "Stable", "purpose": "Client web interface"},
    {"layer": "**Mobile**", "tech": "Flutter Android", "version": "Stable", "purpose": "Client mobile application"},
    {"layer": "**Database**", "tech": "SQLite & Firebase Firestore", "version": "WAL / Native", "purpose": "Local data storage & Cloud sync"},
    {"layer": "**AI/ML**", "tech": "PyTorch & Google Gemini AI", "version": "ResNet18/EfficientNet", "purpose": "Crop suitability & Disease classification"},
    {"layer": "**Authentication**", "tech": "Firebase Auth", "version": "Native JWT", "purpose": "Stateless bearer authorization"}
]

def run_cmd(args, cwd=None):
    try:
        res = subprocess.run(args, capture_output=True, text=True, cwd=cwd, check=True)
        return res.stdout.strip()
    except Exception:
        return ""

def get_git_author(file_path, line_number=None):
    if not file_path:
        return "Unknown Author"
    # Ensure file_path uses forward slashes for git compatibility
    file_path = file_path.replace("\\", "/")
    
    # Try git blame if line number is provided
    if line_number is not None:
        try:
            out = run_cmd(["git", "blame", "-L", f"{line_number},{line_number}", "--", file_path])
            if out:
                # Format: commit_hash (AuthorName Date) line_content
                if "(" in out:
                    part = out.split("(")[1]
                    author = part.split("202")[0].strip() # Blame date starts with 202
                    # strip any digits or timezone info
                    author = " ".join([w for w in author.split() if not any(c.isdigit() for c in w)])
                    if author:
                        return author
        except Exception:
            pass

    # Fallback to git log for the file
    try:
        out = run_cmd(["git", "log", "-1", "--format=%an", "--", file_path])
        if out:
            return out
    except Exception:
        pass
        
    return "github-actions[bot]"

def parse_sarif_severity(result, rule_map):
    # Rule severity in SARIF
    rule_id = result.get("ruleId")
    level = result.get("level", "warning")
    
    # Default severities based on level
    severity = "Medium"
    if level == "error":
        severity = "High"
    elif level == "note":
        severity = "Low"
        
    # Check rule properties
    rule = rule_map.get(rule_id, {})
    properties = rule.get("properties", {})
    
    # Try security-severity score (float scale 0.0 - 10.0)
    score = properties.get("security-severity")
    if score is not None:
        try:
            val = float(score)
            if val >= 9.0:
                severity = "Critical"
            elif val >= 7.0:
                severity = "High"
            elif val >= 4.0:
                severity = "Medium"
            else:
                severity = "Low"
        except ValueError:
            pass
            
    # Try custom severity field
    custom_sev = properties.get("severity")
    if custom_sev:
        custom_sev = custom_sev.lower()
        if "critical" in custom_sev:
            severity = "Critical"
        elif "high" in custom_sev:
            severity = "High"
        elif "medium" in custom_sev or "moderate" in custom_sev:
            severity = "Medium"
        elif "low" in custom_sev:
            severity = "Low"
            
    return severity

def parse_sarif_file(sarif_path):
    findings = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    if not os.path.exists(sarif_path):
        return findings
        
    try:
        with open(sarif_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for run in data.get("runs", []):
            # Build rules lookup map
            rules = run.get("tool", {}).get("driver", {}).get("rules", [])
            rule_map = {r.get("id"): r for r in rules}
            
            for res in run.get("results", []):
                sev = parse_sarif_severity(res, rule_map)
                findings[sev] += 1
    except Exception as e:
        print(f"[Warning] Failed to parse SARIF {sarif_path}: {e}")
        
    return findings

def parse_bandit_file(bandit_path):
    findings = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    if not os.path.exists(bandit_path):
        return findings
        
    try:
        with open(bandit_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for res in data.get("results", []):
            sev = res.get("issue_severity", "MEDIUM").capitalize()
            if sev == "High":
                # Bandit does not have Critical by default, map to High or upgrade
                findings["High"] += 1
            elif sev == "Medium":
                findings["Medium"] += 1
            elif sev == "Low":
                findings["Low"] += 1
    except Exception as e:
        print(f"[Warning] Failed to parse Bandit {bandit_path}: {e}")
        
    return findings

def parse_pip_audit_file(audit_path):
    findings = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    if not os.path.exists(audit_path):
        return findings
        
    try:
        with open(audit_path, "r", encoding="utf-8") as f:
            # pip-audit outputs list of dependencies, some with vulns
            # Format is either list of dependencies, or dictionary with 'dependencies'
            data = json.load(f)
            deps = data if isinstance(data, list) else data.get("dependencies", [])
            for dep in deps:
                vulns = dep.get("vulns", []) if isinstance(dep, dict) else dep[1] if isinstance(dep, list) and len(dep) > 1 else []
                for vuln in vulns:
                    # CVSS score mapping if available
                    cvss = vuln.get("cvss")
                    if cvss is not None:
                        try:
                            val = float(cvss)
                            if val >= 9.0:
                                findings["Critical"] += 1
                            elif val >= 7.0:
                                findings["High"] += 1
                            elif val >= 4.0:
                                findings["Medium"] += 1
                            else:
                                findings["Low"] += 1
                            continue
                        except ValueError:
                            pass
                    # Default: classify pip-audit vuln as High
                    findings["High"] += 1
    except Exception as e:
        print(f"[Warning] Failed to parse pip-audit {audit_path}: {e}")
        
    return findings

def parse_api_security_file(api_path):
    findings = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    if not os.path.exists(api_path):
        return findings
        
    try:
        with open(api_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for issue in data.get("issues", []):
            sev = issue.get("severity", "MEDIUM").capitalize()
            if sev == "Critical":
                findings["Critical"] += 1
            elif sev == "High":
                findings["High"] += 1
            elif sev == "Medium":
                findings["Medium"] += 1
            elif sev == "Low":
                findings["Low"] += 1
    except Exception as e:
        print(f"[Warning] Failed to parse API security check {api_path}: {e}")
        
    return findings

def parse_gitleaks_sarif(gitleaks_path):
    leaks = []
    if not os.path.exists(gitleaks_path):
        return leaks
        
    try:
        with open(gitleaks_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for run in data.get("runs", []):
            for res in run.get("results", []):
                rule_id = res.get("ruleId", "Generic Secret")
                
                # Get file path
                file_name = "Unknown File"
                line_num = None
                locations = res.get("locations", [])
                if locations:
                    ploc = locations[0].get("physicalLocation", {})
                    artifact = ploc.get("artifactLocation", {})
                    file_name = artifact.get("uri", "Unknown File")
                    
                    region = ploc.get("region", {})
                    line_num = region.get("startLine")
                    
                author = get_git_author(file_name, line_num)
                leaks.append({
                    "rule_id": rule_id,
                    "file_name": file_name,
                    "author": author
                })
    except Exception as e:
        print(f"[Warning] Failed to parse Gitleaks SARIF {gitleaks_path}: {e}")
        
    return leaks

def parse_junit_xml(junit_path):
    stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "pass_rate": 0.0}
    if not os.path.exists(junit_path):
        return stats
        
    try:
        tree = ET.parse(junit_path)
        root = tree.getroot()
        
        # In pytest junit xml, root tag is usually <testsuites> or <testsuite>
        testsuite = root if root.tag == "testsuite" else root.find("testsuite")
        
        if testsuite is not None:
            stats["total"] = int(testsuite.attrib.get("tests", 0))
            stats["failed"] = int(testsuite.attrib.get("failures", 0)) + int(testsuite.attrib.get("errors", 0))
            stats["skipped"] = int(testsuite.attrib.get("skipped", 0))
            stats["passed"] = stats["total"] - stats["failed"] - stats["skipped"]
            
            total = stats["total"]
            passed = stats["passed"]
            stats["pass_rate"] = float(f"{(passed / total * 100):.2f}") if total > 0 else 0.0
    except Exception as e:
        print(f"[Warning] Failed to parse JUnit XML {junit_path}: {e}")
        
    return stats

def load_e2e_json_results(json_path):
    stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "pass_rate": 0.0}
    if not os.path.exists(json_path):
        return stats
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            cases = json.load(f)
            
        stats["total"] = len(cases)
        stats["passed"] = sum(1 for c in cases if c.get("status") == "PASSED")
        stats["failed"] = sum(1 for c in cases if c.get("status") == "FAILED")
        stats["skipped"] = sum(1 for c in cases if c.get("status") == "SKIPPED")
        
        total = stats["total"]
        passed = stats["passed"]
        stats["pass_rate"] = float(f"{(passed / total * 100):.2f}") if total > 0 else 0.0
    except Exception as e:
        print(f"[Warning] Failed to load JSON results {json_path}: {e}")
        
    return stats

def parse_load_test_report(report_path):
    stats = {"status": "N/A", "total_requests": 0, "rps": 0.0, "avg_latency": 0.0, "failed_requests": 0}
    if not os.path.exists(report_path):
        return stats
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
        import re
        total_reqs_match = re.search(r"\*\*Total Requests Sent\*\*\s*\|\s*(\d+)", content)
        failed_reqs_match = re.search(r"\*\*Failed Requests\*\*\s*\|\s*(\d+)", content)
        rps_match = re.search(r"\*\*Requests Per Second \(RPS\)\*\*\s*\|\s*\*\*([\d.]+)(?:\s*RPS)?\*\*", content)
        avg_lat_match = re.search(r"\*\*Average Latency\*\*\s*\|\s*([\d.]+) ms", content)
        if total_reqs_match:
            stats["total_requests"] = int(total_reqs_match.group(1))
        if failed_reqs_match:
            stats["failed_requests"] = int(failed_reqs_match.group(1))
        if rps_match:
            stats["rps"] = float(rps_match.group(1))
        if avg_lat_match:
            stats["avg_latency"] = float(avg_lat_match.group(1))
        if stats["total_requests"] > 0:
            stats["status"] = "PASS" if stats["failed_requests"] == 0 else "FAIL"
    except Exception as e:
        print(f"[Warning] Failed to parse load test report {report_path}: {e}")
    return stats

def main():
    parser = argparse.ArgumentParser(description="Consolidated GHA Job Summary Generator")
    parser.add_argument("--type", required=True, choices=["web", "android", "security"], help="Workflow type")
    parser.add_argument("--run-number", required=True, help="GitHub Action Run Number")
    parser.add_argument("--commit", required=True, help="GitHub Commit SHA")
    parser.add_argument("--pages-dir", default="gh-pages-dir", help="Directory where gh-pages branch is checked out")
    args = parser.parse_args()

    # Define paths
    latest_status_dir = os.path.join(args.pages_dir, "reports", "latest")
    status_file_path = os.path.join(latest_status_dir, "cicd-status.json")

    # Ensure pages directory exists
    os.makedirs(latest_status_dir, exist_ok=True)

    # Load existing status or initialize default structure
    status_db = {}
    if os.path.exists(status_file_path):
        try:
            with open(status_file_path, "r", encoding="utf-8") as f:
                status_db = json.load(f)
        except Exception as e:
            print(f"[Warning] Could not parse existing status JSON: {e}")

    # Set up default values if not present
    if "web_e2e" not in status_db:
        status_db["web_e2e"] = {"status": "N/A", "total": 0, "passed": 0, "failed": 0, "skipped": 0, "pass_rate": 0.0, "report_url": "", "build_number": "", "commit": ""}
    if "android_e2e" not in status_db:
        status_db["android_e2e"] = {"status": "N/A", "total": 0, "passed": 0, "failed": 0, "skipped": 0, "pass_rate": 0.0, "report_url": "", "build_number": "", "commit": ""}
    if "backend_security" not in status_db:
        status_db["backend_security"] = {"status": "N/A", "critical": 0, "high": 0, "medium": 0, "low": 0, "report_url": "", "build_number": "", "commit": ""}
    if "secrets_scan" not in status_db:
        status_db["secrets_scan"] = {"status": "N/A", "secrets_found": 0, "leaks": [], "report_url": "", "build_number": "", "commit": ""}
    if "unit_tests" not in status_db:
        status_db["unit_tests"] = {"status": "N/A", "total": 0, "passed": 0, "failed": 0, "skipped": 0, "pass_rate": 0.0, "report_url": "", "build_number": "", "commit": ""}
    if "load_testing" not in status_db:
        status_db["load_testing"] = {"status": "N/A", "total_requests": 0, "rps": 0.0, "avg_latency": 0.0, "failed_requests": 0, "report_url": "", "build_number": "", "commit": ""}

    # Parse inputs and update the appropriate section
    owner_repo = os.getenv("GITHUB_REPOSITORY", "durga1610/kisan-mitra-web")
    owner, repo_name = owner_repo.split("/")
    base_url = f"https://{owner}.github.io/{repo_name}"

    if args.type == "web":
        # Parse Web E2E
        web_json = "tests/e2e/Test Results/JSON/execution-results.json"
        web_stats = load_e2e_json_results(web_json)
        
        status_db["web_e2e"] = {
            "status": "PASS" if web_stats["total"] > 0 and web_stats["pass_rate"] >= 95.0 and web_stats["failed"] == 0 else "FAIL" if web_stats["total"] > 0 else "N/A",
            "total": web_stats["total"],
            "passed": web_stats["passed"],
            "failed": web_stats["failed"],
            "skipped": web_stats["skipped"],
            "pass_rate": web_stats["pass_rate"],
            "report_url": f"{base_url}/reports/latest/web/execution-report.html",
            "build_number": args.run_number,
            "commit": args.commit[:8]
        }

        # Parse Load Testing if report exists
        load_report_path = "all-artifacts/load-test-reports/load-test-report.md"
        if not os.path.exists(load_report_path):
            load_report_path = "Vulnerability Test Results/load-test-report.md"
        
        if os.path.exists(load_report_path):
            l_stats = parse_load_test_report(load_report_path)
            status_db["load_testing"] = {
                "status": l_stats["status"],
                "total_requests": l_stats["total_requests"],
                "rps": l_stats["rps"],
                "avg_latency": l_stats["avg_latency"],
                "failed_requests": l_stats["failed_requests"],
                "report_url": f"{base_url}/reports/latest/load-test-report.md",
                "build_number": args.run_number,
                "commit": args.commit[:8]
            }

    elif args.type == "android":
        # Parse Android E2E
        android_json = "tests/mobile_e2e/Test Results/JSON/execution-results.json"
        android_stats = load_e2e_json_results(android_json)
        
        status_db["android_e2e"] = {
            "status": "PASS" if android_stats["total"] > 0 and android_stats["pass_rate"] >= 95.0 and android_stats["failed"] == 0 else "FAIL" if android_stats["total"] > 0 else "N/A",
            "total": android_stats["total"],
            "passed": android_stats["passed"],
            "failed": android_stats["failed"],
            "skipped": android_stats["skipped"],
            "pass_rate": android_stats["pass_rate"],
            "report_url": f"{base_url}/reports/latest/android/execution-report.html",
            "build_number": args.run_number,
            "commit": args.commit[:8]
        }

    elif args.type == "security":
        # Define search paths for artifacts
        semgrep_path = "all-artifacts/semgrep-sarif/semgrep.sarif"
        if not os.path.exists(semgrep_path):
            semgrep_path = "semgrep.sarif"
            
        bandit_path = "all-artifacts/bandit-report/bandit.json"
        if not os.path.exists(bandit_path):
            bandit_path = "security-reports/bandit.json"
            
        pip_path = "all-artifacts/dependency-scan/pip-audit.json"
        if not os.path.exists(pip_path):
            pip_path = "security-reports/pip-audit.json"
            
        trivy_path = "all-artifacts/trivy-report/trivy-fs.sarif"
        if not os.path.exists(trivy_path):
            trivy_path = "trivy-fs.sarif"
            
        api_path = "all-artifacts/api-security-check/api-security.json"
        if not os.path.exists(api_path):
            api_path = "security-reports/api-security.json"
            
        gitleaks_path = "all-artifacts/gitleaks-report/results.sarif"
        if not os.path.exists(gitleaks_path):
            gitleaks_path = "results.sarif"
            
        junit_path = "all-artifacts/test-results/test-results.xml"
        if not os.path.exists(junit_path):
            junit_path = "test-results.xml"
            if not os.path.exists(junit_path):
                junit_path = "backend/test-results.xml"

        # Parse findings
        semgrep_findings = parse_sarif_file(semgrep_path)
        bandit_findings = parse_bandit_file(bandit_path)
        pip_findings = parse_pip_audit_file(pip_path)
        trivy_findings = parse_sarif_file(trivy_path)
        api_findings = parse_api_security_file(api_path)
        leaks = parse_gitleaks_sarif(gitleaks_path)
        unit_stats = parse_junit_xml(junit_path)

        # Aggregate counts
        crit = semgrep_findings["Critical"] + bandit_findings["Critical"] + pip_findings["Critical"] + trivy_findings["Critical"] + api_findings["Critical"]
        high = semgrep_findings["High"] + bandit_findings["High"] + pip_findings["High"] + trivy_findings["High"] + api_findings["High"]
        med = semgrep_findings["Medium"] + bandit_findings["Medium"] + pip_findings["Medium"] + trivy_findings["Medium"] + api_findings["Medium"]
        low = semgrep_findings["Low"] + bandit_findings["Low"] + pip_findings["Low"] + trivy_findings["Low"] + api_findings["Low"]

        # If security reports exist, update backend security status
        any_security_report = any(os.path.exists(p) for p in [semgrep_path, bandit_path, pip_path, trivy_path, api_path])
        if any_security_report:
            status_db["backend_security"] = {
                "status": "PASS" if crit == 0 else "FAIL",
                "critical": crit,
                "high": high,
                "medium": med,
                "low": low,
                "report_url": f"{base_url}/reports/latest/security-review.md",
                "build_number": args.run_number,
                "commit": args.commit[:8]
            }

        # Update Gitleaks Secrets Scan
        if os.path.exists(gitleaks_path):
            status_db["secrets_scan"] = {
                "status": "PASS" if len(leaks) == 0 else "FAIL",
                "secrets_found": len(leaks),
                "leaks": leaks,
                "report_url": f"https://github.com/{owner_repo}/actions/runs/{os.getenv('GITHUB_RUN_ID', args.run_number)}",
                "build_number": args.run_number,
                "commit": args.commit[:8]
            }

        # Update Unit Tests
        if os.path.exists(junit_path):
            status_db["unit_tests"] = {
                "status": "PASS" if unit_stats["total"] > 0 and unit_stats["failed"] == 0 else "FAIL" if unit_stats["total"] > 0 else "N/A",
                "total": unit_stats["total"],
                "passed": unit_stats["passed"],
                "failed": unit_stats["failed"],
                "skipped": unit_stats["skipped"],
                "pass_rate": unit_stats["pass_rate"],
                "report_url": f"https://github.com/{owner_repo}/actions/runs/{os.getenv('GITHUB_RUN_ID', args.run_number)}",
                "build_number": args.run_number,
                "commit": args.commit[:8]
            }

    # Save the updated status DB
    status_db["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(status_file_path, "w", encoding="utf-8") as f:
            json.dump(status_db, f, indent=2)
        print(f"[Success] Saved updated status file to {status_file_path}")
    except Exception as e:
        print(f"[Error] Failed to save status file: {e}")

    # Compile the consolidated markdown dashboard
    md = []
    md.append("## 🚀 Consolidated CI/CD Dashboard")
    md.append(f"**Last Updated:** `{status_db['last_updated']}` | **Run Trigger:** `{args.type.upper()}` | **SHA:** `{args.commit[:8]}`")
    md.append("")

    # 1. Tech Stack Table
    md.append("### 🛠️ Technology Stack")
    md.append("| Layer | Technology | Version | Purpose |")
    md.append("| :--- | :--- | :--- | :--- |")
    for row in TECH_STACK:
        md.append(f"| {row['layer']} | {row['tech']} | {row['version']} | {row['purpose']} |")
    md.append("")

    # Helpers for rendering status board
    def get_status_icon(stat):
        if stat == "PASS":
            return "🟢 PASS"
        elif stat == "FAIL":
            return "🔴 FAIL"
        elif stat == "WARNING":
            return "🟠 WARNING"
        else:
            return "➖ N/A"

    def get_link(url, label="View Report"):
        return f"[{label}]({url})" if url else "➖"

    # 2. Executive Testing Status Board
    w_stat = status_db["web_e2e"]
    a_stat = status_db["android_e2e"]
    s_stat = status_db["backend_security"]
    l_stat = status_db["secrets_scan"]
    u_stat = status_db["unit_tests"]

    sec_pass_rate = 100.0 if s_stat["critical"] == 0 and s_stat["status"] != "N/A" else 0.0 if s_stat["status"] != "N/A" else 0.0
    sec_total = s_stat["critical"] + s_stat["high"] + s_stat["medium"] + s_stat["low"]
    sec_passed = sec_total - s_stat["critical"] # Simple proxy: non-critical findings

    secrets_pass_rate = 100.0 if l_stat["secrets_found"] == 0 and l_stat["status"] != "N/A" else 0.0 if l_stat["status"] != "N/A" else 0.0

    md.append("### 📊 Executive Testing Status Board")
    md.append("| Check / Test Suite | Total Run | Passed | Failed | Skipped | Pass Rate | Status | Report URL |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")
    
    # Web E2E
    md.append(f"| **Web E2E** | {w_stat['total']} | {w_stat['passed']} | {w_stat['failed']} | {w_stat['skipped']} | {w_stat['pass_rate']}% | {get_status_icon(w_stat['status'])} | {get_link(w_stat['report_url'])} |")
    
    # Android E2E
    md.append(f"| **Android E2E** | {a_stat['total']} | {a_stat['passed']} | {a_stat['failed']} | {a_stat['skipped']} | {a_stat['pass_rate']}% | {get_status_icon(a_stat['status'])} | {get_link(a_stat['report_url'])} |")
    
    # Backend Security Scan
    sec_passed_str = sec_passed if s_stat["status"] != "N/A" else "-"
    sec_failed_str = s_stat["critical"] if s_stat["status"] != "N/A" else "-"
    sec_total_str = sec_total if s_stat["status"] != "N/A" else "-"
    sec_rate_str = f"{sec_pass_rate}%" if s_stat["status"] != "N/A" else "-"
    md.append(f"| **Backend Security Scan** | {sec_total_str} | {sec_passed_str} | {sec_failed_str} | - | {sec_rate_str} | {get_status_icon(s_stat['status'])} | {get_link(s_stat['report_url'])} |")
    
    # Secrets Scan
    secrets_failed_str = l_stat["secrets_found"] if l_stat["status"] != "N/A" else "-"
    secrets_rate_str = f"{secrets_pass_rate}%" if l_stat["status"] != "N/A" else "-"
    md.append(f"| **Secrets Scan** | - | - | {secrets_failed_str} | - | {secrets_rate_str} | {get_status_icon(l_stat['status'])} | {get_link(l_stat['report_url'], 'View Logs')} |")
    
    # Unit Tests
    md.append(f"| **Unit Tests** | {u_stat['total']} | {u_stat['passed']} | {u_stat['failed']} | {u_stat['skipped']} | {u_stat['pass_rate']}% | {get_status_icon(u_stat['status'])} | {get_link(u_stat['report_url'])} |")
    
    # Load Testing
    l_test = status_db.get("load_testing", {"status": "N/A", "total_requests": 0, "rps": 0.0, "avg_latency": 0.0, "failed_requests": 0, "report_url": "", "build_number": "", "commit": ""})
    l_reqs = l_test.get("total_requests", 0)
    l_rps = l_test.get("rps", 0.0)
    l_avg = l_test.get("avg_latency", 0.0)
    l_fail = l_test.get("failed_requests", 0)
    
    if l_test["status"] != "N/A":
        l_perf_info = f"{l_reqs} reqs / {l_rps:.1f} RPS / Avg {l_avg:.1f}ms"
        l_pass_rate = f"{(l_reqs - l_fail) / l_reqs * 100:.1f}%" if l_reqs > 0 else "-"
        l_failed_str = str(l_fail)
    else:
        l_perf_info = "-"
        l_pass_rate = "-"
        l_failed_str = "-"
        
    md.append(f"| **Load Testing** | {l_perf_info} | - | {l_failed_str} | - | {l_pass_rate} | {get_status_icon(l_test['status'])} | {get_link(l_test['report_url'])} |")
    md.append("")

    # 3. Security Findings Summary
    sec_count = s_stat["critical"] + s_stat["high"] + s_stat["medium"] + s_stat["low"]
    md.append("### 🛡️ Security Findings Summary")
    md.append("| Severity | Count | Action Required |")
    md.append("| :--- | :---: | :--- |")
    md.append(f"| 🔴 **Critical** | **{s_stat['critical']}** | Requires immediate remediation |")
    md.append(f"| 🟠 **High** | **{s_stat['high']}** | Remediate within 1 sprint |")
    md.append(f"| 🟡 **Medium** | **{s_stat['medium']}** | Remediate within 1 month |")
    md.append(f"| 🟢 **Low** | **{s_stat['low']}** | Remediate within next release |")
    md.append(f"| **Total Findings** | **{sec_count}** | |")
    md.append("")

    # 4. Secrets Leakage Log
    md.append("### 🔑 Secrets Leakage Log")
    leaks_list = l_stat.get("leaks", [])
    if leaks_list:
        md.append("| Rule ID | File Name | Authors |")
        md.append("| :--- | :--- | :--- |")
        for leak in leaks_list:
            md.append(f"| {leak['rule_id']} | {leak['file_name']} | {leak['author']} |")
    else:
        md.append("🟢 **No secrets leakage detected in this repository.**")
    md.append("")

    # Output to summary file
    summary_md = "\n".join(md)
    print("\n" + "=" * 50)
    print("CONSOLIDATED GHA STEP SUMMARY DASHBOARD")
    print("=" * 50)
    print(summary_md)
    print("=" * 50)

    # Write to GITHUB_STEP_SUMMARY if available
    summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_file:
        try:
            with open(summary_file, "a", encoding="utf-8") as sf:
                sf.write(summary_md)
            print(f"[Success] Append summary to {summary_file}")
        except Exception as e:
            print(f"[Error] Failed to write GITHUB_STEP_SUMMARY: {e}")
            
    # Also save as reports/latest/summary_dashboard.md in gh-pages
    dashboard_md_path = os.path.join(args.pages_dir, "reports", "latest", "summary_dashboard.md")
    try:
        with open(dashboard_md_path, "w", encoding="utf-8") as f:
            f.write(summary_md)
        print(f"[Success] Saved dashboard markdown to {dashboard_md_path}")
    except Exception as e:
        print(f"[Error] Failed to save summary_dashboard.md: {e}")

if __name__ == "__main__":
    main()
