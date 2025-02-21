# watgpt/db/chunk_db.py
from datetime import datetime
from typing import Optional
from watgpt.db.database import SessionLocal
from watgpt.db.models import (
    Chunk, BlockHours, Group,
    Teacher, Course, Lesson
)


##############################
# CHUNKS (site + file)
##############################
def create_chunk(
    source_url: Optional[str],
    file_url: Optional[str],
    title: Optional[str],
    content: str
) -> int:
    """
    Insert a row into the `chunks` table.
    Returns the chunk_id.
    """
    db = SessionLocal()
    try:
        new_chunk = Chunk(
            source_url=source_url,
            file_url=file_url,
            title=title,
            content=content
            # date is set automatically by server_default=func.now()
        )
        db.add(new_chunk)
        db.commit()
        db.refresh(new_chunk)
        return new_chunk.chunk_id
    finally:
        db.close()

def fetch_all_chunks():
    """
    Returns all rows from the 'chunks' table (site+file text).
    """
    db = SessionLocal()
    try:
        return db.query(Chunk).all()
    finally:
        db.close()


##############################
# TIMETABLE / SCHEDULE
##############################
def create_timetable_schema():
    """
    No longer needed if we do init_db().
    But if you want to fill block hours by default, see fill_block_hours below.
    """
    pass

def fill_block_hours():
    """
    Insert default block hours if not present.
    """
    db = SessionLocal()
    try:
        data = [
            ("block1", "08:00", "09:35"),
            ("block2", "09:50", "11:25"),
            ("block3", "11:40", "13:15"),
            ("block4", "13:30", "15:05"),
            ("block5", "15:45", "17:35"),
            ("block6", "17:50", "19:25"),
            ("block7", "19:40", "21:15"),
        ]
        for block_id, st, et in data:
            existing = db.query(BlockHours).filter_by(block_id=block_id).first()
            if not existing:
                db.add(BlockHours(block_id=block_id, start_time=st, end_time=et))
        db.commit()
    finally:
        db.close()

def insert_group(group_code: str) -> int:
    db = SessionLocal()
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

def insert_teacher(full_name: str, short_code: str = None) -> int:
    db = SessionLocal()
    try:
        # up to you if you want to check duplicates
        new_t = Teacher(full_name=full_name, short_code=short_code)
        db.add(new_t)
        db.commit()
        db.refresh(new_t)
        return new_t.teacher_id
    finally:
        db.close()

def insert_course(course_code: str, course_name: str = "") -> int:
    db = SessionLocal()
    try:
        # up to you if you want to check duplicates
        new_c = Course(course_code=course_code, course_name=course_name)
        db.add(new_c)
        db.commit()
        db.refresh(new_c)
        return new_c.course_id
    finally:
        db.close()

def insert_lesson(
    group_id: int,
    course_id: int,
    teacher_id: int | None,
    lesson_date: str,
    block_id: str,
    room: str | None = None,
    building: str | None = None,
    info: str | None = None,
) -> int:
    db = SessionLocal()
    try:
        new_lesson = Lesson(
            group_id=group_id,
            course_id=course_id,
            teacher_id=teacher_id,
            lesson_date=lesson_date,
            block_id=block_id,
            room=room,
            building=building,
            info=info
        )
        db.add(new_lesson)
        db.commit()
        db.refresh(new_lesson)
        return new_lesson.lesson_id
    finally:
        db.close()

def fetch_lessons_by_group(group_code: str):
    """
    Return raw rows or model objects for lessons of a given group_code.
    """
    db = SessionLocal()
    try:
        grp = db.query(Group).filter_by(group_code=group_code).first()
        if not grp:
            return []
        # We can query Lesson objects joined to Group:
        lessons = db.query(Lesson).filter_by(group_id=grp.group_id).all()
        return lessons
    finally:
        db.close()
