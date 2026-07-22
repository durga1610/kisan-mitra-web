import os
import re
import pypdf


def parse_pdf_content(pdf_path):
    """
    Parses PDF document using pypdf, extracts page text, cleans header/footer artifacts,
    normalizes line breaks, and extracts the document title.

    Returns:
    tuple: (title, cleaned_content)
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at '{pdf_path}'")

    reader = pypdf.PdfReader(pdf_path)
    page_texts = []
    title = ""

    # Extract metadata title if available
    if reader.metadata and reader.metadata.title:
        title = reader.metadata.title.strip()

    for page_idx, page in enumerate(reader.pages):
        raw_page_text = page.extract_text() or ""
        lines = [l.strip() for l in raw_page_text.splitlines() if l.strip()]

        # Filter out standalone page numbers (e.g. "Page 1 of 5" or "1")
        filtered_lines = []
        for line in lines:
            if re.match(r"^Page\s+\d+(\s+of\s+\d+)?$", line, re.IGNORECASE) or re.match(r"^\d+$", line):
                continue
            filtered_lines.append(line)

        if filtered_lines:
            page_texts.append("\n".join(filtered_lines))

    full_text = "\n\n".join(page_texts)

    # Normalize internal whitespace
    cleaned_content = re.sub(r"[ \t]+", " ", full_text)
    cleaned_content = re.sub(r"\n{3,}", "\n\n", cleaned_content)

    if not title:
        # Fallback title from filename or first line
        first_line = cleaned_content.splitlines()[0] if cleaned_content else ""
        if first_line and len(first_line) < 100:
            title = first_line.replace("#", "").strip()
        else:
            base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
            title = base_filename.replace("_", " ").replace("-", " ").title()

    return title, cleaned_content
