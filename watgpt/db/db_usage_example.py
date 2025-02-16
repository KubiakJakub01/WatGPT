from .db_utils import (
    create_connection,
    fetch_all_chunks,
    fetch_lessons_namedtuple,
)


def main():
    conn = create_connection('chunks.db')
    rows_in_db = fetch_all_chunks(conn)
    print(f'\nAll PDF chunks in db => total {len(rows_in_db)} rows.')
    for row in rows_in_db:
        print(row)

    group_code = 'WCY24IV1N2'
    lessons_for_group = fetch_lessons_namedtuple(conn, group_code)
    print(f'\nFetched {len(lessons_for_group)} lessons for group: {group_code}')

    for lrow in lessons_for_group:
        print(lrow)

    conn.close()
