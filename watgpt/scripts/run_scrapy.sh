#!/usr/bin/env bash
# Change directory to where scrapy.cfg is located
cd "$(dirname "$0")"
cd ../watscraper

if [ "$1" = "timetable" ]; then
    if [ -n "$2" ]; then
        echo "Running timetable spider with target groups: $2"
        scrapy crawl timetable -a target_groups="$2"
    else
        echo "Running timetable spider with default target groups"
        scrapy crawl timetable
    fi
elif [ "$1" = "all_files" ]; then
    echo "Running all_files spider"
    scrapy crawl all_files
elif [ "$1" = "both" ]; then
    # When both spiders are to be run, pass the target groups to timetable.
    if [ -n "$2" ]; then
        echo "Running timetable spider with target groups: $2"
        scrapy crawl timetable -a target_groups="$2"
    else
        echo "Running timetable spider with default target groups"
        scrapy crawl timetable
    fi
    echo "Running all_files spider"
    scrapy crawl all_files
else
    echo "Unknown spider specified. Exiting."
    exit 1
fi
