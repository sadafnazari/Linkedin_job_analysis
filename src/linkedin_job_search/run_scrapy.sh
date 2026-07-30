#!/bin/bash

# Prevent overlapping runs if a previous invocation is still alive/stuck
exec 200>/tmp/run_scrapy.lock
flock -n 200 || { echo "$(date): previous run still active, skipping"; exit 1; }

# Initialize Conda
source /path/to/conda/activate/script lja

# Navigate to the Scrapy project directory
cd /path/to/Linkedin_job_analysis/src/linkedin_job_search

# Run the Scrapy spider, capped so a hang can't run past the next hourly trigger
timeout 45m scrapy crawl job_scraper -a country=finland -a period=past_2_hours

# Deactivate the conda environment
conda deactivate
