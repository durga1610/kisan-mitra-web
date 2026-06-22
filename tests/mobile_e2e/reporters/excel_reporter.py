import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generate_excel_report(test_results, output_path):
    """Generates a professional Excel automation test report for Appium Android E2E."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Calculate stats
    total = len(test_results)
    passed = sum(1 for r in test_results if r["status"] == "passed")
    failed = sum(1 for r in test_results if r["status"] == "failed")
    skipped = sum(1 for r in test_results if r["status"] == "skipped")
    pass_pct = (passed / total * 100) if total > 0 else 0
    
    wb = Workbook()
    
    # ── Sheet 1: Dashboard Summary ───────────────────────────────────────────
    ws_sum = wb.active
    ws_sum.title = "Summary Dashboard"
    ws_sum.sheet_view.showGridLines = True
    
    # Stylings
    navy_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    green_fill = PatternFill(start_color="D5F5E3", end_color="D5F5E3", fill_type="solid")
    red_fill = PatternFill(start_color="FADBD8", end_color="FADBD8", fill_type="solid")
    yellow_fill = PatternFill(start_color="FCF3CF", end_color="FCF3CF", fill_type="solid")
    
    border_side = Side(style="thin", color="D5D8DC")
    thin_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    
    # Title Block
    ws_sum.merge_cells("A1:D1")
    title_cell = ws_sum["A1"]
    title_cell.value = "KISAN MITRA — MOBILE E2E APPIUM TEST REPORT"
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    title_cell.fill = navy_fill
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_sum.row_dimensions[1].height = 40
    
    # Meta Details
    meta = [
        ("Execution Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Test Environment:", "Android Emulator (UiAutomator2)"),
        ("App Platform:", "Android Debug APK"),
    ]
    for idx, (k, v) in enumerate(meta, 2):
        ws_sum.cell(row=idx, column=1, value=k).font = Font(bold=True)
        ws_sum.cell(row=idx, column=2, value=v)
        ws_sum.row_dimensions[idx].height = 20
        
    # Stats Headers
    ws_sum.cell(row=6, column=1, value="Metric").font = Font(bold=True, color="FFFFFF")
    ws_sum.cell(row=6, column=1).fill = navy_fill
    ws_sum.cell(row=6, column=2, value="Count").font = Font(bold=True, color="FFFFFF")
    ws_sum.cell(row=6, column=2).fill = navy_fill
    
    metrics = [
        ("Total Tests Run", total, None),
        ("Passed Tests", passed, green_fill),
        ("Failed Tests", failed, red_fill),
        ("Skipped Tests", skipped, yellow_fill),
        ("Pass Percentage", f"{pass_pct:.1f}%", green_fill if pass_pct >= 80 else red_fill),
    ]
    
    for idx, (label, val, fill) in enumerate(metrics, 7):
        c1 = ws_sum.cell(row=idx, column=1, value=label)
        c2 = ws_sum.cell(row=idx, column=2, value=val)
        c1.border = thin_border
        c2.border = thin_border
        c2.alignment = Alignment(horizontal="center")
        if fill:
            c1.fill = fill
            c2.fill = fill
            c1.font = Font(bold=True)
            c2.font = Font(bold=True)
        ws_sum.row_dimensions[idx].height = 24
        
    ws_sum.column_dimensions["A"].width = 24
    ws_sum.column_dimensions["B"].width = 50
    
    # ── Sheet 2: Test Details ────────────────────────────────────────────────
    ws_det = wb.create_sheet("Test Execution Details")
    ws_det.sheet_view.showGridLines = True
    ws_det.freeze_panes = "A2"
    
    headers = ["#", "Test Suite", "Test Name", "Status", "Duration (s)", "Timestamp", "Failure Reason"]
    ws_det.row_dimensions[1].height = 28
    
    for col_idx, h in enumerate(headers, 1):
        cell = ws_det.cell(row=1, column=col_idx, value=h)
        cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        cell.fill = navy_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
        
    for r_idx, r in enumerate(test_results, 2):
        ws_det.row_dimensions[r_idx].height = 22
        vals = [
            r_idx - 1,
            r["suite"],
            r["name"],
            r["status"].upper(),
            f"{r['duration']:.2f}",
            r["timestamp"],
            r.get("error", "")
        ]
        
        status = r["status"].lower()
        fill = green_fill if status == "passed" else red_fill if status == "failed" else yellow_fill
        
        for c_idx, val in enumerate(vals, 1):
            cell = ws_det.cell(row=r_idx, column=c_idx, value=val)
            cell.border = thin_border
            cell.font = Font(name="Calibri", size=10)
            if c_idx == 4: # Status
                cell.fill = fill
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center")
            elif c_idx in (1, 5, 6):
                cell.alignment = Alignment(horizontal="center")
                
    widths = [6, 18, 32, 12, 14, 20, 50]
    for col_idx, w in enumerate(widths, 1):
        ws_det.column_dimensions[get_column_letter(col_idx)].width = w
        
    wb.save(output_path)
    print(f"[MobileExcelReporter] Report saved successfully to {output_path}")
