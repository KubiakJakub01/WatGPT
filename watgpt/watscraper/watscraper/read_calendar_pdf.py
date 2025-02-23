import re
import string
from pathlib import Path

import fitz
from langchain.docstore.document import Document

from watgpt.utils import log_debug, log_info

# A quick regex to detect something like DD.MM.YYYY (and optionally trailing " r." or " r")
DATE_PATTERN = re.compile(r'^\d{1,2}\.\d{1,2}\.\d{4}(\s*r\.?)?$')


def extract_header_and_rows(pdf_path: str | Path):
    """
    Extracts:
      - The big/bold heading from the first page (if any).
      - Rows from each page using a row threshold of <12 in y-diff.
      - Merges multi-line rows by your continuation rule.
    
    Returns: (header_text, [row_dict, row_dict, ...])
    """
    doc = fitz.open(pdf_path)
    all_rows = []
    header_text = 'UNDEFINED_HEADER'

    log_info(f'Extracting from PDF: {pdf_path}')

    for page_idx, page in enumerate(doc):
        # 1) Attempt to detect header on first page
        if page_idx == 0:
            possible_header = detect_header(page)
            if possible_header:
                header_text = possible_header

        # 2) Parse the page's spans into row strings
        page_rows = parse_page_into_rows(page)
        all_rows.extend(page_rows)

    # 3) Merge multi-line rows (where next row starts with digit/lowercase)
    merged = merge_multiline_rows(all_rows)

    log_debug(f'Extracted {len(merged)} rows from {pdf_path}')

    return header_text, merged


def detect_header(page, min_font_size=12):
    """
    Looks for large/bold text near the top (y0 < 150) and combines it.
    """
    blocks = page.get_text('dict')['blocks']
    top_candidates = []
    for b in blocks:
        if b.get('type', 1) == 0:  # text block
            for line in b.get('lines', []):
                for span in line.get('spans', []):
                    text = span.get('text', '').strip()
                    if not text:
                        continue
                    font_size = span.get('size', 0)
                    is_bold = 'bold' in span.get('font', '').lower()
                    y0 = span.get('bbox', [0, 0, 0, 0])[1]
                    # If font >= min_font_size OR bold, and near top
                    if (font_size >= min_font_size or is_bold) and (y0 < 150):
                        top_candidates.append(text)
    if top_candidates:
        return ' '.join(top_candidates)
    return None


def parse_page_into_rows(page, row_diff_threshold=12, x_split=140):
    """
    Parse a page into row dictionaries containing page_number and row text.
    """
    page_number = page.number
    blocks = page.get_text('dict')['blocks']
    spans = []

    for b in blocks:
        if b.get('type', 1) == 0:
            for line in b.get('lines', []):
                for span in line.get('spans', []):
                    text = span.get('text', '').strip()
                    if text:
                        x0 = span['bbox'][0]
                        y0 = span['bbox'][1]
                        spans.append((x0, y0, text))

    # Sort spans top-to-bottom, left-to-right
    spans.sort(key=lambda x: (x[1], x[0]))

    log_debug(f'Parsing page {page_number} with {len(spans)} spans')

    rows_of_spans = []
    current_row = []
    last_y = None

    for x0, y0, text in spans:
        if last_y is None:
            current_row.append((x0, y0, text))
            last_y = y0
        else:
            if (y0 - last_y) >= row_diff_threshold:
                rows_of_spans.append(current_row)
                log_debug(f' Finalized row => {current_row}')
                current_row = [(x0, y0, text)]
                last_y = y0
            else:
                current_row.append((x0, y0, text))
                last_y = max(last_y, y0)

    if current_row:
        rows_of_spans.append(current_row)
        log_debug(f' Finalized row => {current_row}')

    # Convert each list of spans into a dict with row text and page number.
    row_dicts = []
    for row_spans in rows_of_spans:
        row_text = finalize_row_columns(row_spans, x_split)
        row_dicts.append(
            {
                'page_number': page_number,
                'text': row_text,
            }
        )
        log_debug(f' Row => {row_spans}')
        log_debug(f"  => row_text='{row_text}'")

    log_debug(f'Parsed {len(row_dicts)} rows from page {page_number}')

    return row_dicts


def finalize_row_columns(row_spans, x_split=100):
    """
    Splits row_spans into left and right columns and builds a row string.
    """
    left_column = []
    right_column = []

    for x, y, t in row_spans:
        if x < x_split:
            left_column.append((x, y, t))
        else:
            right_column.append((x, y, t))

    left_column.sort(key=lambda s: (s[1], s[0]))
    right_column.sort(key=lambda s: (s[1], s[0]))

    left_text = ''.join(item[2] for item in left_column)
    right_texts = [item[2] for item in right_column]
    if len(right_texts) == 2 and all(DATE_PATTERN.search(rt) for rt in right_texts):
        right_text = f'{right_texts[0]} - {right_texts[1]}'
    else:
        right_text = ' '.join(right_texts)

    row_str = f'{left_text} | {right_text}'
    row_str = re.sub(r'\s+', ' ', row_str).strip()
    return row_str


def is_continuation(row: list[str]) -> bool:
    """
    Return True if row[0] starts with a digit or a lowercase letter.
    """
    if not row:
        return False
    first_cell = row[0].strip()
    if not first_cell:
        return False
    first_char = first_cell[0]
    return first_char.isdigit() or (first_char in string.ascii_lowercase)


def merge_multiline_rows(rows: list[dict]) -> list[dict]:
    """
    Merge rows when the next row's text starts with a digit/lowercase.
    """
    merged_rows: list[dict] = []
    for row in rows:
        text = row['text']
        if not merged_rows:
            merged_rows.append(row)
        else:
            left_side = text.split('|', 1)[0].strip()
            if left_side and is_continuation([left_side]):
                merged_rows[-1]['text'] += ' ' + text
            else:
                merged_rows.append(row)
    return merged_rows

def extract_calendar_text(pdf_path: str | Path) -> str:
    """
    Simplified single-method extraction for calendar PDFs.
    
    Uses all the read_calendar.py methods but returns a single aggregated text
    (header plus all merged row texts) as one string.
    """
    header_text, row_dicts = extract_header_and_rows(pdf_path)
    # Join the header and each row's text into a single text block.
    all_text = header_text + "\n" + "\n".join(row['text'] for row in row_dicts)
    return all_text
