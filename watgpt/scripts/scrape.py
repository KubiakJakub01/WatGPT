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
    return parser.parse_args()


def main(url: str, exclude: list, download_folder: str):
    crawler = SiteCrawler(url, exclude, download_folder)
    crawler.run()


if __name__ == '__main__':
    args = parse_args()
    main(args.url, args.exclude, args.download_folder)
