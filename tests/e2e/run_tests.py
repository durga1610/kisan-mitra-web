import os
import sys
import json
import pytest
from datetime import datetime

# Add the directory containing run_tests.py to sys.path so modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reporters.excel_reporter import (
    generate_excel_report,
    generate_passed_report,
    generate_failed_report,
    generate_summary_report
)
from reporters.html_reporter import (
    generate_html_report,
    generate_dashboard_report
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

# Helper to enrich collected results with test case metadata
def enrich_collected_results(results_list):
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

def generate_summary_markdown(enriched_results, summary_path, build_status):
    """Generates the enterprise markdown summary log matching user's layout requirements."""
    total = len(enriched_results)
    passed = sum(1 for r in enriched_results if r["status"] == "PASSED")
    failed = sum(1 for r in enriched_results if r["status"] == "FAILED")
    skipped = sum(1 for r in enriched_results if r["status"] == "SKIPPED")
    
    pass_pct = (passed / total * 100) if total > 0 else 0
    duration = sum(r["execution_time"] for r in enriched_results)
    
    target_url = os.getenv("BASE_URL", "https://durga1610.github.io/kisan-mitra-web/")
    
    # Calculate modules performance
    module_data = {}
    for t in enriched_results:
        mod = t["module"]
        if mod not in module_data:
            module_data[mod] = {"total": 0, "passed": 0, "failed": 0}
        module_data[mod]["total"] += 1
        if t["status"] == "PASSED":
            module_data[mod]["passed"] += 1
        elif t["status"] == "FAILED":
            module_data[mod]["failed"] += 1

    modules_stats = []
    for mod, data in module_data.items():
        rate = (data["passed"] / data["total"] * 100) if data["total"] > 0 else 0
        modules_stats.append({"name": mod, "rate": rate, "failed": data["failed"]})
        
    # Sort modules for failed / passing logs
    top_failed = sorted([m for m in modules_stats if m["failed"] > 0], key=lambda x: x["rate"])
    top_passing = sorted(modules_stats, key=lambda x: x["rate"], reverse=True)
    
    lines = [
        "# Live GitHub Pages E2E Execution Summary",
        "",
        f"**Deployment URL**:",
        f"{target_url}",
        "",
        f"**Execution Date**:",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"**Build Status**:",
        f"{build_status}",
        "",
        "**Deployment Status**:",
        "PASS" if build_status == "PASS" else "FAIL",
        "",
        f"**Total Test Cases**:",
        f"{total}",
        "",
        f"**Executed**: {total}",
        f"**Passed**: {passed}",
        f"**Failed**: {failed}",
        f"**Skipped**: {skipped}",
        "",
        f"**Pass Percentage**: {pass_pct:.2f}%",
        "",
        f"**Execution Duration**: {duration:.2f}s",
        "",
        "### Top Failed Modules:",
        ""
    ]
    
    for fm in top_failed[:3]:
        lines.append(f"- **{fm['name']}** (Pass Rate: {fm['rate']:.1f}%, Failures: {fm['failed']})")
    if not top_failed:
        lines.append("No failed modules.")
        
    lines.append("")
    lines.append("### Failed Tests:")
    lines.append("")
    
    failed_cases = [r for r in enriched_results if r["status"] == "FAILED"]
    for t in failed_cases:
        reason = t["error"].replace("\n", " ").replace("|", "\\|")
        if len(reason) > 100:
            reason = reason[:97] + "..."
        lines.append(f"- **{t['id']}** - {t['name']}")
        lines.append(f"  *Reason*: {reason}")
        
    if not failed_cases:
        lines.append("No failed tests.")
        
    lines.append("")
    lines.append("### Top Passing Modules:")
    lines.append("")
    
    for pm in top_passing[:5]:
        lines.append(f"- **{pm['name']}** - Pass Rate: {pm['rate']:.2f}%")
        
    lines.append("")
    lines.append("### Artifacts Generated:")
    lines.append("")
    lines.append("✓ Excel Reports")
    lines.append("✓ HTML Reports")
    lines.append("✓ Screenshots")
    lines.append("✓ Logs")
    lines.append("✓ JSON Results")
    
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[SummaryReporter] Summary saved to {summary_path}")

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
    print(f"KISAN MITRA WEB E2E TEST RUNNER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Base URL: {os.getenv('BASE_URL', 'https://durga1610.github.io/kisan-mitra-web/')}")
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
    enriched_results = enrich_collected_results(results_list)
    
    excel_dir = os.path.join(results_dir, "Excel")
    html_dir = os.path.join(results_dir, "HTML")
    json_path = os.path.join(results_dir, "JSON", "execution-results.json")
    summary_path = os.path.join(results_dir, "Summary", "summary.md")
    
    print("\n" + "=" * 70)
    print("WEB TEST SUITE COMPLETED. GENERATING REPORTS...")
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
            print(f"[WebTestRunner] Copied screenshots: {screenshots_dest}")
        except Exception as e:
            print(f"[WebTestRunner] Failed to copy screenshots: {e}")
            
    # Generate reports
    generate_excel_report(results_list, os.path.join(excel_dir, "Automation_Test_Report.xlsx"))
    generate_passed_report(results_list, os.path.join(excel_dir, "Passed_Test_Cases.xlsx"))
    generate_failed_report(results_list, os.path.join(excel_dir, "Failed_Test_Cases.xlsx"))
    generate_summary_report(results_list, os.path.join(excel_dir, "Summary_Report.xlsx"))
    
    generate_html_report(results_list, os.path.join(html_dir, "execution-report.html"))
    generate_dashboard_report(results_list, os.path.join(html_dir, "dashboard.html"))
    
    # Validation Gate Calculations
    total_count = len(enriched_results)
    
    if total_count == 0:
        print("ERROR: Web Validation Gate Failed - Total Tests run is 0! Failing build.")
        generate_summary_markdown(enriched_results, summary_path, "FAIL")
        sys.exit(1)
        
    passed_count = sum(1 for t in enriched_results if t["status"] == "PASSED")
    failed_count = sum(1 for t in enriched_results if t["status"] == "FAILED")
    pass_pct = (passed_count / total_count * 100)
    
    critical_tests = [t for t in enriched_results if t["priority"] == "Critical"]
    critical_failed = sum(1 for t in critical_tests if t["status"] == "FAILED")
    critical_fail_pct = (critical_failed / len(critical_tests) * 100) if critical_tests else 0
    
    print(f"Overall Pass Rate: {pass_pct:.2f}% (Required >= 95.0%)")
    print(f"Critical Fail Rate: {critical_fail_pct:.2f}% (Allowed <= 5.0%)")
    
    if pass_pct < 95.0 or critical_fail_pct > 5.0:
        build_status = "FAIL"
    else:
        build_status = "PASS"
        
    # Generate Markdown Summary
    generate_summary_markdown(enriched_results, summary_path, build_status)
    
    print("Reports compilation complete.")
    print("=" * 70)
    
    if build_status == "FAIL":
        print("ERROR: E2E Validation Gate Failed. Exiting status 1.")
        sys.exit(1)
    else:
        print("Validation Gate Passed successfully! Exiting status 0.")
        sys.exit(0)

if __name__ == "__main__":
    main()
