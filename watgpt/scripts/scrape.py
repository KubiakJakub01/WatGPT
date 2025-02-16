import argparse

from ..scraper import SiteCrawler


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='The URL to start crawling from.',
    )
    parser.add_argument(
        '--exclude',
        type=str,
        nargs='+',
        default=[],
        help='A list of URLs to skip entirely during crawling.',
    )
    parser.add_argument(
        '--download_folder',
        type=str,
        default='downloads',
        help='Directory path to store downloaded PDF files.',
    )
    parser.add_argument(
        '--info_file',
        type=str,
        default='scrape_info.txt',
        help='File path where we log scraped text and download messages.',
    )

    return parser.parse_args()


def main(url: str, exclude: list, download_folder: str, info_file: str):
    crawler = SiteCrawler(url, exclude, download_folder, info_file)
    crawler.run()


if __name__ == '__main__':
    args = parse_args()
    main(args.url, args.exclude, args.download_folder, args.info_file)
