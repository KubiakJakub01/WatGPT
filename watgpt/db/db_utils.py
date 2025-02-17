import sqlite3
from collections import namedtuple
from sqlite3 import Connection

from ..constants import DATABASE_FILE


def create_connection(db_file: str = DATABASE_FILE) -> Connection:
    """
    Create (or open) a SQLite database at db_file.
    Returns a sqlite3 Connection object.
    """
    conn = sqlite3.connect(db_file)
    return conn


def create_table_pdf_chunks(conn: Connection) -> None:
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


def drop_table(conn: Connection, table_name: str = 'pdf_chunks') -> None:
    """
    Drop the given table. Use with caution!
    """
    drop_sql = f'DROP TABLE IF EXISTS {table_name};'
    with conn:
        conn.execute(drop_sql)


def insert_chunk(
    conn: Connection,
    heading: str,
    content: str,
    source_file: str | None = None,
    page_number: int | None = None,
) -> int | None:
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


def insert_multiple_chunks(
    conn: Connection, chunks: list[tuple[str, str, str | None, int | None]]
) -> None:
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


def fetch_all_chunks(conn: Connection) -> list[tuple[int, str, str, str, int]]:
    """
    Retrieve all rows from pdf_chunks.
    Returns a list of tuples (chunk_id, heading, content, source_file, page_number).
    """
    select_sql = 'SELECT chunk_id, heading, content, source_file, page_number FROM pdf_chunks;'
    with conn:
        rows = conn.execute(select_sql).fetchall()
    return rows


def fetch_chunk_by_id(conn: Connection, chunk_id: int) -> tuple[int, str, str, str, int] | None:
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


# ----------------------------------------------------------------------
# NEW: Timetable schema (groups, teachers, courses, lessons)
# ----------------------------------------------------------------------


def create_timetable_schema(conn: Connection) -> None:
    create_block_hours_sql = """
    CREATE TABLE IF NOT EXISTS block_hours (
        block_id   TEXT PRIMARY KEY,   -- e.g. "block1"
        start_time TEXT NOT NULL,      -- e.g. "08:00"
        end_time   TEXT NOT NULL       -- e.g. "09:35"
        -- add any extra columns, if needed
    );
    """
    create_groups_sql = """
    CREATE TABLE IF NOT EXISTS groups (
        group_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_code TEXT NOT NULL UNIQUE
    );
    """
    create_teachers_sql = """
    CREATE TABLE IF NOT EXISTS teachers (
        teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name  TEXT NOT NULL,
        short_code TEXT
    );
    """
    create_courses_sql = """
    CREATE TABLE IF NOT EXISTS courses (
        course_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT NOT NULL,
        course_name TEXT
    );
    """
    create_lessons_sql = """
    CREATE TABLE IF NOT EXISTS lessons (
        lesson_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        
        group_id    INTEGER NOT NULL,
        course_id   INTEGER NOT NULL,
        teacher_id  INTEGER,

        -- Now references the block_hours table:
        block_id   TEXT NOT NULL,

        lesson_date TEXT NOT NULL,   -- "YYYY-MM-DD" or "YYYY_MM_DD"

        room   TEXT,    -- e.g. "308"
        building TEXT,  -- e.g. "65" or "100"
        info   TEXT,

        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (group_id)     REFERENCES groups(group_id),
        FOREIGN KEY (course_id)    REFERENCES courses(course_id),
        FOREIGN KEY (teacher_id)   REFERENCES teachers(teacher_id),
        FOREIGN KEY (block_id)     REFERENCES block_hours(block_id)
    );
    """

    with conn:
        conn.execute(create_block_hours_sql)
        conn.execute(create_groups_sql)
        conn.execute(create_teachers_sql)
        conn.execute(create_courses_sql)
        conn.execute(create_lessons_sql)


def fill_block_hours(conn: Connection) -> None:
    """
    Insert the known block hours (block1..block7) if they are not already in the table.
    """
    block_data = [
        ('block1', '08:00', '09:35'),
        ('block2', '09:50', '11:25'),
        ('block3', '11:40', '13:15'),
        ('block4', '13:30', '15:05'),
        ('block5', '15:45', '17:35'),
        ('block6', '17:50', '19:25'),
        ('block7', '19:40', '21:15'),
    ]
    insert_sql = """
    INSERT OR IGNORE INTO block_hours (block_id, start_time, end_time)
    VALUES (?, ?, ?);
    """
    with conn:
        conn.executemany(insert_sql, block_data)


def drop_timetable_tables(conn: Connection) -> None:
    """
    Drops all timetable-related tables (groups, teachers, courses, lessons).
    Use with caution!
    """
    with conn:
        conn.execute('DROP TABLE IF EXISTS lessons;')
        conn.execute('DROP TABLE IF EXISTS groups;')
        conn.execute('DROP TABLE IF EXISTS teachers;')
        conn.execute('DROP TABLE IF EXISTS courses;')


def insert_group(conn: Connection, group_code: str) -> int | None:
    """
    Insert a new group record. Returns the new group_id.
    """
    sql = 'INSERT INTO groups (group_code) VALUES (?);'
    with conn:
        cursor = conn.execute(sql, (group_code,))
        return cursor.lastrowid


def insert_teacher(conn: Connection, full_name: str, short_code: str | None = None) -> int | None:
    """
    Insert a new teacher record. Returns the new teacher_id.
    """
    sql = 'INSERT INTO teachers (full_name, short_code) VALUES (?, ?);'
    with conn:
        cursor = conn.execute(sql, (full_name, short_code))
        return cursor.lastrowid


def insert_course(conn: Connection, course_code: str, course_name: str = '') -> int | None:
    """
    Insert a new course record. Returns the new course_id.
    """
    sql = 'INSERT INTO courses (course_code, course_name) VALUES (?, ?);'
    with conn:
        cursor = conn.execute(sql, (course_code, course_name))
        return cursor.lastrowid


def insert_lesson(
    conn: Connection,
    group_id: int | None,
    course_id: int | None,
    teacher_id: int | None,
    lesson_date: str,
    block_id: str,
    room: str | None = None,
    building: str | None = None,
    info: str | None = None,
) -> int | None:
    """
    Insert a new lesson record. Returns the new lesson_id.
    """
    sql = """
    INSERT INTO lessons (
        group_id, course_id, teacher_id, lesson_date, block_id, room, building, info
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """
    with conn:
        cursor = conn.execute(
            sql,
            (
                group_id,
                course_id,
                teacher_id,
                lesson_date,
                block_id,
                room,
                building,
                info,
            ),
        )
        return cursor.lastrowid


def fetch_lessons_by_group(conn: Connection, group_code: str) -> list[tuple]:
    """
    Example query: join lessons -> groups -> courses -> teachers
    to return timetable info for a given group_code.
    """
    sql = """
    SELECT
        l.lesson_id,
        g.group_code,
        c.course_code,
        t.full_name AS teacher_name,
        l.lesson_date,
        l.block_id,
        l.room,
        l.building,
        l.info
    FROM lessons l
    JOIN groups g ON l.group_id = g.group_id
    JOIN courses c ON l.course_id = c.course_id
    LEFT JOIN teachers t ON l.teacher_id = t.teacher_id
    WHERE g.group_code = ?
    ORDER BY l.lesson_date, l.block_id;
    """
    with conn:
        rows = conn.execute(sql, (group_code,)).fetchall()
    return rows


# Example namedtuple to interpret the fetch_lessons_by_group() rows:
LessonRow = namedtuple(
    'LessonRow',
    [
        'lesson_id',
        'group_code',
        'course_code',
        'teacher_name',
        'lesson_date',
        'block_id',
        'room',
        'building',
        'info',
    ],
)


def fetch_lessons_namedtuple(conn: Connection, group_code: str) -> list[LessonRow]:
    """
    Same as fetch_lessons_by_group but returns a list of LessonRow namedtuples.
    """
    raw_rows = fetch_lessons_by_group(conn, group_code)
    results = []
    for row in raw_rows:
        results.append(LessonRow(*row))
    return results
