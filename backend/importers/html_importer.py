import os
import re
from bs4 import BeautifulSoup


def parse_html_content(html_input, source_path=None):
    """
    Parses raw HTML string or HTML file path, removes markup tags,
    preserves headings (#, ##, ###), and normalizes spacing.

    Returns:
    tuple: (title, cleaned_content)
    """
    if os.path.exists(html_input) and os.path.isfile(html_input):
        with open(html_input, "r", encoding="utf-8", errors="ignore") as f:
            raw_html = f.read()
    else:
        raw_html = html_input

    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove unwanted script, style, nav, header, footer elements
    for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
        element.decompose()

    # Extract Title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.find("h1"):
        title = soup.find("h1").get_text().strip()

    # Convert headings to Markdown headers
    for h1 in soup.find_all("h1"):
        h1.replace_with(f"\n\n# {h1.get_text().strip()}\n")
    for h2 in soup.find_all("h2"):
        h2.replace_with(f"\n\n## {h2.get_text().strip()}\n")
    for h3 in soup.find_all("h3"):
        h3.replace_with(f"\n\n### {h3.get_text().strip()}\n")

    # Extract clean text
    text = soup.get_text(separator=" ")

    # Normalize spacing & line breaks
    cleaned_lines = []
    for line in text.splitlines():
        line_str = line.strip()
        if line_str:
            # Replace multiple internal spaces with a single space
            line_str = re.sub(r"[ \t]+", " ", line_str)
            cleaned_lines.append(line_str)

    cleaned_content = "\n".join(cleaned_lines)
    # Remove consecutive blank lines
    cleaned_content = re.sub(r"\n{3,}", "\n\n", cleaned_content)

    if not title and cleaned_lines:
        title = cleaned_lines[0].replace("#", "").strip()

    return title or "Agricultural Knowledge Guide", cleaned_content
