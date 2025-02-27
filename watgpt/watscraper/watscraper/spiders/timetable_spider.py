import re
from urllib.parse import urljoin

import scrapy

from watscraper.items import GroupItem, TimetableItem


class TimetableSpider(scrapy.Spider):
    name = 'timetable'
    start_urls = ['https://planzajec.wcy.wat.edu.pl/pl/rozklad']

    def __init__(self, *args, target_groups=None, **kwargs):
        """
        Optionally pass a comma-separated list of group codes that you want to scrape.
        Example:
          scrapy crawl timetable -a target_groups="WCY19IL1S0,WCY19IT1S0"
        """
        super().__init__(*args, **kwargs)
        if target_groups:
            # Create a set of target group codes for fast lookup.
            self.target_groups = set(target_groups.split(','))
            self.logger.info(f'Target groups: {self.target_groups}')
        else:
            self.target_groups = None

    def parse(self, response):
        # Extract group options from the drop-down.
        options = response.css('select.ctools-jump-menu-select option')
        for option in options:
            group_text = option.xpath('normalize-space(text())').get()
            if group_text == '- Wybierz grupę -':
                continue
            value = option.xpath('./@value').get()
            if not value:
                continue
            parts = value.split('::')
            if len(parts) < 2:
                continue
            group_url = urljoin(response.url, parts[1].strip())
            group_code = group_text.strip()

            # If target_groups is specified, skip groups not in the list.
            if self.target_groups and group_code not in self.target_groups:
                continue

            # Yield a GroupItem for the GroupPipeline.
            yield GroupItem(group_code=group_code, group_url=group_url)

            # Immediately schedule a request to scrape the timetable for that group.
            yield scrapy.Request(
                url=group_url,
                callback=self.parse_timetable,
                meta={'group_code': group_code},
            )

    def parse_timetable(self, response):
        group_code = response.meta.get('group_code')
        lessons_div = response.css('div.lessons.hidden')
        if not lessons_div:
            self.logger.warning(f'No timetable found for group {group_code}.')
            return

        for lesson in lessons_div.css('div.lesson'):
            info_str = lesson.css('span.info::text').get(default='').strip()
            if info_str == '- - (Rezerwacja) - -':
                continue

            teacher_name = ''
            parts = info_str.split(' - ')
            if len(parts) >= 3:
                teacher_name = parts[-1].strip()

            name_texts = lesson.css('span.name::text').getall()
            lines = [text.strip() for text in name_texts if text.strip()]

            room_val = ''
            building_val = '100'
            for ln in lines[1:]:
                if re.search(r'\d', ln):
                    parts2 = ln.split()
                    if len(parts2) == 1:
                        match = re.match(r'(\d+)', parts2[0])
                        if match:
                            room_val = match.group(1)
                    else:
                        match_room = re.match(r'(\d+)', parts2[0])
                        if match_room:
                            room_val = match_room.group(1)
                        match_bld = re.match(r'(\d+)', parts2[1])
                        if match_bld:
                            building_val = match_bld.group(1)
                    break

            yield TimetableItem(
                date=lesson.css('span.date::text').get(default='').strip(),
                block_id=lesson.css('span.block_id::text').get(default='').strip(),
                course_code=lines[0] if lines else '',
                info=info_str,
                teacher_name=teacher_name,
                room=room_val,
                building=building_val,
                group_code=group_code,
            )
