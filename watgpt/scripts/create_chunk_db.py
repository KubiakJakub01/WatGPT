# watgpt/scripts/create_chunk_db.py
from watgpt.db.database import init_db
from watgpt.db.chunk_db import fill_block_hours

def main():
    # 1) Initialize tables
    init_db()
    # 2) Optionally fill block hours
    fill_block_hours()
    print("Database created and block hours filled.")

if __name__ == "__main__":
    main()
