import os
import fitz  # PyMuPDF; install with: pip install PyMuPDF
import pypdf  # PyPDF2; install with: pip install PyPDF2
from .read_calendar_pdf import extract_calendar_text

def regular_pdf_reader(pdf_path: str) -> str:
    """
    Regular PDF text extraction using pypdf.
    Extracts text from each page and returns a single string.
    """
    text = []
    try:
        with open(pdf_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text.append(page_text)
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return "\n".join(text)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file.
    If the filename contains 'organizacja_zajec_w_roku_akademickim',
    use the calendar_reader; otherwise, use the regular_pdf_reader.
    """
    filename = os.path.basename(pdf_path).lower()
    if "organizacja_zajec_w_roku_akademickim" in filename:
        return extract_calendar_text(pdf_path)
    else:
        return regular_pdf_reader(pdf_path)

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
        # Future implementation for other file types (e.g., .docx, .txt)
        return ""
