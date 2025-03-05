from collections import namedtuple

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from ..constants import CHUNKS_DATABASE_FILE, DEFAULT_BLOCK_HOURS
from ..utils import log_info
from .models import Base, BlockHours, Chunk, Course, Group, Lesson, Teacher


class SqlDB:
    def __init__(self, db_file: str = CHUNKS_DATABASE_FILE):
        """
        Initialize the SQL database connection using the path provided in CHUNKS_DATABASE_FILE.
        """
        self.db_url = f'sqlite:///{db_file}'
        self.engine = create_engine(
            self.db_url,
            echo=False,
            connect_args={'check_same_thread': False},
        )
        self.session_local = sessionmaker(bind=self.engine)
        self.init_db()
        self.fill_block_hours()

    def init_db(self):
        """
        Create all tables defined in Base.metadata.
        """
        Base.metadata.create_all(bind=self.engine)
        log_info(f'Created tables in {self.db_url}')

    def create_chunk(self, source_url: str, file_url: str, title: str, content: str) -> int:
        """
        Insert a new row into the 'chunks' table and return its chunk_id.
        """
        with self.session_local() as session:
            with session.begin():
                new_chunk = Chunk(
                    source_url=source_url,
                    file_url=file_url,
                    title=title,
                    content=content,
                )
                session.add(new_chunk)
            session.refresh(new_chunk)
            return new_chunk.chunk_id

    def fetch_all_chunks(self):
        """
        Returns all rows from the 'chunks' table.
        """
        with self.session_local() as session:
            statement = select(Chunk)
            result = session.execute(statement).scalars().all()
            return result

    def fill_block_hours(self):
        """
        Insert default block hours if they are not present.
        """
        # Combine session + transaction in a single with statement:
        with self.session_local() as session, session.begin():
            for block_id, st, et in DEFAULT_BLOCK_HOURS:
                existing = session.execute(
                    select(BlockHours).filter_by(block_id=block_id)
                ).scalar_one_or_none()
                if not existing:
                    session.add(BlockHours(block_id=block_id, start_time=st, end_time=et))

    def insert_group(self, group_code: str) -> int:
        """
        Insert a new group (if not exists) and return its group_id.
        """
        with self.session_local() as session:
            with session.begin():
                existing = session.execute(
                    select(Group).filter_by(group_code=group_code)
                ).scalar_one_or_none()
                if existing:
                    return existing.group_id
                new_group = Group(group_code=group_code)
                session.add(new_group)
            session.refresh(new_group)
            return new_group.group_id

    def insert_teacher(self, full_name: str, short_code: str = '') -> int:
        """
        Insert a new teacher and return its teacher_id.
        """
        with self.session_local() as session:
            with session.begin():
                new_teacher = Teacher(full_name=full_name, short_code=short_code)
                session.add(new_teacher)
            session.refresh(new_teacher)
            return new_teacher.teacher_id

    def insert_course(self, course_code: str, course_name: str = '') -> int:
        """
        Insert a new course and return its course_id.
        """
        with self.session_local() as session:
            with session.begin():
                new_course = Course(course_code=course_code, course_name=course_name)
                session.add(new_course)
            session.refresh(new_course)
            return new_course.course_id

    def insert_lesson(
        self,
        group_id: int,
        course_id: int,
        teacher_id: int | None,
        lesson_date: str,
        block_id: str,
        room: str | None = None,
        building: str | None = None,
        info: str | None = None,
    ) -> int:
        """
        Insert a new lesson and return its lesson_id.
        """
        with self.session_local() as session:
            with session.begin():
                new_lesson = Lesson(
                    group_id=group_id,
                    course_id=course_id,
                    teacher_id=teacher_id,
                    lesson_date=lesson_date,
                    block_id=block_id,
                    room=room,
                    building=building,
                    info=info,
                )
                session.add(new_lesson)
            session.refresh(new_lesson)
            return new_lesson.lesson_id

    def fetch_lessons_by_group(self, group_code: str):
        """
        Return lessons (as a list) for a given group_code.
        """
        with self.session_local() as session:
            grp = session.execute(
                select(Group).filter_by(group_code=group_code)
            ).scalar_one_or_none()
            if not grp:
                return []
            statement = select(Lesson).filter_by(group_id=grp.group_id)
            return session.execute(statement).scalars().all()

    def fetch_lessons_namedtuple(self, group_code: str):
        """
        Return lessons for the given group_code as named tuples with the fields:
        lesson_date, block_id, course_code, teacher_name, room, building.
        """
        with self.session_local() as session:
            grp = session.execute(
                select(Group).filter_by(group_code=group_code)
            ).scalar_one_or_none()
            if not grp:
                return []

            LessonNT = namedtuple(
                'LessonNT',
                [
                    'lesson_date',
                    'block_id',
                    'course_code',
                    'teacher_name',
                    'room',
                    'building',
                ],
            )

            stmt = (
                select(
                    Lesson.lesson_date,
                    Lesson.block_id,
                    Course.course_code,
                    Teacher.full_name.label('teacher_name'),
                    Lesson.room,
                    Lesson.building,
                )
                .join(Course, Lesson.course_id == Course.course_id)
                .outerjoin(Teacher, Lesson.teacher_id == Teacher.teacher_id)
                .filter(Lesson.group_id == grp.group_id)
            )
            results = session.execute(stmt).all()
            lessons_nt = [LessonNT(*row) for row in results]
            return lessons_nt
