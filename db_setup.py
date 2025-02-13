#db_setup.py

from db_utils import (
    create_connection,
    create_table_pdf_chunks,
    insert_chunk,
    fetch_all_chunks,
    # Timetable schema imports:
    create_timetable_schema,
    fill_block_hours,          # We'll add this helper to db_utils (see below),
    insert_group, insert_teacher, insert_course, insert_lesson,
    fetch_lessons_namedtuple
)

from read_calendar_pdf import extract_pdf_records as extract_records_calendar
from read_structured_pdf import extract_pdf_records as extract_records_structured

# This is your scraping function that returns list[dict], each with
# { date, block_id, course_code, info, color, teacher_short, room, building, etc. }
from timetable_scraper import scrape_timetable


def main():
    # 1) Connect to our SQLite db
    conn = create_connection("chunks.db")
    create_table_pdf_chunks(conn)
    create_timetable_schema(conn)
    fill_block_hours(conn)

    pdf_path_1 = r"wat_data\zal._nr_1_organizacja_zajec_w_roku_akademickim_2024_2025_na_studiach_stacjonarnych.pdf"
    records_1 = extract_records_calendar(pdf_path_1)
    print(f"Calendar script => extracted {len(records_1)} records from {pdf_path_1}")

    pdf_path_2 = r"wat_data\informator_dla_studentow_1_roku_2024.pdf"
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
    print(f"\nAll PDF chunks in db => total {len(rows_in_db)} rows.")
    for row in rows_in_db:
        print(row)

    url = "https://planzajec.wcy.wat.edu.pl/pl/rozklad?grupa_id=WCY24IV1N2"
    timetable_data = scrape_timetable(url)
    print(f"\nScraped {len(timetable_data)} lessons from {url}")

    group_code = "WCY24IV1N2"
    group_id = insert_group(conn, group_code)

    for lesson in timetable_data:
        teacher_id = None
        if lesson["teacher_name"]:
            # We store teacher's full name
            teacher_id = insert_teacher(
                conn,
                full_name=lesson["teacher_name"],
                short_code=None  # or parse if you have short code
            )

        course_id = insert_course(conn,
                                course_code=lesson["course_code"],
                                course_name="")

        new_lesson_id = insert_lesson(
            conn=conn,
            group_id=group_id,
            course_id=course_id,
            teacher_id=teacher_id,
            lesson_date=lesson["date"],   # e.g. "2024_10_05"
            block_id=lesson["block_id"],
            room=lesson["room"],
            building=lesson["building"],
            info=lesson["info"]
        )

        # print(f"Inserted lesson_id={new_lesson_id} for block={lesson['block_id']}")

    lessons_for_group = fetch_lessons_namedtuple(conn, group_code)
    print(f"\nFetched {len(lessons_for_group)} lessons for group: {group_code}")

    for lrow in lessons_for_group:
        print(lrow)

    conn.close()

if __name__ == "__main__":
    main()
