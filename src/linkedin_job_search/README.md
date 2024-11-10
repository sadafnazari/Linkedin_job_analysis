# LinkedIn Job Search

Scrapes the linkedin job posts on a country level.

## Introduction

`Linkedin job search` has been written with `Scrapy`. It can be customized with different criteria, as one can choose the country and the period of scraping, e.g. Finland.

The retrieved information is:
- date_posted
- title
- company
- location
- city
- region
- country
- seniority_level
- employment_type
- job_function
- job_fields
- industries
- description
- job_url

The job information will be stored in a `Postgresql` database.

## Usage

The process can be done by calling the scraper to crawl the data with the following command.
Two arguments should be given to the scraper:
- country: the name of the country. If it has more than one word, just replace the `space` with `_`. e.g. `New_Zealand`.
- period: the basis for the scraper to look for. options are:
  - `daily`
  - `weekly`
  -  `monthly`
  - `any_time`

```bash
cd src/linkedin_job_search
scrapy crawl job_scraper -a country=finland -a period=daily
```

Running the scraper periodically can be done with `crontab` job with the `run_scrapy.sh` helper script.

Open and edit the cron table with the following command:
```bash
crontab -e
```
Then, add the job and modify the command:
```bash
00 24 * * * /bin/bash /path/to/run_scrapy.sh >> /path/to/logs.log 2>&1
```
