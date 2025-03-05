import argparse
import os
import stat
import subprocess
from pathlib import Path

from watgpt.constants import TARGET_GROUPS
from watgpt.utils import create_marker_file, delete_marker_file, log_info


def ensure_executable(script_path: Path) -> None:
    """Ensure that the given script has executable permissions."""
    if not os.access(script_path, os.X_OK):
        st = os.stat(script_path)
        os.chmod(script_path, st.st_mode | stat.S_IEXEC)


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        Run one or both spiders: 'timetable' - for scraping timetable data 
        and/or 'all_files' - for scraping data from WAT websites and files.
        """
    )
    parser.add_argument(
        '--spider_name',
        type=str,
        choices=['timetable', 'all_files', 'both'],
        default='both',
        help=(
            "Which spider(s) to run. Possible values: 'timetable', "
            "'all_files', or 'both'. Defaults to 'both' if not specified."
        ),
    )
    return parser.parse_args()


def main(spider_name: str):
    # Remove any existing marker file
    delete_marker_file('scrape.done')

    # Resolve path to run_scrapy.sh
    script_path = (Path(__file__).parent / 'run_scrapy.sh').resolve()
    ensure_executable(script_path)

    if not script_path.exists():
        raise FileNotFoundError(f'Cannot find the script: {script_path}')

    if spider_name.lower() == 'timetable':
        log_info(
            f"Running spider '{spider_name}' with target groups '{TARGET_GROUPS}' via {script_path}"
        )
        subprocess.run([str(script_path), spider_name, TARGET_GROUPS], check=True)
    elif spider_name:
        log_info(f"Running spider '{spider_name}' via {script_path}")
        subprocess.run([str(script_path), spider_name], check=True)
    else:
        # If no spider specified, pass a keyword "both" and the target groups for timetable.
        log_info(
            f"""
            No spider specified -> running both 'timetable' and 'all_files' 
            spiders with target groups '{TARGET_GROUPS}'.
            """
        )
        subprocess.run([str(script_path), 'both', TARGET_GROUPS], check=True)

    create_marker_file('scrape.done')


if __name__ == '__main__':
    args = parse_args()
    main(args.spider_name)
