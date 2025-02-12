from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service

def scrape_timetable(url):
    # 1) Configure Selenium to use headless Chrome
    service = Service(r'C:\\watGPT_project\\WatGPT-text_extraction\\webdriver\\chromedriver-win64\\chromedriver.exe')
    service.start()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")         # run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 2) Instantiate the WebDriver (make sure you have ChromeDriver installed)
    driver = webdriver.Chrome(options=chrome_options)

    # 3) Request the page and let it load
    driver.get(url)
    # Give it a few seconds to render dynamically loaded elements, if needed
    time.sleep(3)

    # 4) Get the final, rendered HTML (including JS-generated content)
    html = driver.page_source

    # 5) We’re done with the browser session
    driver.quit()

    # 6) Now parse using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Find each day container: <div class="day 2025_01_19 ">
    day_divs = soup.find_all("div", class_="day")

    all_days_data = []

    for day_div in day_divs:
        classes = day_div.get("class", [])
        if len(classes) < 2:
            continue

        day_label = classes[1]  # e.g. "2025_01_19"

        blocks_div = day_div.find("div", class_="blocks")
        if not blocks_div:
            continue

        block_divs = blocks_div.find_all("div", class_="block")

        block_data_list = []
        for block in block_divs:
            block_title = block.get("title", "")
            raw_text = block.get_text(separator="\n").strip()
            lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

            block_data = {
                "title": block_title,
                "lines": lines,
            }
            block_data_list.append(block_data)

        if block_data_list:
            all_days_data.append({
                "day": day_label,
                "blocks": block_data_list
            })

    return all_days_data

if __name__ == "__main__":
    url = "https://planzajec.wcy.wat.edu.pl/pl/rozklad?grupa_id=WCY24IV1N2"
    results = scrape_timetable(url)

    # 7) Write out to a text file
    with open("timetable.txt", "w", encoding="utf-8") as f:
        for day_dict in results:
            f.write(f"day {day_dict['day']}\n")
            for block in day_dict['blocks']:
                if block['title']:
                    f.write(f'title="{block["title"]}"\n')
                for line in block['lines']:
                    f.write(line + "\n")
            f.write("\n")
