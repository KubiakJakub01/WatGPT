import os

from ..constants import CHUNKS_DATABASE_FILE
from ..db.sql_db import SqlDB
from ..utils import log_info


def main():
    if os.path.exists(CHUNKS_DATABASE_FILE):
        os.remove(CHUNKS_DATABASE_FILE)
        log_info(f'Removed existing database file: {CHUNKS_DATABASE_FILE}')
    else:
        log_info('No previous database file found.')
    # Instantiating SqlDB automatically initializes the database (init_db is called in __init__)
    db = SqlDB()
    db.fill_block_hours()
    log_info('Database created and block hours filled.')


if __name__ == '__main__':
    main()
