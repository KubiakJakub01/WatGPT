import argparse

from ..constants import CHUNKS_DATABASE_FILE
from ..db import ChunkDB
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
    db = ChunkDB(CHUNKS_DATABASE_FILE)
    rows_in_db = db.fetch_all_chunks()
    log_info(f'All PDF chunks in db => total {len(rows_in_db)} rows.')
    for row in rows_in_db:
        log_info(row)

    lessons_for_group = db.fetch_lessons_namedtuple(group_code)
    log_info(f'Fetched {len(lessons_for_group)} lessons for group: {group_code}')

    for lrow in lessons_for_group:
        log_info(lrow)

    db.close()


if __name__ == '__main__':
    args = parse_args()
    main(args.group)
