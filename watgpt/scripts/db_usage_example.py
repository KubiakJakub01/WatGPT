import argparse

from ..constants import DATABASE_FILE
from ..db import (
    create_connection,
    fetch_all_chunks,
    fetch_lessons_namedtuple,
)
from ..utils import log_info


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--group',
        type=str,
        default='WCY24IV1N2',
        help='Group code for which to fetch the timetable.',
    )
    return parser.parse_args()


def main(group_code: str):
    conn = create_connection(DATABASE_FILE)
    rows_in_db = fetch_all_chunks(conn)
    log_info(f'All PDF chunks in db => total {len(rows_in_db)} rows.')
    for row in rows_in_db:
        log_info(row)

    lessons_for_group = fetch_lessons_namedtuple(conn, group_code)
    log_info(f'Fetched {len(lessons_for_group)} lessons for group: {group_code}')

    for lrow in lessons_for_group:
        log_info(lrow)

    conn.close()


if __name__ == '__main__':
    args = parse_args()
    main(args.group)
