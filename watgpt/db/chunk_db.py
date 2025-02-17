import sqlite3
from pathlib import Path

from ..constants import CHUNKS_DATABASE_FILE
from .models import LessonRow


class ChunkDB:
    def __init__(self, db_file: str = CHUNKS_DATABASE_FILE):
        self.conn = sqlite3.connect(db_file)

    def create_table_pdf_chunks(self) -> None:
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
        with self.conn:
            self.conn.execute(create_table_sql)

    def drop_table(self, table_name: str = 'pdf_chunks') -> None:
        drop_sql = f'DROP TABLE IF EXISTS {table_name};'
        with self.conn:
            self.conn.execute(drop_sql)

    def insert_chunk(
        self,
        heading: str,
        content: str,
        source_file: str | Path,
        page_number: int,
    ) -> int | None:
        insert_sql = """
        INSERT INTO pdf_chunks (heading, content, source_file, page_number)
        VALUES (?, ?, ?, ?);
        """
        with self.conn:
            cursor = self.conn.execute(
                insert_sql, (heading, content, str(source_file), page_number)
            )
            return cursor.lastrowid

    def insert_multiple_chunks(self, chunks: list[tuple[str, str, str | None, int | None]]) -> None:
        insert_sql = """
        INSERT INTO pdf_chunks (heading, content, source_file, page_number)
        VALUES (?, ?, ?, ?);
        """
        with self.conn:
            self.conn.executemany(insert_sql, chunks)

    def fetch_all_chunks(self) -> list[tuple[int, str, str, str, int]]:
        select_sql = 'SELECT chunk_id, heading, content, source_file, page_number FROM pdf_chunks;'
        with self.conn:
            rows = self.conn.execute(select_sql).fetchall()
        return rows

    def fetch_chunk_by_id(self, chunk_id: int) -> tuple[int, str, str, str, int] | None:
        select_sql = """
        SELECT chunk_id, heading, content, source_file, page_number
        FROM pdf_chunks
        WHERE chunk_id = ?;
        """
        with self.conn:
            row = self.conn.execute(select_sql, (chunk_id,)).fetchone()
        return row

    def create_timetable_schema(self) -> None:
        create_block_hours_sql = """
        CREATE TABLE IF NOT EXISTS block_hours (
            block_id   TEXT PRIMARY KEY,
            start_time TEXT NOT NULL,
            end_time   TEXT NOT NULL
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
            block_id   TEXT NOT NULL,
            lesson_date TEXT NOT NULL,
            room   TEXT,
            building TEXT,
            info   TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id)     REFERENCES groups(group_id),
            FOREIGN KEY (course_id)    REFERENCES courses(course_id),
            FOREIGN KEY (teacher_id)   REFERENCES teachers(teacher_id),
            FOREIGN KEY (block_id)     REFERENCES block_hours(block_id)
        );
        """
        with self.conn:
            self.conn.execute(create_block_hours_sql)
            self.conn.execute(create_groups_sql)
            self.conn.execute(create_teachers_sql)
            self.conn.execute(create_courses_sql)
            self.conn.execute(create_lessons_sql)

    def fill_block_hours(self) -> None:
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
        with self.conn:
            self.conn.executemany(insert_sql, block_data)

    def drop_timetable_tables(self) -> None:
        with self.conn:
            self.conn.execute('DROP TABLE IF EXISTS lessons;')
            self.conn.execute('DROP TABLE IF EXISTS groups;')
            self.conn.execute('DROP TABLE IF EXISTS teachers;')
            self.conn.execute('DROP TABLE IF EXISTS courses;')

    def insert_group(self, group_code: str) -> int | None:
        sql = 'INSERT INTO groups (group_code) VALUES (?);'
        with self.conn:
            cursor = self.conn.execute(sql, (group_code,))
            return cursor.lastrowid

    def insert_teacher(self, full_name: str, short_code: str | None = None) -> int | None:
        sql = 'INSERT INTO teachers (full_name, short_code) VALUES (?, ?);'
        with self.conn:
            cursor = self.conn.execute(sql, (full_name, short_code))
            return cursor.lastrowid

    def insert_course(self, course_code: str, course_name: str = '') -> int | None:
        sql = 'INSERT INTO courses (course_code, course_name) VALUES (?, ?);'
        with self.conn:
            cursor = self.conn.execute(sql, (course_code, course_name))
            return cursor.lastrowid

    def insert_lesson(
        self,
        group_id: int | None,
        course_id: int | None,
        teacher_id: int | None,
        lesson_date: str,
        block_id: str,
        room: str | None = None,
        building: str | None = None,
        info: str | None = None,
    ) -> int | None:
        sql = """
        INSERT INTO lessons (
            group_id, course_id, teacher_id, lesson_date, block_id, room, building, info
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        with self.conn:
            cursor = self.conn.execute(
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

    def fetch_lessons_by_group(self, group_code: str) -> list[tuple]:
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
        with self.conn:
            rows = self.conn.execute(sql, (group_code,)).fetchall()
        return rows

    def fetch_lessons_namedtuple(self, group_code: str) -> list[LessonRow]:
        raw_rows = self.fetch_lessons_by_group(group_code)
        results = []
        for row in raw_rows:
            results.append(LessonRow(*row))
        return results
