from collections import namedtuple

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from watgpt.constants import CHUNKS_DATABASE_FILE
from watgpt.db.models import Base, BlockHours, Chunk, Course, Group, Lesson, Teacher


class SqlDB:
    def __init__(self, db_file: str = CHUNKS_DATABASE_FILE):
        """
        Initialize the SQL database connection using the path provided in CHUNKS_DATABASE_FILE.
        """
        self.db_url = f'sqlite:///{db_file}'
        self.engine = create_engine(
            self.db_url, echo=False, connect_args={'check_same_thread': False}
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.init_db()
        self.fill_block_hours()

    def init_db(self):
        """
        Create all tables defined in Base.metadata.
        """
        Base.metadata.create_all(bind=self.engine)
        print(f'Created tables in {self.db_url}')

    # ---------------------------
    # CHUNKS (site + file) methods
    # ---------------------------
    def create_chunk(self, source_url: str, file_url: str, title: str, content: str) -> int:
        """
        Insert a new row into the 'chunks' table and return its chunk_id.
        """
        db = self.SessionLocal()
        try:
            new_chunk = Chunk(
                source_url=source_url, file_url=file_url, title=title, content=content
            )
            db.add(new_chunk)
            db.commit()
            db.refresh(new_chunk)
            return new_chunk.chunk_id
        finally:
            db.close()

    def fetch_all_chunks(self):
        """
        Returns all rows from the 'chunks' table.
        """
        db = self.SessionLocal()
        try:
            return db.query(Chunk).all()
        finally:
            db.close()

    # ---------------------------
    # TIMETABLE / SCHEDULE methods
    # ---------------------------
    def fill_block_hours(self):
        """
        Insert default block hours if they are not present.
        """
        db = self.SessionLocal()
        try:
            data = [
                ('block1', '08:00', '09:35'),
                ('block2', '09:50', '11:25'),
                ('block3', '11:40', '13:15'),
                ('block4', '13:30', '15:05'),
                ('block5', '15:45', '17:35'),
                ('block6', '17:50', '19:25'),
                ('block7', '19:40', '21:15'),
            ]
            for block_id, st, et in data:
                existing = db.query(BlockHours).filter_by(block_id=block_id).first()
                if not existing:
                    db.add(BlockHours(block_id=block_id, start_time=st, end_time=et))
            db.commit()
        finally:
            db.close()

    def insert_group(self, group_code: str) -> int:
        """
        Insert a new group (if not exists) and return its group_id.
        """
        db = self.SessionLocal()
        try:
            existing = db.query(Group).filter_by(group_code=group_code).first()
            if existing:
                return existing.group_id
            new_group = Group(group_code=group_code)
            db.add(new_group)
            db.commit()
            db.refresh(new_group)
            return new_group.group_id
        finally:
            db.close()

    def insert_teacher(self, full_name: str, short_code: str = '') -> int:
        """
        Insert a new teacher and return its teacher_id.
        """
        db = self.SessionLocal()
        try:
            new_teacher = Teacher(full_name=full_name, short_code=short_code)
            db.add(new_teacher)
            db.commit()
            db.refresh(new_teacher)
            return new_teacher.teacher_id
        finally:
            db.close()

    def insert_course(self, course_code: str, course_name: str = '') -> int:
        """
        Insert a new course and return its course_id.
        """
        db = self.SessionLocal()
        try:
            new_course = Course(course_code=course_code, course_name=course_name)
            db.add(new_course)
            db.commit()
            db.refresh(new_course)
            return new_course.course_id
        finally:
            db.close()

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
        db = self.SessionLocal()
        try:
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
            db.add(new_lesson)
            db.commit()
            db.refresh(new_lesson)
            return new_lesson.lesson_id
        finally:
            db.close()

    def fetch_lessons_by_group(self, group_code: str):
        """
        Return lessons (as a list) for a given group_code.
        """
        db = self.SessionLocal()
        try:
            grp = db.query(Group).filter_by(group_code=group_code).first()
            if not grp:
                return []
            lessons = db.query(Lesson).filter_by(group_id=grp.group_id).all()
            return lessons
        finally:
            db.close()

    def fetch_lessons_namedtuple(self, group_code: str):
        """
        Return lessons for the given group_code as named tuples with the fields:
        lesson_date, block_id, course_code, teacher_name, room, building.
        """
        db = self.SessionLocal()
        try:
            grp = db.query(Group).filter_by(group_code=group_code).first()
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

            # Join Lesson with Course and Teacher
            # (using outer join for Teacher in case it's missing)
            query = (
                db.query(
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
            results = query.all()
            lessons_nt = [LessonNT(*row) for row in results]
            return lessons_nt
        finally:
            db.close()
