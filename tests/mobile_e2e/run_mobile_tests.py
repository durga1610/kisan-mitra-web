import os
import sys
import json
import pytest
from datetime import datetime

# Add the directory containing run_mobile_tests.py to sys.path so modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reporters.excel_reporter import (
    generate_excel_report,
    generate_passed_report,
    generate_failed_report,
    generate_summary_report
)
from reporters.html_reporter import (
    generate_html_report,
    generate_dashboard_report,
    generate_trends_report
)

# Custom stream duplicator to write logs to both console and file
class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")
        self.encoding = self.terminal.encoding if hasattr(self.terminal, 'encoding') else 'utf-8'

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def isatty(self):
        return self.terminal.isatty() if hasattr(self.terminal, 'isatty') else False

# Pytest plugin to collect test execution details
class ResultCollector:
    def __init__(self):
        self.reports = {}

    def pytest_runtest_logreport(self, report):
        nodeid = report.nodeid
        if nodeid not in self.reports:
            parts = nodeid.split("::")
            suite = os.path.basename(report.fspath) if hasattr(report, 'fspath') else parts[0]
            name = parts[-1]
            self.reports[nodeid] = {
                "suite": suite,
                "name": name,
                "status": "passed",
                "duration": 0.0,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": ""
            }
        
        self.reports[nodeid]["duration"] += report.duration
        
        if report.failed:
            self.reports[nodeid]["status"] = "failed"
            err_msg = ""
            if report.longrepr:
                err_msg = str(report.longrepr)
            self.reports[nodeid]["error"] = err_msg
        elif report.skipped and self.reports[nodeid]["status"] != "failed":
            self.reports[nodeid]["status"] = "skipped"
            err_msg = ""
            if report.longrepr:
                if isinstance(report.longrepr, tuple):
                    err_msg = report.longrepr[2]
                else:
                    err_msg = str(report.longrepr)
            self.reports[nodeid]["error"] = err_msg

# Helper to enrich pytest results with test case metadata
def enrich_collected_results(results_list):
    # Load test case metadata for details
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "test_cases.json")
    tc_map = {}
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                tcs = json.load(f)
                tc_map = {tc["id"]: tc for tc in tcs}
        except Exception:
            pass

    enriched = []
    for idx, r in enumerate(results_list, 1):
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
            "status": r["status"].upper(),
            "execution_time": r["duration"],
            "timestamp": r["timestamp"],
            "error": r.get("error", "")
        })
    return enriched

def generate_summary_markdown(enriched_results, summary_path):
    """Generates the Markdown summary report for step summary validation."""
    total = len(enriched_results)
    passed = sum(1 for r in enriched_results if r["status"] == "PASSED")
    failed = sum(1 for r in enriched_results if r["status"] == "FAILED")
    skipped = sum(1 for r in enriched_results if r["status"] == "SKIPPED")
    blocked = 0
    
    pass_pct = (passed / total * 100) if total > 0 else 0
    fail_pct = (failed / total * 100) if total > 0 else 0
    duration = sum(r["execution_time"] for r in enriched_results)
    
    repo_env = os.getenv("GITHUB_REPOSITORY", "durga1610/kisan-mitra-web")
    owner, repo = repo_env.split("/")
    live_report_url = f"https://{owner}.github.io/{repo}/reports/latest/execution-report.html"
    
    lines = [
        "# Android Appium E2E Execution Summary",
        "",
        f"**Build Number**: #{os.getenv('GITHUB_RUN_NUMBER', '13')}",
        f"**Execution Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Git Commit**: {os.getenv('GITHUB_SHA', '651fccc1')[:8]}",
        f"**Branch**: {os.getenv('GITHUB_REF_NAME', 'main')}",
        "",
        "**APK Version**: 1.0.0-debug",
        "**Device**: Android Emulator (UiAutomator2)",
        "**Android Version**: 10.0 (API 29)",
        "",
        "### Execution Metrics",
        "",
        f"- **Total Test Cases**: {total}",
        f"- **Executed**: {total}",
        f"- **Passed**: {passed}",
        f"- **Failed**: {failed}",
        f"- **Skipped**: {skipped}",
        f"- **Blocked**: {blocked}",
        "",
        f"- **Pass Percentage**: {pass_pct:.2f}%",
        f"- **Fail Percentage**: {fail_pct:.2f}%",
        f"- **Execution Duration**: {duration:.2f}s",
        "",
        "### Live Hosted Reports",
        f"- **HTML Dashboard**: {live_report_url}",
        "",
        "### Test Execution Details",
        "",
        "#### PASSED TESTS",
        ""
    ]
    
    # Add passed tests (limit to 10 for viewability)
    passed_cases = [r for r in enriched_results if r["status"] == "PASSED"]
    for t in passed_cases[:15]:
        lines.append(f"✓ {t['id']} - {t['name']}")
    if len(passed_cases) > 15:
        lines.append(f"... and {len(passed_cases) - 15} more passed tests.")
        
    lines.append("")
    lines.append("#### FAILED TESTS")
    lines.append("")
    
    failed_cases = [r for r in enriched_results if r["status"] == "FAILED"]
    for t in failed_cases:
        reason = t["error"].replace("\n", " ").replace("|", "\\|")
        if len(reason) > 100:
            reason = reason[:97] + "..."
        lines.append(f"✗ {t['id']} - {t['name']}")
        lines.append(f"  *Reason*: {reason}")
        
    if not failed_cases:
        lines.append("No failed tests.")
        
    lines.append("")
    lines.append("#### SKIPPED TESTS")
    lines.append("")
    
    skipped_cases = [r for r in enriched_results if r["status"] == "SKIPPED"]
    for t in skipped_cases:
        lines.append(f"- {t['id']}")
    if not skipped_cases:
        lines.append("No skipped tests.")
        
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[MobileSummaryReporter] Summary saved successfully to {summary_path}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(base_dir, "Test Results")
    
    # Ensure folder structure exists
    os.makedirs(os.path.join(results_dir, "Excel"), exist_ok=True)
    os.makedirs(os.path.join(results_dir, "HTML"), exist_ok=True)
    os.makedirs(os.path.join(results_dir, "Logs"), exist_ok=True)
    os.makedirs(os.path.join(results_dir, "Summary"), exist_ok=True)
    os.makedirs(os.path.join(results_dir, "Screenshots"), exist_ok=True)
    os.makedirs(os.path.join(results_dir, "JSON"), exist_ok=True)
    
    # Start logging redirection to Logs/execution.log
    log_path = os.path.join(results_dir, "Logs", "execution.log")
    sys.stdout = Logger(log_path)
    sys.stderr = sys.stdout
    
    print("=" * 70)
    print(f"KISAN MITRA MOBILE APPIUM TEST RUNNER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    collector = ResultCollector()
    
    # Run pytest programmatically on test_suites/
    test_suites_path = os.path.join(base_dir, "test_suites")
    pytest_args = [
        "-s",
        "-v",
        "--reruns", "3",
        "--reruns-delay", "5",
        test_suites_path
    ]
    
    print(f"Running pytest with args: {pytest_args}\n")
    pytest.main(pytest_args, plugins=[collector])
    
    # Compile results
    results_list = list(collector.reports.values())
    enriched_results = enrich_collected_results(results_list)
    
    # Generate files
    excel_dir = os.path.join(results_dir, "Excel")
    html_dir = os.path.join(results_dir, "HTML")
    json_path = os.path.join(results_dir, "JSON", "execution-results.json")
    summary_path = os.path.join(results_dir, "Summary", "summary.md")
    
    print("\n" + "=" * 70)
    print("MOBILE TEST SUITE COMPLETED. GENERATING REPORTS...")
    print("=" * 70)
    
    # Save JSON report
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(enriched_results, f, indent=2)
    print(f"JSON results saved: {json_path}")
    
    # Copy screenshots to HTML/Screenshots for local relative path consistency
    screenshots_src = os.path.join(results_dir, "Screenshots")
    screenshots_dest = os.path.join(results_dir, "HTML", "Screenshots")
    if os.path.exists(screenshots_src):
        import shutil
        if os.path.exists(screenshots_dest):
            try:
                shutil.rmtree(screenshots_dest)
            except Exception:
                pass
        try:
            shutil.copytree(screenshots_src, screenshots_dest)
            print(f"[MobileTestRunner] Copied screenshots to HTML folder for local viewing: {screenshots_dest}")
        except Exception as e:
            print(f"[MobileTestRunner] Failed to copy screenshots: {e}")
            
    # Generate reports
    generate_excel_report(results_list, os.path.join(excel_dir, "Automation_Test_Report.xlsx"))
    generate_passed_report(results_list, os.path.join(excel_dir, "Passed_Test_Cases.xlsx"))
    generate_failed_report(results_list, os.path.join(excel_dir, "Failed_Test_Cases.xlsx"))
    generate_summary_report(results_list, os.path.join(excel_dir, "Execution_Summary.xlsx"))
    
    generate_html_report(results_list, os.path.join(html_dir, "execution-report.html"))
    generate_dashboard_report(results_list, os.path.join(html_dir, "dashboard.html"))
    generate_trends_report(results_list, os.path.join(html_dir, "trends.html"))
    
    generate_summary_markdown(enriched_results, summary_path)
    
    print("Reports compilation complete.")
    print("=" * 70)
    
    # Determine exit code based on the verification gate:
    # 1. Total tests > 0
    # 2. Overall pass rate >= 95%
    # 3. Critical tests failure rate <= 5%
    total_count = len(enriched_results)
    
    if total_count == 0:
        print("ERROR: Mobile Validation Gate Failed - Total Tests run is 0! Failing build.")
        sys.exit(1)
        
    passed_count = sum(1 for t in enriched_results if t["status"] == "PASSED")
    failed_count = sum(1 for t in enriched_results if t["status"] == "FAILED")
    pass_pct = (passed_count / total_count * 100)
    
    critical_tests = [t for t in enriched_results if t["priority"] == "Critical"]
    critical_failed = sum(1 for t in critical_tests if t["status"] == "FAILED")
    critical_fail_pct = (critical_failed / len(critical_tests) * 100) if critical_tests else 0
    
    print(f"Overall Pass Rate: {pass_pct:.2f}% (Required >= 95.0%)")
    print(f"Critical Fail Rate: {critical_fail_pct:.2f}% (Allowed <= 5.0%)")
    
    if pass_pct < 95.0:
        print(f"ERROR: Overall Pass Rate is {pass_pct:.2f}%, which is below the 95.0% threshold. Failing build.")
        sys.exit(1)
    elif critical_fail_pct > 5.0:
        print(f"ERROR: Critical Fail Rate is {critical_fail_pct:.2f}%, which is above the 5.0% threshold. Failing build.")
        sys.exit(1)
    else:
        print(f"Validation Gate Passed successfully! Exiting with status code 0.")
        sys.exit(0)

if __name__ == "__main__":
    main()
