#!/usr/bin/env python3
import os
import stat
import subprocess
from pathlib import Path
import argparse
from watgpt.db.database import init_db

def ensure_executable(script_path: Path) -> None:
    """
    Ensure that the given script has executable permissions.
    """
    if not os.access(script_path, os.X_OK):
        # Add execute permission for the owner, group, and others.
        st = os.stat(script_path)
        os.chmod(script_path, st.st_mode | stat.S_IEXEC)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run 'timetable' and/or 'all_files' spiders via the Bash script."
    )
    parser.add_argument(
        "--only",
        type=str,
        default="",
        help="Spider name to run (e.g., 'timetable' or 'all_files'). If empty, both spiders will run."
    )
    return parser.parse_args()

def main(spider_name: str):

    init_db()
    # The Bash script is located at: watgpt/scripts/run_scrapy.sh
    # Since this file (scrape.py) is in the same folder, we can resolve it relative to __file__.
    script_path = (Path(__file__).parent / "run_scrapy.sh").resolve()

    # Ensure the Bash script is executable so the user doesn't have to manually chmod it.
    ensure_executable(script_path)

    if not script_path.exists():
        raise FileNotFoundError(f"Cannot find the script: {script_path}")

    # Call the Bash script with or without a spider argument.
    if spider_name:
        print(f"Running spider '{spider_name}' via {script_path}")
        subprocess.run([str(script_path), spider_name], check=True)
    else:
        print("No spider specified -> running both 'timetable' and 'all_files' spiders.")
        subprocess.run([str(script_path)], check=True)

if __name__ == "__main__":
    args = parse_args()
    main(args.only)
