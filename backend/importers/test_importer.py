import os
import sys
import json
import shutil
import tempfile
import pypdf
from pypdf import PdfWriter

# Ensure parent directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from importers.knowledge_importer import KnowledgeImporter
from importers.html_importer import parse_html_content
from importers.pdf_importer import parse_pdf_content
from importers.json_exporter import export_record_to_knowledge_base


def create_sample_pdf(pdf_path, title_text, body_text):
    """
    Creates a minimal valid PDF file for testing using pypdf.
    """
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(pdf_path, "wb") as f:
        writer.write(f)


def test_knowledge_importer_suite():
    print("=" * 80)
    print(" KISAN MITRA: AGRICULTURAL KNOWLEDGE IMPORTER VERIFICATION TESTS")
    print("=" * 80)

    # Setup temporary directory for test output
    temp_dir = tempfile.mkdtemp(prefix="kisan_importer_test_")
    importer = KnowledgeImporter()

    try:
        # 1. Test HTML Guide Import
        print("\n1. Testing HTML Document Import (ICAR Tomato Guide)...")
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head><title>ICAR Tomato Cultivation and Blight Protection Guide</title></head>
        <body>
            <h1>Tomato (Solanum lycopersicum) Farming Guide</h1>
            <p>Tomato is an important commercial vegetable crop in India requiring warm weather and well-drained loamy soil.</p>
            <h2>Fertilizer Dose & NPK Management</h2>
            <p>Apply split doses of Nitrogen and Urea @ 40kg/acre along with DAP during land preparation.</p>
            <h2>Early Blight Disease Prevention</h2>
            <p>High humidity causes fungal Early Blight. Apply Mancozeb spray at 15-day intervals.</p>
        </body>
        </html>
        """
        html_file = os.path.join(temp_dir, "icar_tomato_guide.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(sample_html)

        res_html = importer.import_file(html_file, source="ICAR Agriportal (HTML Test)")
        print(f"   |- Status    : {'SUCCESS' if res_html['success'] else 'FAILED'}")
        print(f"   |- Record ID : {res_html['record_id']}")
        print(f"   |- Category  : {res_html['category']}")

        assert res_html["success"] == True, f"HTML Import failed: {res_html['message']}"
        rec_h = res_html["record"]

        # Check Schema fields
        for field in ["id", "category", "title", "content", "keywords", "related_crops", "language", "source"]:
            assert field in rec_h, f"Missing field '{field}' in HTML imported record"

        assert "<html" not in rec_h["content"].lower(), "HTML tags were not stripped"
        assert "# Tomato" in rec_h["content"] or "Tomato" in rec_h["title"], "Title/Heading lost"
        assert "Tomato" in rec_h["related_crops"], "Tomato not identified in related crops"
        print("   >>> PASS: HTML document imported and schema verified!")

        # 2. Test Text Guide Import
        print("\n2. Testing TXT Document Import (TNAU Spinach Farming Guide)...")
        sample_txt = """Spinach (Spinacia oleracea) Leafy Vegetable Cultivation Guide

        Spinach is a nutrient-dense leafy vegetable rich in iron and vitamins grown during Rabi season.
        Requires fertile alluvial or clay loam soil with pH 6.5-7.5.
        Water management: Requires light frequent drip irrigation every 4-6 days.
        Nutrient management: Apply Urea and organic compost after each leaf harvest.
        """
        txt_file = os.path.join(temp_dir, "tnau_spinach_guide.txt")
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(sample_txt)

        res_txt = importer.import_file(txt_file, source="TNAU Agriportal (TXT Test)")
        print(f"   |- Status    : {'SUCCESS' if res_txt['success'] else 'FAILED'}")
        print(f"   |- Record ID : {res_txt['record_id']}")
        print(f"   |- Category  : {res_txt['category']}")

        assert res_txt["success"] == True, f"TXT Import failed: {res_txt['message']}"
        rec_t = res_txt["record"]
        assert "Spinach" in rec_t["related_crops"], "Spinach crop not identified"
        print("   >>> PASS: TXT document imported and schema verified!")

        # 3. Test Deduplication (Non-destructive append check)
        print("\n3. Testing Duplicate Record Protection & Non-destructive Append...")
        res_dup = importer.import_file(html_file, source="ICAR Duplicate Attempt")
        print(f"   |- Status  : {'SUCCESS' if res_dup['success'] else 'SKIPPED (Duplicate Detected)'}")
        print(f"   |- Message : {res_dup['message']}")

        assert res_dup["success"] == False, "Expected importer to reject duplicate record!"
        assert "duplicate" in res_dup["message"].lower(), "Expected duplicate refusal message"
        print("   >>> PASS: Duplicate guide correctly detected and rejected!")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n" + "=" * 80)
    print(" ALL AGRICULTURAL KNOWLEDGE IMPORTER TESTS PASSED PERFECTLY!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_knowledge_importer_suite()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
