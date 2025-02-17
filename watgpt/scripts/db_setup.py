import argparse
from pathlib import Path

from ..constants import CALENDAR_PDF_FP, CHUNKS_DATABASE_FILE, STRUCTURED_PDF_FP, TIMETABLE_URL
from ..db import ChunkDB
from ..reader import extract_records_calendar, extract_records_structured
from ..scraper import scrape_timetable
from ..utils import log_debug, log_info


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
    db = ChunkDB(CHUNKS_DATABASE_FILE)
    db.create_table_pdf_chunks()
    db.create_timetable_schema()
    db.fill_block_hours()

    calendar_records = extract_records_calendar(calendar_pdf_fp)
    log_info(f'Calendar script => extracted {len(calendar_records)} records from {calendar_pdf_fp}')

    structured_records = extract_records_structured(structured_pdf_fp)
    log_info(
        f'Structured script => extracted {len(structured_records)} records from {structured_pdf_fp}'
    )

    for row in calendar_records + structured_records:
        heading = row['heading']
        content = row['content']
        source_file = row['source_file']
        page_number = row['page_number']
        new_id = db.insert_chunk(heading, content, source_file, page_number)
        log_info(f'Inserted chunk_id={new_id} from PDF={source_file}')

    rows_in_db = db.fetch_all_chunks()
    log_info(f'All PDF chunks in db => total {len(rows_in_db)} rows.')
    for row_in_db in rows_in_db:
        log_debug(row_in_db)

    url = TIMETABLE_URL.format(group=group)
    timetable_data = scrape_timetable(url)
    log_info(f'Scraped {len(timetable_data)} lessons from {url}')
    group_id = db.insert_group(group)

    for lesson in timetable_data:
        teacher_id = None
        if lesson['teacher_name']:
            # We store teacher's full name
            teacher_id = db.insert_teacher(
                full_name=lesson['teacher_name'],
                short_code=None,  # or parse if you have short code
            )

        course_id = db.insert_course(course_code=lesson['course_code'], course_name='')

        db.insert_lesson(
            group_id=group_id,
            course_id=course_id,
            teacher_id=teacher_id,
            lesson_date=lesson['date'],  # e.g. "2024_10_05"
            block_id=lesson['block_id'],
            room=lesson['room'],
            building=lesson['building'],
            info=lesson['info'],
        )

    lessons_for_group = db.fetch_lessons_namedtuple(group)
    log_info(f'Fetched {len(lessons_for_group)} lessons for group: {group}')

    for lrow in lessons_for_group:
        log_debug(lrow)


if __name__ == '__main__':
    args = parse_args()
    main(args.calendar_pdf_fp, args.structured_pdf_fp, args.group)
