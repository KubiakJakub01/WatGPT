#!/usr/bin/env python3

from db_utils import (
    create_connection,
    create_table,
    insert_chunk,
    fetch_all_chunks
)

from read_calendar_pdf import extract_pdf_records as extract_records_calendar
from read_structured_pdf import extract_pdf_records as extract_records_structured

def main():
    conn = create_connection("chunks.db")
    create_table(conn)

    pdf_path_1 = r"C:\watGPT_project\WatGPT-text_extraction\wat_data\zal._nr_1_organizacja_zajec_w_roku_akademickim_2024_2025_na_studiach_stacjonarnych.pdf"
    records_1 = extract_records_calendar(pdf_path_1)
    print(f"Calendar script => extracted {len(records_1)} records from {pdf_path_1}")

    pdf_path_2 = r"C:\watGPT_project\WatGPT-text_extraction\wat_data\informator_dla_studentow_1_roku_2024.pdf"
    records_2 = extract_records_structured(pdf_path_2)
    print(f"Structured script => extracted {len(records_2)} records from {pdf_path_2}")

    for row in (records_1 + records_2):
        heading = row["heading"]
        content = row["content"]
        source_file = row["source_file"]
        page_number = row["page_number"]
        new_id = insert_chunk(conn, heading, content, source_file, page_number)
        print(f"Inserted chunk_id={new_id} from PDF={source_file}")

    rows_in_db = fetch_all_chunks(conn)

    for row in rows_in_db:
        print(row)

    conn.close()

if __name__ == "__main__":
    main()
