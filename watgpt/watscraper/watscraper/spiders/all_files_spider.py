import os
import scrapy
from urllib.parse import urljoin,urlparse
from watscraper.items import PageContentItem, FileDownloadItem


class AllFilesSpider(scrapy.Spider):
    name = "all_files"
    start_urls = [
        "https://www.wcy.wat.edu.pl/pl/wydzial/ksztalcenie/informacje-studenci/informator-1-rok",
    ]

    def parse(self, response):
        """
        1) Extract heading & text from .post-content (exclude h3 text from main content).
        2) Save them to chunk DB via pipeline (PageContentItem).
        3) Identify file links => yield FileDownloadItem for custom pipeline.
        """

        # --- Extract heading (the first <h3> inside .post-content)
        heading = response.css("div.post-content h3::text").get() or ""

        # --- Extract all text from .post-content EXCEPT <h3> elements
        # This XPath selects every text node in .post-content, 
        # but excludes any <h3> by skipping nodes whose "self::h3" matches.
        content_text_nodes = response.xpath(
            '//div[@class="post-content"]//*[not(self::h3)]//text()'
        ).getall()

        # Clean up whitespace/newlines
        content_text = "\n".join(t.strip() for t in content_text_nodes if t.strip())

        # Yield a PageContentItem => triggers DB insert via PostContentPipeline
        yield PageContentItem(
            heading=heading,
            content=content_text,
            source_url=response.url,
            page_number=0,
        )

        # --- Identify file links (doc, pdf, xls, etc.), skipping typical images
        all_links = response.css("a[href]").xpath("@href").getall()
        for link in all_links:
            absolute_url = urljoin(response.url, link)
            if self.is_image_file(absolute_url):
                continue
            if self.is_file_link(absolute_url):
                # Folder name is the last path segment from this page's URL
                dir_name = self.get_last_path_part(response.url)
                yield FileDownloadItem(
                    file_urls=[absolute_url],
                    dir_name=dir_name,
                    origin_url=response.url
                )
            else:
                # If you want to follow other HTML pages, do so here:
                pass

    def is_image_file(self, url: str) -> bool:
        """Very naive check for typical image extensions."""
        url_lower = url.lower()
        return any(url_lower.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"])

    def is_file_link(self, url: str) -> bool:
        """Check if URL points to a downloadable file based on common extensions."""
        parsed = urlparse(url)
        path = parsed.path  # This automatically excludes query parameters (?download=1 etc)
        
        # Common file extensions to download
        ALLOWED_EXTENSIONS = {
            # Documents
            'pdf', 'doc', 'docx', 'odt', 'rtf', 'txt',
            # Spreadsheets
            'xls', 'xlsx', 'ods', 'csv',
            # Presentations
            'ppt', 'pptx', 'odp',
            # Archives
            'zip', 'rar', '7z', 'tar', 'gz'
        }
        
        ext = os.path.splitext(path)[1].lstrip('.').lower()
        
        return ext in ALLOWED_EXTENSIONS

    def get_last_path_part(self, url: str) -> str:
        parsed = urlparse(url)  # from urllib.parse
        parts = [p for p in parsed.path.split('/') if p]
        if parts:
            return parts[-1]
        return "unnamed-page"

