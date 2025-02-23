# all_files_crawl_spider.py
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.project import get_project_settings
from urllib.parse import urlparse, urljoin
from watscraper.items import PageContentItem, FileDownloadItem
import os
from watgpt.constants import ALLOWED_PATHS, DENIED_PATHS, DENIED_EXTENSIONS

class AllFilesSpider(CrawlSpider):
    name = "all_files"
    allowed_domains = ["wcy.wat.edu.pl"]
    start_urls = [
        "https://www.wcy.wat.edu.pl/wydzial/ksztalcenie/informacje-studenci"
    ]

    rules = (
        Rule(
            LinkExtractor(
                allow=ALLOWED_PATHS,
                deny=DENIED_PATHS,
                deny_extensions=DENIED_EXTENSIONS,
                unique=True,
            ),
            callback="parse_page",
            follow=True
        ),
    )

    def parse_page(self, response):
        """
        1) Extract heading & text from .post-content
        2) Yield PageContentItem
        3) Identify file links => yield FileDownloadItem
        """
        # Extract heading
        heading = response.css("div.post-content h3::text").get() or ""

        # Extract text from .post-content (excluding <h3>)
        content_text_nodes = response.xpath(
            '//div[@class="post-content"]//text()[normalize-space() and not(ancestor::script) and not(ancestor::style)]'
        ).getall()

        content_text = "\n".join(t.strip() for t in content_text_nodes if t.strip())

        yield PageContentItem(
            heading=heading,
            content=content_text,
            source_url=response.url,
            page_number=0,
        )

        # Identify and yield file download items
        for link in response.css("a[href]::attr(href)").getall():
            absolute_url = urljoin(response.url, link)
            if self.is_file_link(absolute_url):
                dir_name = self.get_last_path_part(response.url)
                yield FileDownloadItem(
                    file_urls=[absolute_url],
                    dir_name=dir_name,
                    origin_url=response.url
                )

    def is_file_link(self, url: str) -> bool:
        parsed = urlparse(url)
        path = parsed.path
        ALLOWED_EXTENSIONS = {
            'pdf','doc','docx','odt','rtf','txt',
            'xls','xlsx','ods','csv',
            'ppt','pptx','odp',
            'zip','rar','7z','tar','gz'
        }
        ext = os.path.splitext(path)[1].lstrip('.').lower()
        return ext in ALLOWED_EXTENSIONS

    def get_last_path_part(self, url: str) -> str:
        parsed = urlparse(url)
        parts = [p for p in parsed.path.split('/') if p]
        return parts[-1] if parts else "unnamed-page"
