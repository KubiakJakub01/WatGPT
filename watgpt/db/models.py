from collections import namedtuple

ChunkRow = namedtuple(
    'ChunkRow',
    ['chunk_id', 'heading', 'content', 'source_file', 'page_number'],
)

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
