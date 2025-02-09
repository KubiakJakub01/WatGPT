import fitz  # PyMuPDF
import re
import pandas as pd
from unidecode import unidecode
from langchain.docstore.document import Document

def filter_out_numeric_chunks(docs):
    filtered_docs = []
    for doc in docs:
        # Strip leading/trailing whitespace
        text = doc.page_content.strip()
        # If it's NOT just digits/spaces, keep it
        if not re.match(r'^[0-9\s]+$', text):
            filtered_docs.append(doc)
    return filtered_docs

def extract_spans_to_df(pdf_path: str) -> pd.DataFrame:
    doc = fitz.open(pdf_path)
    all_rows = []
    page_num = 1
    for page in doc:
        page_dict = page.get_text("dict")
        blocks = page_dict.get("blocks", [])
        for block in blocks:
            if block.get("type", 1) == 0:  # text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if not text.strip():
                            continue
                        bbox = span.get("bbox", [0,0,0,0])
                        (xmin, ymin, xmax, ymax) = bbox
                        font_name = span.get("font", "")
                        font_size = span.get("size", 0.0)
                        # remove diacritics for better uppercase check
                        text_no_diacritics = unidecode(text)
                        # remove bracketed content
                        text_for_upper_check = re.sub(r"[\(\[].*?[\)\]]", "", text_no_diacritics)
                        is_bold = "bold" in font_name.lower()
                        is_upper = text_for_upper_check.strip().isupper()

                        all_rows.append({
                            "page": page_num,
                            "xmin": xmin,
                            "ymin": ymin,
                            "xmax": xmax,
                            "ymax": ymax,
                            "text": text.strip(),
                            "font_name": font_name,
                            "font_size": font_size,
                            "is_bold": is_bold,
                            "is_upper": is_upper
                        })
        page_num += 1
    df = pd.DataFrame(all_rows)
    return df

def classify_spans(df: pd.DataFrame) -> pd.DataFrame:
    font_size_counts = df["font_size"].round(2).value_counts()
    p_size = font_size_counts.idxmax()  # most common => paragraph size

    tags = []
    for idx, row in df.iterrows():
        size = row["font_size"]
        is_bold = row["is_bold"]
        is_upper = row["is_upper"]
        score = size - p_size
        if is_bold:
            score += 1
        if is_upper:
            score += 1
        
        if score >= 1:
            tag = "h"
        elif size < p_size:
            tag = "s"
        else:
            tag = "p"
        tags.append(tag)

    df["tag"] = tags
    return df

def build_heading_blocks(df: pd.DataFrame) -> list[tuple[str, list[dict]]]:
    """
    Sort spans top-to-bottom and group them under headings.
    Instead of storing only text, we store a list of records,
    each with 'text', 'font_size', 'is_bold', 'is_upper', etc.
    """
    df_sorted = df.sort_values(by=["page", "ymin"]).reset_index(drop=True)

    heading_blocks = []
    current_heading = "UNDEFINED_HEADING"
    current_body = []  # will store a list of dicts (one per span)

    for _, row in df_sorted.iterrows():
        tag = row["tag"]
        # We'll build a small dictionary for each span
        record = {
            "text": row["text"],
            "font_size": row["font_size"],
            "is_bold": row["is_bold"],
            "is_upper": row["is_upper"],
        }

        if tag == "h":
            # store old heading+body if we have any
            if current_body:
                heading_blocks.append((current_heading, current_body))
                current_body = []
            current_heading = row["text"]
        else:
            # p or s => accumulate in current_body
            current_body.append(record)

    if current_body:
        heading_blocks.append((current_heading, current_body))

    return heading_blocks

def chunk_text_by_sentence(text: str, chunk_size=1500, overlap_sentences=1) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_len = 0
    for sentence in sentences:
        sentence_length = len(sentence)
        if current_len + sentence_length > chunk_size and current_chunk:
            chunk_str = " ".join(current_chunk).strip()
            chunks.append(chunk_str)
            # overlap
            overlap = current_chunk[-overlap_sentences:] if overlap_sentences else []
            current_chunk = overlap + [sentence]
            current_len = sum(len(s) for s in current_chunk)
        else:
            current_chunk.append(sentence)
            current_len += sentence_length
    if current_chunk:
        chunk_str = " ".join(current_chunk).strip()
        chunks.append(chunk_str)
    return chunks

def build_docs_from_blocks(
    heading_blocks: list[tuple[str, list[dict]]],
    chunk_size=1500,
    overlap_sentences=1
) -> list[Document]:
    """
    Turn (heading, list_of_span_records) into chunked Documents.
    Each Document's .page_content is combined text from those spans,
    and the metadata includes the heading plus a summary of spans 
    (font_size, is_bold, is_upper).
    """
    docs = []

    for heading, span_records in heading_blocks:
        # Combine all text from this heading-block into one string
        full_text = " ".join(r["text"] for r in span_records)

        # If the block is too large, chunk it further
        if len(full_text) > chunk_size:
            sub_chunks = chunk_text_by_sentence(full_text, chunk_size, overlap_sentences)
            # For each sub-chunk, let's gather its relevant span metadata
            for sc in sub_chunks:
                doc = Document(
                    page_content=sc,
                    metadata={
                        "heading": heading,
                        # Example: store entire block's metadata or subset
                        # "span_info": [
                        #     {
                        #         "font_size": r["font_size"],
                        #         "is_bold": r["is_bold"],
                        #         "is_upper": r["is_upper"],
                        #         "text": r["text"]
                        #     }
                        #     for r in span_records
                        # ]
                    }
                )
                docs.append(doc)
        else:
            # If the text is short enough, just 1 chunk
            doc = Document(
                page_content=full_text,
                metadata={
                    "heading": heading,
                    # "span_info": [
                    #     {
                    #         "font_size": r["font_size"],
                    #         "is_bold": r["is_bold"],
                    #         "is_upper": r["is_upper"],
                    #         "text": r["text"]
                    #     }
                    #     for r in span_records
                    # ]
                }
            )
            docs.append(doc)

    return docs

def save_docs_to_txt(docs: list[Document], output_file: str):
    """
    Save each Document to a .txt file, including the heading
    and also the 'span_info' about size, is_bold, is_upper, etc.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        for i, doc in enumerate(docs, start=1):
            heading = doc.metadata.get("heading", "NONE")
            f.write(f"--- Chunk {i} ---\n")
            f.write(f"HEADING: {heading}\n")
            f.write(f"CONTENT:\n{doc.page_content}\n\n")

            # Display the metadata about each span
            # span_info = doc.metadata.get("span_info", [])
            # if span_info:
            #     f.write("SPAN METADATA:\n")
            #     for span in span_info:
            #         f.write(
            #             f"  size={span['font_size']}, "
            #             f"is_bold={span['is_bold']}, "
            #             f"is_upper={span['is_upper']}, "
            #             f"text=\"{span['text']}\"\n"
            #         )
            f.write("\n")

if __name__ == "__main__":
    pdf_path = r"C:\projekt-chatbot-wat\WatGPT\wat_data\informator_dla_studentow_1_roku_2024.pdf"
    output_file = r"C:\projekt-chatbot-wat\WatGPT\output_data\output_chunks.txt"

    # 1) Extract all spans into DataFrame
    df_spans = extract_spans_to_df(pdf_path)

    # 2) Classify them as heading 'h', paragraph 'p', or smaller 's'
    df_tagged = classify_spans(df_spans)

    # 3) Group them by heading blocks
    heading_blocks = build_heading_blocks(df_tagged)

    # 4) Build Documents, chunking if needed
    docs = build_docs_from_blocks(heading_blocks, chunk_size=1500, overlap_sentences=0)
    docs = filter_out_numeric_chunks(docs)

    # 5) Save to .txt
    save_docs_to_txt(docs, output_file)
    print(f"Saved {len(docs)} chunks to {output_file}")


#r"C:\\chatWAT\\Data\\informator_dla_studentow_1_roku_2024.pdf"