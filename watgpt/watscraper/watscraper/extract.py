import re
from pathlib import Path

import pymupdf4llm

from watgpt.utils import log_info

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
    except OSError as e:
        log_info(f'Error processing {pdf_path} with pymupdf4llm: {e}')
        return ''


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Use the custom calendar extractor if the filename indicates a calendar;
    otherwise, convert the PDF to Markdown.
    """
    path_obj = Path(pdf_path)
    filename_lower = path_obj.name.lower()
    if 'organizacja_zajec_w_roku_akademickim' in filename_lower:
        return extract_calendar_text(str(path_obj))
    return markdown_pdf_reader(str(path_obj))


def extract_text_from_file(filepath: str) -> str:
    """
    Extract text from a file based on its extension.
    Currently supports PDF files.
    """
    path_obj = Path(filepath)

    if not path_obj.exists():
        return ''

    ext_lower = path_obj.suffix.lower()
    if ext_lower == '.pdf':
        return extract_text_from_pdf(str(path_obj))
    return ''
