# pylint: disable=unsubscriptable-object,too-few-public-methods, not-callable
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Chunk(Base):
    __tablename__ = 'chunks'

    chunk_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    file_url: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BlockHours(Base):
    __tablename__ = 'block_hours'

    block_id: Mapped[str] = mapped_column(String, primary_key=True)
    start_time: Mapped[str] = mapped_column(String, nullable=False)
    end_time: Mapped[str] = mapped_column(String, nullable=False)
    lessons: Mapped[list['Lesson']] = relationship('Lesson', back_populates='block')


class Group(Base):
    __tablename__ = 'groups'

    group_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    lessons: Mapped[list['Lesson']] = relationship('Lesson', back_populates='group')


class Teacher(Base):
    __tablename__ = 'teachers'

    teacher_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    short_code: Mapped[str | None] = mapped_column(String, nullable=True)
    lessons: Mapped[list['Lesson']] = relationship('Lesson', back_populates='teacher')


class Course(Base):
    __tablename__ = 'courses'

    course_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_code: Mapped[str] = mapped_column(String, nullable=False)
    course_name: Mapped[str | None] = mapped_column(String, nullable=True)
    lessons: Mapped[list['Lesson']] = relationship('Lesson', back_populates='course')


class Lesson(Base):
    __tablename__ = 'lessons'

    lesson_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id'), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.course_id'), nullable=False)
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey('teachers.teacher_id'), nullable=True)
    block_id: Mapped[str] = mapped_column(ForeignKey('block_hours.block_id'), nullable=False)

    lesson_date: Mapped[str] = mapped_column(String, nullable=False)
    room: Mapped[str | None] = mapped_column(String)
    building: Mapped[str | None] = mapped_column(String)
    info: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    group: Mapped['Group'] = relationship('Group', back_populates='lessons')
    course: Mapped['Course'] = relationship('Course', back_populates='lessons')
    teacher: Mapped[Optional['Teacher']] = relationship('Teacher', back_populates='lessons')
    block: Mapped['BlockHours'] = relationship('BlockHours', back_populates='lessons')
