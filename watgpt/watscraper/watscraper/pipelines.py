# pylint: disable=too-few-public-methods
"""
Define your item pipelines here
Don't forget to add your pipeline to the ITEM_PIPELINES setting
See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from scrapy.pipelines.files import FilesPipeline

from watgpt.db.sql_db import SqlDB
from watgpt.utils import log_info
from watgpt.watscraper.watscraper.text_chunker import TextChunker
from watscraper.items import GroupItem, PageContentItem, TimetableItem

from .extract import extract_text_from_file


class WatscraperPipeline:
    def process_item(self, item, _spider):
        return item


class GroupPipeline:
    """
    Pipeline for processing GroupItem objects.

    This pipeline:
      - Opens a database connection and creates the timetable schema.
      - Inserts group records into the database.
      - Caches group IDs to avoid duplicate insertions.
    """

    def __init__(self):
        self.db = SqlDB()
        self.groups_cache = {}

    def process_item(self, item, _spider):
        if isinstance(item, GroupItem):
            group_code = item.get('group_code')
            if group_code and group_code not in self.groups_cache:
                group_id = self.db.insert_group(group_code)  # new SQLAlchemy method
                self.groups_cache[group_code] = group_id
                log_info(f"Inserted group '{group_code}' with id {group_id}")
        return item


class TimetablePipeline:
    def __init__(self):
        self.db = SqlDB()
        self.groups_cache = {}

    def process_item(self, item, _spider):
        if isinstance(item, TimetableItem):
            date_str = item.get('date')
            try:
                dt = datetime.strptime(date_str, '%Y_%m_%d')
                formatted_date = dt.strftime('%Y-%m-%d')
            except ValueError as e:
                log_info(f"Error parsing date '{date_str}': {e}")
                formatted_date = date_str  # Fallback to original string if conversion fails

            group_code = item.get('group_code', 'WCY24IX3S0')
            if group_code not in self.groups_cache:
                group_id = self.db.insert_group(group_code)
                self.groups_cache[group_code] = group_id
            else:
                group_id = self.groups_cache[group_code]

            teacher_name = item.get('teacher_name')
            teacher_id = self.db.insert_teacher(teacher_name) if teacher_name else None

            course_id = self.db.insert_course(item.get('course_code'))

            lesson_id = self.db.insert_lesson(
                group_id=group_id,
                course_id=course_id,
                teacher_id=teacher_id,
                lesson_date=formatted_date,
                block_id=item.get('block_id'),
                room=item.get('room'),
                building=item.get('building'),
                info=item.get('info'),
            )
            log_info(f"Inserted lesson with id {lesson_id} for group '{group_code}'")
        return item


class PostContentPipeline:
    """
    This pipeline:
      1) Creates site_chunks table (where we store web content).
      2) Uses a token-based splitter to chunk the text from PageContentItem.
      3) Inserts each chunk into site_chunks.
    """

    def __init__(self):
        self.db = SqlDB()

    def process_item(self, item, _spider):
        if isinstance(item, PageContentItem):
            heading = item.get('heading', 'No Heading')
            full_text = item.get('content', '')
            source_url = item.get('source_url', '')
            chunker = TextChunker(tokenizer_model='gpt2')
            text_chunks = chunker.chunk_text_token_based(
                full_text, max_tokens=1024, overlap_tokens=20
            )

            for text_chunk in text_chunks:
                self.db.create_chunk(
                    source_url=source_url,
                    file_url=None,  # no file URL for site
                    title=heading,
                    content=text_chunk,
                )
        return item


class CustomFilesPipeline(FilesPipeline):
    """
    1) Saves files to FILES_STORE/<dir_name>/<original_filename>
    2) After download, parses the file -> chunks text -> stores in file_chunks table.
    """

    def open_spider(self, spider):
        # pylint: disable=attribute-defined-outside-init
        self.db = SqlDB()
        super().open_spider(spider)

    def file_path(self, request, response=None, info=None, *, item=None):
        # Parse the URL to get the original file name without query parameters.
        parsed = urlparse(request.url)
        original_filename = Path(parsed.path).name

        # Get the desired directory name from the item (set by spider).
        if item is not None:
            dir_name = item.get('dir_name', '')
            if dir_name:
                # Return path as: <dir_name>/<original_filename>
                return str(Path(dir_name) / original_filename)
        return original_filename

    def item_completed(self, results, item, info):
        super_item = super().item_completed(results, item, info)

        for success, file_info in results:
            if success:
                local_path = file_info['path']
                downloaded_url = file_info['url']
                source_page_url = item.get('origin_url', '')
                file_text = extract_text_from_file(str(Path(self.store.basedir) / local_path))
                # Chunk the extracted text.
                chunker = TextChunker(tokenizer_model='gpt2')
                text_chunks = chunker.chunk_text_token_based(
                    file_text, max_tokens=1024, overlap_tokens=20
                )
                file_name = Path(local_path).name

                for text_chunk in text_chunks:
                    self.db.create_chunk(
                        source_url=source_page_url,
                        file_url=downloaded_url,
                        title=file_name,
                        content=text_chunk,
                    )

        return super_item
