import fitz
import re
import string
from langchain.docstore.document import Document

# A quick regex to detect something like DD.MM.YYYY
# (and optionally the trailing " r." or " r" etc.)
DATE_PATTERN = re.compile(r"^\d{1,2}\.\d{1,2}\.\d{4}(\s*r\.?)?$")

def extract_header_and_rows(pdf_path: str, debug_file: str = None):
    """
    Extracts:
      - The big/bold heading from the first page (if any).
      - Rows from each page using a row threshold of <12 in y-diff.
      - Merges multi-line rows by your continuation rule.

    Returns: (header_text, [row_text, row_text, ...])

    If debug_file is not None, logs the grouping process.
    """
    doc = fitz.open(pdf_path)
    all_rows = []
    header_text = "UNDEFINED_HEADER"

    debug_handle = None
    if debug_file:
        debug_handle = open(debug_file, "w", encoding="utf-8")
        debug_handle.write(f"DEBUG LOG for PDF: {pdf_path}\n\n")

    for page_idx, page in enumerate(doc):
        # 1) Attempt to detect header on first page
        if page_idx == 0:
            possible_header = detect_header(page)
            if possible_header:
                header_text = possible_header

        # 2) Parse the page's spans into row strings
        page_rows = parse_page_into_rows(page, debug_handle)
        all_rows.extend(page_rows)

    # 3) Merge multi-line rows (where next row starts with digit/lowercase)
    merged = merge_multiline_rows(all_rows)

    if debug_handle:
        debug_handle.write(f"\nFINAL MERGED ROWS:\n")
        for r in merged:
            debug_handle.write(f"  {r}\n")
        debug_handle.close()

    return header_text, merged

def detect_header(page, min_font_size=12):
    """
    Looks for large/bold text near the top (y0 < 150) and combines it.
    """
    blocks = page.get_text("dict")["blocks"]
    top_candidates = []
    for b in blocks:
        if b.get("type", 1) == 0:  # text block
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                    font_size = span.get("size", 0)
                    is_bold = "bold" in span.get("font", "").lower()
                    y0 = span.get("bbox", [0, 0, 0, 0])[1]
                    # If font >= min_font_size OR bold, and near top
                    if (font_size >= min_font_size or is_bold) and (y0 < 150):
                        top_candidates.append(text)
    if top_candidates:
        return " ".join(top_candidates)
    return None

def parse_page_into_rows(page, debug_handle=None, row_diff_threshold=12, x_split=140):
    """
    Reads all spans (x0, y0, text) from the page, sorts them by y (top->bottom),
    then groups them into rows whenever (current_y - last_y) >= row_diff_threshold.

    Then each row is split into 2 columns:
      - Left column (x < x_split)
      - Right column (x >= x_split)
    We sort each column by (y0, x0), combine them into strings, then join with ' | '.

    Returns: a list of row_text strings for this page.
    """
    page_number = page.number
    blocks = page.get_text("dict")["blocks"]
    spans = []

    for b in blocks:
        if b.get("type", 1) == 0:
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        x0 = span["bbox"][0]
                        y0 = span["bbox"][1]
                        spans.append((x0, y0, text))

    # Sort spans top->bottom, left->right
    spans.sort(key=lambda x: (x[1], x[0]))

    if debug_handle:
        debug_handle.write(f"--- Page {page_number} ---\n")
        debug_handle.write("Extracted spans (x0, y0, text):\n")
        for (x0, y0, txt) in spans:
            debug_handle.write(f"  x0={x0:.1f}, y0={y0:.1f}, text='{txt}'\n")
        debug_handle.write("\nRow grouping with row_diff_threshold=12:\n")

    rows_of_spans = []
    current_row = []
    last_y = None

    for (x0, y0, text) in spans:
        if last_y is None:
            # first span in this page
            current_row.append((x0, y0, text))
            last_y = y0
        else:
            # check if new row
            if (y0 - last_y) >= row_diff_threshold:
                # finalize current_row
                rows_of_spans.append(current_row)
                if debug_handle:
                    debug_handle.write(f" Finalized row => {current_row}\n")
                current_row = [(x0, y0, text)]
                last_y = y0
            else:
                # same row
                current_row.append((x0, y0, text))
                # We'll do max so row extends as far down as we go
                last_y = max(last_y, y0)

    if current_row:
        rows_of_spans.append(current_row)
        if debug_handle:
            debug_handle.write(f" Finalized row => {current_row}\n")

    # Convert each list of spans into a single string by splitting into columns
    row_strings = []
    for row_spans in rows_of_spans:
        row_text = finalize_row_columns(row_spans, x_split)
        row_strings.append(row_text)
        if debug_handle:
            debug_handle.write(f" Row => {row_spans}\n")
            debug_handle.write(f"  => row_text='{row_text}'\n\n")

    if debug_handle:
        debug_handle.write("\n")

    return row_strings

def finalize_row_columns(row_spans, x_split=100):
    """
    Splits row_spans into:
      left column: (x,y,text) with x < x_split
      right column: (x,y,text) with x >= x_split

    Sort each column by y ascending (if tie, by x).
    Join each column's text with spaces. Then final row is "left_text | right_text".
    If the right column text contains exactly 2 date-like items, join them with ' - '.

    Finally, collapse extra spaces so we don't get weird spacing in words.
    """
    import re

    left_column = []
    right_column = []

    for (x, y, t) in row_spans:
        if x < x_split:
            left_column.append((x, y, t))
        else:
            right_column.append((x, y, t))

    # Sort each column top->bottom, left->right
    left_column.sort(key=lambda s: (s[1], s[0]))
    right_column.sort(key=lambda s: (s[1], s[0]))

    # Join left column text
    left_text = "".join(item[2] for item in left_column)

    # Join right column text, with optional dash for two date-like items
    right_texts = [item[2] for item in right_column]
    if len(right_texts) == 2 and all(DATE_PATTERN.search(rt) for rt in right_texts):
        right_text = f"{right_texts[0]} - {right_texts[1]}"
    else:
        right_text = " ".join(right_texts)

    # Build the raw row string
    row_str = f"{left_text} | {right_text}"

    # Now collapse multiple spaces to a single space
    # This also helps if the PDF introduced weird breaks or spacing.
    row_str = re.sub(r"\s+", " ", row_str).strip()

    return row_str

def is_continuation(row: list[str]) -> bool:
    """
    Return True if row[0] starts with a digit or a lowercase letter,
    meaning it's a continuation line.
    """
    if not row:
        return False
    first_cell = row[0].strip()
    if not first_cell:
        return False
    first_char = first_cell[0]
    # If first_char is a digit or a lowercase letter
    return first_char.isdigit() or (first_char in string.ascii_lowercase)

def merge_multiline_rows(rows: list[str]) -> list[str]:
    """
    If the next row starts with digit/lowercase in its first cell,
    append that row's entire text to the previous row.
    NOTE: Each 'row' is now a single string like "LeftText | RightText".
          We'll consider the 'first cell' as just the text before the first space
          or up to the first '|'?
    """
    merged_rows = []
    for r in rows:
        if not merged_rows:
            merged_rows.append(r)
        else:
            # parse out left side
            left_side = r.split("|", 1)[0].strip()  # text before the first '|'
            if left_side and is_continuation([left_side]):
                # merge with previous
                merged_rows[-1] += " " + r
            else:
                merged_rows.append(r)
    return merged_rows

def build_table_chunks(header_text, rows, chunk_size=5):
    """
    Takes a list of row strings, groups them into chunks of size=5,
    returns a list of Documents with metadata = header_text.
    """
    docs = []
    current_batch = []
    for row_text in rows:
        current_batch.append(row_text)
        if len(current_batch) == chunk_size:
            doc = create_doc_from_rows(header_text, current_batch)
            docs.append(doc)
            current_batch = []
    # leftover
    if current_batch:
        doc = create_doc_from_rows(header_text, current_batch)
        docs.append(doc)
    return docs

def create_doc_from_rows(header_text, row_batch):
    """
    row_batch is a list of row strings, e.g. ["LeftCol1 | RightCol1", "LeftCol2 | RightCol2"]
    We'll combine them with newlines.
    """
    chunk_text = "\n".join(row_batch)
    return Document(
        page_content=chunk_text,
        metadata={"header": header_text}
    )

def save_docs_to_txt(docs: list[Document], output_file: str):
    with open(output_file, "w", encoding="utf-8") as f:
        for i, doc in enumerate(docs, start=1):
            heading = doc.metadata.get("header", "NONE")
            f.write(f"--- Chunk {i} ---\n")
            f.write(f"HEADING: {heading}\n")
            f.write(f"CONTENT:\n{doc.page_content}\n\n")

if __name__ == "__main__":
    pdf_path = r"C:\projekt-chatbot-wat\WatGPT\wat_data\zal._nr_3_organizacja_zajec_w_roku_akademickim_2024_2025_na_jednolitych_studiach_magisterskich.pdf"
    output_file = r"C:\projekt-chatbot-wat\WatGPT\output_data\dates_output_chunks.txt"
    debug_log_path = r"C:\projekt-chatbot-wat\WatGPT\output_data\debug_log.txt"

    header_text, row_texts = extract_header_and_rows(pdf_path, debug_file=debug_log_path)
    docs = build_table_chunks(header_text, row_texts, chunk_size=5)
    save_docs_to_txt(docs, output_file)

    print(f"Saved {len(docs)} chunks to {output_file}")
    print(f"Debug info saved to {debug_log_path}")
