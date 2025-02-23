import os
import re
import pymupdf4llm
from .read_calendar_pdf import extract_calendar_text

def normalize_newlines(text: str) -> str:
    """
    Replace multiple consecutive newlines with a single newline.
    """
    return re.sub(r'\n+', '\n', text)

def markdown_pdf_reader(pdf_path: str) -> str:
    """
    Converts the given PDF to Markdown text using pymupdf4llm.
    You can adjust parameters (e.g. write_images, dpi) if needed.
    """
    try:
        # For a basic conversion of all pages:
        md_text = pymupdf4llm.to_markdown(pdf_path)
        return normalize_newlines(md_text)
    except Exception as e:
        print(f"Error processing {pdf_path} with pymupdf4llm: {e}")
        return ""

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Use the custom calendar extractor if the filename indicates a calendar;
    otherwise, convert the PDF to Markdown.
    """
    filename = os.path.basename(pdf_path).lower()
    if "organizacja_zajec_w_roku_akademickim" in filename:
        return extract_calendar_text(pdf_path)
    else:
        return markdown_pdf_reader(pdf_path)

def extract_text_from_file(filepath: str) -> str:
    """
    Extract text from a file based on its extension.
    Currently supports PDF files.
    """
    if not os.path.exists(filepath):
        return ""
    _, ext = os.path.splitext(filepath)
    ext_lower = ext.lower()
    if ext_lower == ".pdf":
        return extract_text_from_pdf(filepath)
    else:
        # Future support for other file types
        return ""
