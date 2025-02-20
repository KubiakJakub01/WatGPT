# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WatscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

import scrapy

class TimetableItem(scrapy.Item):
    date = scrapy.Field()
    block_id = scrapy.Field()
    course_code = scrapy.Field()
    info = scrapy.Field()
    teacher_name = scrapy.Field()
    room = scrapy.Field()
    building = scrapy.Field()
    group_code = scrapy.Field()

class GroupItem(scrapy.Item):
    group_code = scrapy.Field()
    group_url = scrapy.Field()

class PageContentItem(scrapy.Item):
    """Item for storing the extracted text from .post-content."""
    heading = scrapy.Field()
    content = scrapy.Field()
    source_url = scrapy.Field()   # URL of the page
    page_number = scrapy.Field()  # For the chunk DB, can default to 0 or 1

class FileDownloadItem(scrapy.Item):
    """
    Item for downloading a file (doc, pdf, xls, etc.) 
    using a custom pipeline.
    """
    file_urls = scrapy.Field()  # Scrapy's FilesPipeline expects 'file_urls'
    files = scrapy.Field()      # Will be populated by FilesPipeline
    dir_name = scrapy.Field()   # The subfolder name where we'll store it
    origin_url = scrapy.Field() # Which page triggered the download