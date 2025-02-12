# db_utils.py

import sqlite3
from sqlite3 import Connection
from typing import Optional, List, Tuple

DATABASE_FILE = "chunks.db"


def create_connection(db_file: str = DATABASE_FILE) -> Connection:
    """
    Create (or open) a SQLite database at db_file.
    Returns a sqlite3 Connection object.
    """
    conn = sqlite3.connect(db_file)
    return conn


def create_table(conn: Connection) -> None:
    """
    Create the pdf_chunks table if it doesn't exist yet.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS pdf_chunks (
        chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
        heading TEXT NOT NULL,
        content TEXT NOT NULL,
        source_file TEXT,
        page_number INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with conn:
        conn.execute(create_table_sql)


def drop_table(conn: Connection, table_name: str = "pdf_chunks") -> None:
    """
    Drop the given table. Use with caution!
    """
    drop_sql = f"DROP TABLE IF EXISTS {table_name};"
    with conn:
        conn.execute(drop_sql)


def insert_chunk(
    conn: Connection,
    heading: str,
    content: str,
    source_file: Optional[str] = None,
    page_number: Optional[int] = None
) -> int:
    """
    Insert a single chunk (heading + content) into the db.
    Returns the newly inserted chunk_id.
    """
    insert_sql = """
    INSERT INTO pdf_chunks (heading, content, source_file, page_number)
    VALUES (?, ?, ?, ?);
    """
    with conn:
        cursor = conn.execute(insert_sql, (heading, content, source_file, page_number))
        return cursor.lastrowid


def insert_multiple_chunks(conn: Connection, chunks: List[Tuple[str, str, Optional[str], Optional[int]]]) -> None:
    """
    Insert multiple chunks in one go.
    Each tuple in 'chunks' should be: (heading, content, source_file, page_number).
    """
    insert_sql = """
    INSERT INTO pdf_chunks (heading, content, source_file, page_number)
    VALUES (?, ?, ?, ?);
    """
    with conn:
        conn.executemany(insert_sql, chunks)


def fetch_all_chunks(conn: Connection) -> List[Tuple[int, str, str, str, int]]:
    """
    Retrieve all rows from pdf_chunks.
    Returns a list of tuples (chunk_id, heading, content, source_file, page_number).
    """
    select_sql = "SELECT chunk_id, heading, content, source_file, page_number FROM pdf_chunks;"
    with conn:
        rows = conn.execute(select_sql).fetchall()
    return rows


def fetch_chunk_by_id(conn: Connection, chunk_id: int) -> Optional[Tuple[int, str, str, str, int]]:
    """
    Fetch a single chunk row by its primary key chunk_id.
    Returns tuple (chunk_id, heading, content, source_file, page_number) or None if not found.
    """
    select_sql = """
    SELECT chunk_id, heading, content, source_file, page_number
    FROM pdf_chunks
    WHERE chunk_id = ?;
    """
    with conn:
        row = conn.execute(select_sql, (chunk_id,)).fetchone()
    return row

