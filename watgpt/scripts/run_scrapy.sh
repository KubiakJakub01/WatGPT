#!/usr/bin/env bash

# 1) Move into the directory that contains scrapy.cfg:
cd "$(dirname "$0")"          # moves into watgpt/scripts
cd ../watscraper/watscraper   # now at watgpt/watscraper/watscraper => where scrapy.cfg is

# 2) If you passed "timetable" or "all_files" to the script, only run those
#    Otherwise, run both by default

if [ -z "$1" ]; then
    echo "No spider name passed => running both timetable and all_files"
    #scrapy crawl timetable
    scrapy crawl timetable -a target_groups="WCY24IV1N2"
    scrapy crawl all_files
else
    echo "Running spider: $1"
    scrapy crawl "$1"
fi
