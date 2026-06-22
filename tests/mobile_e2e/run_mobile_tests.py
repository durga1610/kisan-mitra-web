import os
import sys
import pytest
from datetime import datetime

# Add the directory containing run_mobile_tests.py to sys.path so modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reporters.excel_reporter import generate_excel_report
from reporters.html_reporter import generate_html_report

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

def generate_summary_markdown(test_results, summary_path):
    """Generates the Markdown summary report for step summary validation."""
    total = len(test_results)
    passed = sum(1 for r in test_results if r["status"] == "passed")
    failed = sum(1 for r in test_results if r["status"] == "failed")
    pass_pct = (passed / total * 100) if total > 0 else 0
    
    # Resolve repository urls
    repo_env = os.getenv("GITHUB_REPOSITORY", "durga1610/kisan-mitra-web")
    owner, repo = repo_env.split("/")
    live_report_url = f"https://{owner}.github.io/{repo}/reports/latest/execution-report.html"
    
    lines = [
        "# Android Appium Test Summary",
        "",
        f"Build Number: #{os.getenv('GITHUB_RUN_NUMBER', 'Local')}",
        f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Total Tests: {total}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        f"Pass Rate: {pass_pct:.1f}%",
        "",
        "Report URL:",
        live_report_url,
        "",
        "## Detailed Mobile Results",
        "",
        "| # | Suite | Test Case | Status | Duration | Failure Reason |",
        "| :---: | :--- | :--- | :---: | :---: | :--- |"
    ]
    
    for idx, r in enumerate(test_results, 1):
        status_badge = "🟢 PASS" if r["status"] == "passed" else "🔴 FAIL" if r["status"] == "failed" else "🟡 SKIP"
        err_reason = r["error"].replace("\n", " ").replace("|", "\\|") if r.get("error") else ""
        if len(err_reason) > 100:
            err_reason = err_reason[:97] + "..."
        lines.append(f"| {idx} | {r['suite']} | `{r['name']}` | {status_badge} | {r['duration']:.2f}s | {err_reason} |")
        
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
        test_suites_path
    ]
    
    print(f"Running pytest with args: {pytest_args}\n")
    pytest.main(pytest_args, plugins=[collector])
    
    # Compile results
    results_list = list(collector.reports.values())
    
    # Generate files
    excel_path = os.path.join(results_dir, "Excel", "Automation_Test_Report.xlsx")
    html_path = os.path.join(results_dir, "HTML", "execution-report.html")
    summary_path = os.path.join(results_dir, "Summary", "summary.md")
    
    print("\n" + "=" * 70)
    print("MOBILE TEST SUITE COMPLETED. GENERATING REPORTS...")
    print("=" * 70)
    
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
            
    generate_excel_report(results_list, excel_path)
    generate_html_report(results_list, html_path)
    generate_summary_markdown(results_list, summary_path)
    
    print(f"Excel report: {excel_path}")
    print(f"HTML report: {html_path}")
    print(f"Summary markdown: {summary_path}")
    print(f"Logs: {log_path}")
    print("=" * 70)
    
    # Determine exit code based on failures and validation gate
    total_count = len(results_list)
    failed_count = sum(1 for r in results_list if r["status"] == "failed")
    
    if total_count == 0:
        print("ERROR: Mobile Validation Gate Failed - Total Tests run is 0! Failing build.")
        sys.exit(1)
    elif failed_count > 0:
        print(f"Execution finished with {failed_count} failures. Exiting with status code 1.")
        sys.exit(1)
    else:
        print(f"All {total_count} tests executed successfully. Exiting with status code 0.")
        sys.exit(0)

if __name__ == "__main__":
    main()
