import argparse
from pathlib import Path

from ..reader import extract_records_calendar, extract_records_structured
from ..scraper import scrape_timetable
from .constants import CALENDAR_PDF_FP, DATABASE_FILE, STRUCTURED_PDF_FP, TIMETABLE_URL
from .db_utils import (
    create_connection,
    create_table_pdf_chunks,
    create_timetable_schema,
    fetch_all_chunks,
    fetch_lessons_namedtuple,
    fill_block_hours,
    insert_chunk,
    insert_course,
    insert_group,
    insert_lesson,
    insert_teacher,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--calendar_pdf_fp',
        type=Path,
        default=CALENDAR_PDF_FP,
        help='Path to the first PDF file with calendar data.',
    )
    parser.add_argument(
        '--structured_pdf_fp',
        type=Path,
        default=STRUCTURED_PDF_FP,
        help='Path to the second PDF file with structured data.',
    )
    parser.add_argument(
        '--group',
        type=str,
        default='WCY24IV1N2',
        help='Group code for which to scrape the timetable.',
    )

    return parser.parse_args()


def main(calendar_pdf_fp: Path, structured_pdf_fp: Path, group: str):
    conn = create_connection(DATABASE_FILE)
    create_table_pdf_chunks(conn)
    create_timetable_schema(conn)
    fill_block_hours(conn)

    calendar_records = extract_records_calendar(calendar_pdf_fp)
    print(f'Calendar script => extracted {len(calendar_records)} records from {calendar_pdf_fp}')

    structured_records = extract_records_structured(structured_pdf_fp)
    print(
        f'Structured script => extracted {len(structured_records)} records from {structured_pdf_fp}'
    )

    for row in calendar_records + structured_records:
        heading = row['heading']
        content = row['content']
        source_file = row['source_file']
        page_number = row['page_number']
        new_id = insert_chunk(conn, heading, content, source_file, page_number)
        print(f'Inserted chunk_id={new_id} from PDF={source_file}')

    rows_in_db = fetch_all_chunks(conn)
    print(f'\nAll PDF chunks in db => total {len(rows_in_db)} rows.')
    for row_in_db in rows_in_db:
        print(row_in_db)

    url = TIMETABLE_URL.format(group=group)
    timetable_data = scrape_timetable(url)
    print(f'\nScraped {len(timetable_data)} lessons from {url}')
    group_id = insert_group(conn, group)

    for lesson in timetable_data:
        teacher_id = None
        if lesson['teacher_name']:
            # We store teacher's full name
            teacher_id = insert_teacher(
                conn,
                full_name=lesson['teacher_name'],
                short_code=None,  # or parse if you have short code
            )

        course_id = insert_course(conn, course_code=lesson['course_code'], course_name='')

        insert_lesson(
            conn=conn,
            group_id=group_id,
            course_id=course_id,
            teacher_id=teacher_id,
            lesson_date=lesson['date'],  # e.g. "2024_10_05"
            block_id=lesson['block_id'],
            room=lesson['room'],
            building=lesson['building'],
            info=lesson['info'],
        )

    lessons_for_group = fetch_lessons_namedtuple(conn, group)
    print(f'\nFetched {len(lessons_for_group)} lessons for group: {group}')

    for lrow in lessons_for_group:
        print(lrow)

    conn.close()


if __name__ == '__main__':
    args = parse_args()
    main(args.calendar_pdf_fp, args.structured_pdf_fp, args.group)
