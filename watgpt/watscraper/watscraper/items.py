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