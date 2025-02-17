from collections import namedtuple

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
