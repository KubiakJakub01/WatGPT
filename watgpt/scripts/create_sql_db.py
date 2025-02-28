import os

from watgpt.constants import CHUNKS_DATABASE_FILE
from watgpt.db.sql_db import SqlDB


def main():
    if os.path.exists(CHUNKS_DATABASE_FILE):
        os.remove(CHUNKS_DATABASE_FILE)
        print(f'Removed existing database file: {CHUNKS_DATABASE_FILE}')
    else:
        print('No previous database file found.')
    # Instantiating SqlDB automatically initializes the database (init_db is called in __init__)
    db = SqlDB()
    # Fill block hours as needed
    db.fill_block_hours()
    print('Database created and block hours filled.')


if __name__ == '__main__':
    main()
