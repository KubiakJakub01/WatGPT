import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import re

def scrape_timetable(url):
    """
    1) Fetch the page with requests.
    2) Locate the hidden <div class="lessons hidden">.
    3) For each <div class="lesson">, extract date, block_id, name, info, color, teacher_short,
       plus parse out room & building from the name lines.
    4) Returns a list of dicts, each representing one lesson:
       {
         "date": "2024_10_05",
         "block_id": "block1",
         "course_code": "MumII",
         "info": "...",
         "color": "#CD5C5C",
         "teacher_short": "OJ",
         "room": "308",
         "building": "100"
       }
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    lessons_div = soup.find("div", class_="lessons hidden")
    if not lessons_div:
        print("No <div class='lessons hidden'> found.")
        return []

    lesson_divs = lessons_div.find_all("div", class_="lesson")

    all_lessons = []

    for lesson in lesson_divs:
        date_str = lesson.find("span", class_="date")
        block_id_span = lesson.find("span", class_="block_id")
        name_span = lesson.find("span", class_="name")
        info_span = lesson.find("span", class_="info")
        teacher_span = lesson.find("span", class_="sSkrotProwadzacego")

        date_str = date_str.get_text(strip=True) if date_str else ""
        block_id = block_id_span.get_text(strip=True) if block_id_span else ""
        info_str = info_span.get_text(strip=True) if info_span else ""
        teacher_str = teacher_span.get_text(strip=True) if teacher_span else ""

        if info_str == '- - (Rezerwacja) - -':
            continue

        # "name" block might have multiple lines: course code, (w), room-building, teacher short code, etc.
        if name_span:
            raw_html = name_span.decode_contents()
            name_str = raw_html.replace("<br/>", "\n").replace("<br>", "\n")
        else:
            name_str = ""

        lines = [line.strip() for line in name_str.split("\n") if line.strip()]

        course_code = lines[0] if lines else ""

        # Now we want to parse "room" and "building" from whichever line includes numeric tokens
        # We'll do a simple approach: if there's a line with digits that looks like:
        #   "203 65" => room=203, building=65
        #   "308 S" => maybe room=308, building=100 (since 'S' is not numeric)
        #   "308" => room=308, building=100
        # We'll just look for the line that has at least one digit.  Then parse tokens.
        room_val = ""
        building_val = "100"   # default building is "100"

        for ln in lines[1:]:
            if re.search(r"\d", ln):
                parts = ln.split()
                if len(parts) == 1:
                    match = re.match(r"(\d+)", parts[0])
                    if match:
                        room_val = match.group(1)  # "308"
                        building_val = "100"       # default
                else:
                    # e.g. ["203", "65"] or ["308", "S"]
                    # if second part is purely digits, building = that, else building=100
                    match_room = re.match(r"(\d+)", parts[0])  # "203"
                    if match_room:
                        room_val = match_room.group(1)
                    # check second part
                    match_bld = re.match(r"(\d+)", parts[1])
                    if match_bld:
                        building_val = match_bld.group(1)
                    else:
                        building_val = "100"
                break 

        if not room_val:
            pass

        lesson_dict = {
            "date": date_str,         # e.g. "2024_10_05"
            "block_id": block_id,     # e.g. "block1"
            "course_code": course_code,
            "info": info_str,         # e.g. "Metody uczenia maszynowego II - (Wykład) - Olejniczak Jarosław"
            "teacher_short": teacher_str,  # e.g. "OJ"
            "room": room_val,         # "308"
            "building": building_val  # "100" or "65"
        }
        all_lessons.append(lesson_dict)

    return all_lessons


if __name__ == "__main__":
    url = "https://planzajec.wcy.wat.edu.pl/pl/rozklad?grupa_id=WCY24IV1N2"
    result = scrape_timetable(url)
    #print(f"result {result}")

