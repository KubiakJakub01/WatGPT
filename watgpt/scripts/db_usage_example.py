import argparse

from ..constants import DATABASE_FILE
from ..db import (
    create_connection,
    fetch_all_chunks,
    fetch_lessons_namedtuple,
)


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
    print(f'\nAll PDF chunks in db => total {len(rows_in_db)} rows.')
    for row in rows_in_db:
        print(row)

    lessons_for_group = fetch_lessons_namedtuple(conn, group_code)
    print(f'\nFetched {len(lessons_for_group)} lessons for group: {group_code}')

    for lrow in lessons_for_group:
        print(lrow)

    conn.close()


if __name__ == '__main__':
    args = parse_args()
    main(args.group)
