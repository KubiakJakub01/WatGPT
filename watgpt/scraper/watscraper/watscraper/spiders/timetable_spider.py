import re
import scrapy
from watscraper.items import TimetableItem

class TimetableSpider(scrapy.Spider):
    name = "timetable"
    
    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url] if url else []

    def parse(self, response):
        lessons_div = response.css('div.lessons.hidden')
        if not lessons_div:
            self.logger.warning("No <div class='lessons hidden'> found.")
            return

        for lesson in lessons_div.css('div.lesson'):
            info_str = lesson.css('span.info::text').get('').strip()
            
            # Skip reservations
            if info_str == '- - (Rezerwacja) - -':
                continue

            # Extract teacher name
            teacher_name = ''
            parts = info_str.split(' - ')
            if len(parts) >= 3:
                teacher_name = parts[-1].strip()

            # Process name span content (fix applied here)
            # Extract only the text nodes, not the raw HTML
            name_texts = lesson.css('span.name::text').getall()
            lines = [text.strip() for text in name_texts if text.strip()]

            # Parse room and building from the rest of the lines
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
                date=lesson.css('span.date::text').get('').strip(),
                block_id=lesson.css('span.block_id::text').get('').strip(),
                course_code=lines[0] if lines else '',  # Now properly extracted
                info=info_str,
                teacher_name=teacher_name,
                room=room_val,
                building=building_val
            )
