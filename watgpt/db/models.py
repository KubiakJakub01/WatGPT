from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Chunk(Base):
    """
    One table for both site and file data.
    """

    __tablename__ = 'chunks'

    chunk_id = Column(Integer, primary_key=True, autoincrement=True)
    source_url = Column(String, nullable=True)
    file_url = Column(String, nullable=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())


class BlockHours(Base):
    __tablename__ = 'block_hours'

    block_id = Column(String, primary_key=True)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)


class Group(Base):
    __tablename__ = 'groups'

    group_id = Column(Integer, primary_key=True, autoincrement=True)
    group_code = Column(String, nullable=False, unique=True)
    # lessons = relationship("Lesson", back_populates="group")


class Teacher(Base):
    __tablename__ = 'teachers'

    teacher_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    short_code = Column(String, nullable=True)


class Course(Base):
    __tablename__ = 'courses'

    course_id = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String, nullable=False)
    course_name = Column(String, nullable=True)


class Lesson(Base):
    __tablename__ = 'lessons'

    lesson_id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.course_id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id'))
    block_id = Column(String, ForeignKey('block_hours.block_id'), nullable=False)

    lesson_date = Column(String, nullable=False)
    room = Column(String)
    building = Column(String)
    info = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    group: 'Group' = relationship('Group', backref='lessons')
    course: 'Course' = relationship('Course', backref='lessons')
    teacher: Optional['Teacher'] = relationship('Teacher', backref='lessons')
    block: 'BlockHours' = relationship('BlockHours', backref='lessons')
