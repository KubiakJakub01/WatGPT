import os
import requests
from urllib.parse import urljoin, urlparse
from collections import deque
from bs4 import BeautifulSoup

class SiteCrawler:
    def __init__(self, start_url, exclude_urls, download_folder, info_file):
        """
        :param start_url:     The root URL to start crawling from.
        :param exclude_urls:  A list of URLs to skip entirely during crawling.
        :param download_folder: Directory path to store downloaded PDF files.
        :param info_file:     File path where we log scraped text and download messages.
        """
        self.start_url = start_url
        self.exclude_urls = set(exclude_urls)  # convert to set for faster lookup
        self.download_folder = download_folder
        self.info_file = info_file
        os.makedirs(self.download_folder, exist_ok=True)

        self.visited = set()   # Keep track of visited URLs (HTML pages)
        self.queue = deque([self.start_url])  # A queue for BFS or DFS

    def run(self):
        """Main entry point for the crawler."""
        while self.queue:
            current_url = self.queue.popleft()
            if current_url in self.visited:
                continue
            self.visited.add(current_url)

            # If this URL should be ignored, skip it
            if self.should_ignore_url(current_url):
                continue

            print(f"[INFO] Crawling: {current_url}")
            self.crawl_page(current_url)

    def crawl_page(self, url):
        """
        Fetch, parse, and handle the page at `url`.
         - Extract text and log it to scrape_info.txt
         - Find links for subpages or PDFs, handle them accordingly
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            return

        # Only parse if it's HTML
        content_type = response.headers.get("Content-Type", "").lower()
        if "text/html" not in content_type:
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # 1) Scrape text and log it
        page_text = self.extract_text(soup)
        self.log_info(f"Scraped text from this site: {url}\n{page_text}\n\n")

        # 2) Find and process links
        for link_tag in soup.find_all("a", href=True):
            href = link_tag["href"].strip()
            absolute_url = urljoin(url, href)

            # If the link should be ignored, skip it
            if self.should_ignore_url(absolute_url):
                continue

            # Check PDF vs. subpage
            if self.is_pdf(absolute_url):
                self.handle_pdf_link(absolute_url, url)
            else:
                # If it's an HTML page in the same domain, consider crawling it
                if self.is_same_domain(absolute_url, self.start_url):
                    if absolute_url not in self.visited and absolute_url not in self.queue:
                        self.queue.append(absolute_url)

    def extract_text(self, soup):
        """
        Given a BeautifulSoup object, return the extracted text in a clean format.
        This is a simple approach: soup.get_text().
        You can refine as needed (e.g., removing scripts, style tags, etc.).
        """
        text = soup.get_text(separator="\n", strip=True)
        return text

    def handle_pdf_link(self, pdf_url, current_url):
        """
        Download the PDF file from `pdf_url` into the download folder (once only).
        Log the action to scrape_info.txt
        """
        filename = os.path.basename(urlparse(pdf_url).path)
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        file_path = os.path.join(self.download_folder, filename)

        if os.path.exists(file_path):
            print(f"[INFO] Already downloaded, skipping: {file_path}")
            return

        print(f"[INFO] Downloading PDF: {pdf_url}")
        try:
            with requests.get(pdf_url, stream=True, timeout=15) as r:
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            
            self.log_info(f"Downloaded PDF {filename} from this site {current_url}\n")
        except requests.RequestException as e:
            print(f"[ERROR] Failed to download {pdf_url}: {e}")

    def log_info(self, message):
        """
        Append a message to the info_file. This can include scraped text or PDF logs.
        """
        with open(self.info_file, "a", encoding="utf-8") as f:
            f.write(message)

    def should_ignore_url(self, url):
        """
        Return True if this URL should NOT be visited or processed:
        1) It's in the exclude_urls list
        2) It contains "gallery" (case-insensitive)
        3) It contains "aktualnosci" (case-insensitive)
        4) It ends with .jpg or .png
        """
        # 1) Check the exclude list
        if url in self.exclude_urls:
            return True

        # 2) Check if 'gallery' appears anywhere in the URL
        if "gallery" in url.lower():
            return True

        # 3) Check if 'aktualnosci' appears anywhere in the URL
        if "aktualnosci" in url.lower():
            return True

        # 4) Check the file extension
        path = urlparse(url).path.lower()
        if path.endswith(".jpg") or path.endswith(".png"):
            return True

        return False

    @staticmethod
    def is_pdf(url):
        """Naive check for PDF by extension. Refine if needed."""
        return url.lower().endswith(".pdf")

    @staticmethod
    def is_same_domain(url, root_url):
        """Check if `url` shares the same domain as `root_url`."""
        return urlparse(url).netloc == urlparse(root_url).netloc


if __name__ == "__main__":
    START_URL = "https://www.wcy.wat.edu.pl/wydzial/ksztalcenie/informacje-studenci"
    # We now use a list for excluded URLs. You can add more if needed.
    EXCLUDE_URLS = [
        "https://www.wcy.wat.edu.pl/wydzial/aktualnosci/dzialalnosc-studencka"
    ]
    DOWNLOAD_FOLDER = "output_data\downloaded_pdfs"
    INFO_FILE = "output_data\scrape_info.txt"

    crawler = SiteCrawler(
        start_url=START_URL,
        exclude_urls=EXCLUDE_URLS,
        download_folder=DOWNLOAD_FOLDER,
        info_file=INFO_FILE
    )
    crawler.run()
