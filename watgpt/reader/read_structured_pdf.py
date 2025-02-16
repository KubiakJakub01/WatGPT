import re
from pathlib import Path
from typing import Any

import fitz
import pandas as pd
from langchain.docstore.document import Document
from unidecode import unidecode


def filter_out_numeric_chunks(docs):
    filtered_docs = []
    for doc in docs:
        # Strip leading/trailing whitespace
        text = doc.page_content.strip()
        # If it's NOT just digits/spaces, keep it
        if not re.match(r'^[0-9\s]+$', text):
            filtered_docs.append(doc)
    return filtered_docs


def extract_spans_to_df(pdf_path: str | Path) -> pd.DataFrame:
    doc = fitz.open(pdf_path)
    all_rows = []
    page_num = 1
    for page in doc:  # pylint: disable=too-many-nested-blocks
        page_dict = page.get_text('dict')
        blocks = page_dict.get('blocks', [])
        for block in blocks:
            if block.get('type', 1) == 0:  # text block
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        text = span.get('text', '')
                        if not text.strip():
                            continue
                        bbox = span.get('bbox', [0, 0, 0, 0])
                        (xmin, ymin, xmax, ymax) = bbox
                        font_name = span.get('font', '')
                        font_size = span.get('size', 0.0)
                        # remove diacritics for better uppercase check
                        text_no_diacritics = unidecode(text)
                        # remove bracketed content
                        text_for_upper_check = re.sub(r'[\(\[].*?[\)\]]', '', text_no_diacritics)
                        is_bold = 'bold' in font_name.lower()
                        is_upper = text_for_upper_check.strip().isupper()

                        all_rows.append(
                            {
                                'page': page_num,
                                'xmin': xmin,
                                'ymin': ymin,
                                'xmax': xmax,
                                'ymax': ymax,
                                'text': text.strip(),
                                'font_name': font_name,
                                'font_size': font_size,
                                'is_bold': is_bold,
                                'is_upper': is_upper,
                            }
                        )
        page_num += 1
    df = pd.DataFrame(all_rows)
    return df


def classify_spans(df: pd.DataFrame) -> pd.DataFrame:
    font_size_counts = df['font_size'].round(2).value_counts()
    p_size = font_size_counts.idxmax()  # most common => paragraph size

    tags = []
    for _, row in df.iterrows():
        size = row['font_size']
        is_bold = row['is_bold']
        is_upper = row['is_upper']
        score = size - p_size
        if is_bold:
            score += 1
        if is_upper:
            score += 1

        if score >= 1:
            tag = 'h'
        elif size < p_size:
            tag = 's'
        else:
            tag = 'p'
        tags.append(tag)

    df['tag'] = tags
    return df


def build_heading_blocks(df: pd.DataFrame) -> list[tuple[str, int, list[dict[str, Any]]]]:
    """
    Sort spans top-to-bottom and group them under headings.
    We'll store:
      (heading_text, min_page_in_block, [span_records]).
    """
    df_sorted = df.sort_values(by=['page', 'ymin']).reset_index(drop=True)

    heading_blocks = []
    current_heading = 'UNDEFINED_HEADING'
    current_body: list[dict[str, Any]] = []  # store a list of dicts (one per span)
    current_body_pages: list[int] = []  # track pages for the current block

    for _, row in df_sorted.iterrows():
        tag = row['tag']
        # Build a small dictionary for each span
        record = {
            'text': row['text'],
            'page': row['page'],  # <--- store page here
            'font_size': row['font_size'],
            'is_bold': row['is_bold'],
            'is_upper': row['is_upper'],
        }

        if tag == 'h':
            # finalize the previous heading block if we have any
            if current_body:
                min_page = min(current_body_pages)
                heading_blocks.append((current_heading, min_page, current_body))
                # reset for the next block
                current_body = []
                current_body_pages = []

            current_heading = row['text']
        else:
            # p or s => accumulate in current_body
            current_body.append(record)
            current_body_pages.append(row['page'])

    # finalize the last block if it exists
    if current_body:
        min_page = min(current_body_pages)
        heading_blocks.append((current_heading, min_page, current_body))

    return heading_blocks


def chunk_text_by_sentence(text: str, chunk_size=1500, overlap_sentences=1) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk: list[str] = []
    current_len = 0
    for sentence in sentences:
        sentence_length = len(sentence)
        if current_len + sentence_length > chunk_size and current_chunk:
            chunk_str = ' '.join(current_chunk).strip()
            chunks.append(chunk_str)
            # overlap
            overlap = current_chunk[-overlap_sentences:] if overlap_sentences else []
            current_chunk = overlap + [sentence]
            current_len = sum(len(s) for s in current_chunk)
        else:
            current_chunk.append(sentence)
            current_len += sentence_length
    if current_chunk:
        chunk_str = ' '.join(current_chunk).strip()
        chunks.append(chunk_str)
    return chunks


def build_docs_from_blocks(
    heading_blocks: list[tuple[str, int, list[dict]]], chunk_size=1500, overlap_sentences=1
) -> list[Document]:
    """
    Turn (heading, min_page, list_of_span_records) into chunked Documents.
    Each Document's .page_content is combined text from those spans,
    and we store 'heading' and 'page_number' in .metadata.
    """
    docs = []

    for heading, min_page, span_records in heading_blocks:
        # Combine all text in this block
        full_text = ' '.join(r['text'] for r in span_records)

        # If the block is too large, chunk it further
        if len(full_text) > chunk_size:
            sub_chunks = chunk_text_by_sentence(full_text, chunk_size, overlap_sentences)
            for sc in sub_chunks:
                doc = Document(
                    page_content=sc,
                    metadata={
                        'heading': heading,
                        'page_number': min_page,  # <--- store earliest page
                    },
                )
                docs.append(doc)
        else:
            # If short enough, just 1 chunk
            doc = Document(
                page_content=full_text, metadata={'heading': heading, 'page_number': min_page}
            )
            docs.append(doc)

    return docs


def save_docs_to_txt(docs: list[Document], output_file: str):
    """
    Save each Document to a .txt file, including the heading
    and also the 'span_info' about size, is_bold, is_upper, etc.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, doc in enumerate(docs, start=1):
            heading = doc.metadata.get('heading', 'NONE')
            f.write(f'--- Chunk {i} ---\n')
            f.write(f'HEADING: {heading}\n')
            f.write(f'CONTENT:\n{doc.page_content}\n\n')
            f.write('\n')


def extract_pdf_to_docs(pdf_path: str | Path) -> list[Document]:
    df_spans = extract_spans_to_df(pdf_path)
    df_tagged = classify_spans(df_spans)
    heading_blocks = build_heading_blocks(df_tagged)
    docs = build_docs_from_blocks(heading_blocks, chunk_size=1500, overlap_sentences=0)
    docs = filter_out_numeric_chunks(docs)
    return docs


def extract_pdf_records(pdf_path: str | Path) -> list[dict]:
    """
    1) Extract text blocks as Documents (which now have 'page_number' in metadata).
    2) Convert them into a list of dicts for the DB:
       (chunk_id, heading, content, source_file, page_number, created_at).
    """
    docs = extract_pdf_to_docs(pdf_path)  # This calls build_docs_from_blocks, etc.
    records = []
    for doc in docs:
        record = {
            'chunk_id': None,
            'heading': doc.metadata.get('heading', 'NONE'),
            'content': doc.page_content,
            'source_file': pdf_path,
            'page_number': doc.metadata.get('page_number'),  # <--- now we have it
            'created_at': None,
        }
        records.append(record)
    return records
