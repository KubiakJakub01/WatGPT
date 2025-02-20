# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3
from datetime import datetime
from itemadapter import ItemAdapter
from watgpt.db.chunk_db import ChunkDB
from watscraper.items import GroupItem,TimetableItem, PageContentItem, FileDownloadItem
from scrapy.pipelines.files import FilesPipeline
from urllib.parse import urlparse
import os



class WatscraperPipeline:
    def process_item(self, item, spider):
        return item

class GroupPipeline:
    """
    Pipeline for processing GroupItem objects.
    
    This pipeline:
      - Opens a database connection and creates the timetable schema.
      - Inserts group records into the database.
      - Caches group IDs to avoid duplicate insertions.
    """
    def open_spider(self, spider):
        self.db = ChunkDB()
        self.db.create_timetable_schema()
        self.db.fill_block_hours()
        # Cache inserted groups keyed by group_code.
        self.groups_cache = {}

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Only process GroupItem objects.
        if isinstance(item, GroupItem):
            group_code = adapter.get("group_code")
            if group_code and group_code not in self.groups_cache:
                group_id = self.db.insert_group(group_code)
                self.groups_cache[group_code] = group_id
                spider.logger.info(f"Inserted group '{group_code}' with id {group_id}")
        return item

class TimetablePipeline:
    """
    Pipeline for processing TimetableItem objects.
    
    This pipeline:
      - Converts the date from "YYYY_MM_DD" to "YYYY-MM-DD".
      - Ensures the group exists (inserting it if needed) using a local cache.
      - Inserts teacher, course, and lesson data into the database.
    """
    def open_spider(self, spider):
        self.db = ChunkDB()
        self.db.create_timetable_schema()
        self.db.fill_block_hours()
        # Cache for groups to prevent duplicate group insertions.
        self.groups_cache = {}

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Only process TimetableItem objects.
        if isinstance(item, TimetableItem):
            # Convert the date string from "YYYY_MM_DD" to "YYYY-MM-DD".
            date_str = adapter.get("date")
            try:
                dt = datetime.strptime(date_str, "%Y_%m_%d")
                formatted_date = dt.strftime("%Y-%m-%d")
            except Exception as e:
                spider.logger.error(f"Error parsing date '{date_str}': {e}")
                formatted_date = date_str  # Fallback to original string if conversion fails

            # Ensure the group exists in the database.
            group_code = adapter.get("group_code") or "WCY24IX3S0"
            if group_code not in self.groups_cache:
                group_id = self.db.insert_group(group_code)
                self.groups_cache[group_code] = group_id
            else:
                group_id = self.groups_cache[group_code]

            # Insert teacher if available.
            teacher_name = adapter.get("teacher_name")
            teacher_id = None
            if teacher_name:
                teacher_id = self.db.insert_teacher(teacher_name)

            # Insert the course based on the course_code.
            course_code = adapter.get("course_code")
            course_id = self.db.insert_course(course_code)

            # Insert the lesson into the database.
            lesson_id = self.db.insert_lesson(
                group_id=group_id,
                course_id=course_id,
                teacher_id=teacher_id,
                lesson_date=formatted_date,
                block_id=adapter.get("block_id"),
                room=adapter.get("room"),
                building=adapter.get("building"),
                info=adapter.get("info")
            )
            spider.logger.info(f"Inserted lesson with id {lesson_id} for group '{group_code}'")
        return item

class PostContentPipeline:
    """
    Insert (heading, content, source_file) into pdf_chunks table via ChunkDB.
    """
    def open_spider(self, spider):
        self.db = ChunkDB()
        self.db.create_table_pdf_chunks()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        if isinstance(item, PageContentItem):
            adapter = ItemAdapter(item)
            heading = adapter.get("heading", "No Heading")
            content = adapter.get("content", "")
            source_file = adapter.get("source_url", "")
            page_number = adapter.get("page_number", 0)

            self.db.insert_chunk(
                heading=heading,
                content=content,
                source_file=source_file,  # store the URL as "source_file"
                page_number=page_number
            )

        # Return item so it can be passed to next pipeline if needed
        return item


class CustomFilesPipeline(FilesPipeline):
    """
    Saves files to:  FILES_STORE/<dir_name>/<original_filename>
    """
    def file_path(self, request, response=None, info=None, item=None):
        adapter = ItemAdapter(item)
        dir_name = adapter.get("dir_name", "no-dir")
        parsed_url = urlparse(request.url)
        filename = os.path.basename(parsed_url.path)

        # If there's no filename in the path, fallback:
        if not filename:
            filename = "unnamed_file"

        return f"{dir_name}/{filename}"