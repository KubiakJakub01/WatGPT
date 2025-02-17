import re

import requests
from bs4 import BeautifulSoup

from ..utils import log_warning


def scrape_timetable(url):
    """
    1) Fetch the page with requests.
    2) Locate the hidden <div class="lessons hidden">.
    3) For each <div class="lesson">, extract date, block_id, name, info,
       parse out teacher_name from info, parse out room & building from the name lines.
    4) Returns a list of dicts, each representing one lesson:
       {
         "date": "2024_10_05",
         "block_id": "block1",
         "course_code": "MumII",
         "info": "...",
         "teacher_name": "Olejniczak Jarosław",
         "room": "308",
         "building": "100"
       }
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')

    lessons_div = soup.find('div', class_='lessons hidden')
    if not lessons_div:
        log_warning("No <div class='lessons hidden'> found.")
        return []

    lesson_divs = lessons_div.find_all('div', class_='lesson')

    all_lessons = []

    for lesson in lesson_divs:
        date_span = lesson.find('span', class_='date')
        block_id_span = lesson.find('span', class_='block_id')
        name_span = lesson.find('span', class_='name')
        info_span = lesson.find('span', class_='info')

        date_str = date_span.get_text(strip=True) if date_span else ''
        block_id = block_id_span.get_text(strip=True) if block_id_span else ''
        info_str = info_span.get_text(strip=True) if info_span else ''

        # Skip if info is '- - (Rezerwacja) - -'
        if info_str == '- - (Rezerwacja) - -':
            continue

        # Attempt to parse the teacher name out of 'info' by splitting on " - "
        # Example: "Metody uczenia maszynowego II - (Wykład) - Olejniczak Jarosław"
        # We want teacher_name = "Olejniczak Jarosław"
        teacher_name = ''
        parts = info_str.split(' - ')
        if len(parts) >= 3:
            teacher_name = parts[-1].strip()
        # If there's fewer than 3 parts, teacher_name remains ""

        # The <span class="name"> might have multiple lines: course code, (w), room-building, etc.
        if name_span:
            raw_html = name_span.decode_contents()
            name_str = raw_html.replace('<br/>', '\n').replace('<br>', '\n')
        else:
            name_str = ''

        lines = [line.strip() for line in name_str.split('\n') if line.strip()]

        # The first line is often the course code
        course_code = lines[0] if lines else ''

        # Parse room / building from lines beyond the first
        room_val = ''
        building_val = '100'  # default building

        # e.g. If there's a line with digits like "203 65" => room=203, building=65
        for ln in lines[1:]:
            if re.search(r'\d', ln):
                parts2 = ln.split()
                if len(parts2) == 1:
                    # e.g. "308" or "308S"
                    match = re.match(r'(\d+)', parts2[0])
                    if match:
                        room_val = match.group(1)
                        building_val = '100'
                else:
                    # e.g. ["203", "65"] or ["308", "S"]
                    match_room = re.match(r'(\d+)', parts2[0])
                    if match_room:
                        room_val = match_room.group(1)
                    match_bld = re.match(r'(\d+)', parts2[1])
                    building_val = match_bld.group(1) if match_bld else '100'
                break

        lesson_dict = {
            'date': date_str,
            'block_id': block_id,
            'course_code': course_code,
            'info': info_str,
            'teacher_name': teacher_name,  # extracted from info
            'room': room_val,
            'building': building_val,
        }
        all_lessons.append(lesson_dict)

    return all_lessons
