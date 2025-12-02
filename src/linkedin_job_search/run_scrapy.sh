#!/bin/bash

# Initialize Conda
source /path/to/conda/activate/script lja

# Navigate to the Scrapy project directory
cd /path/to/Linkedin_job_analysis/src/linkedin_job_search

# Run the Scrapy spider
scrapy crawl job_scraper -a country=finland -a period=past_2_hours

# Deactivate the conda environment
conda deactivate
