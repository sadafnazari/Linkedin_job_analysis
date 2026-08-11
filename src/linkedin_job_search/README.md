# LinkedIn Job Search

Scrapes the linkedin job posts based on a given country.

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
  - `past_2_hours`
  - `past_24_hours`
  - `past_week`
  - `past_month`
  - `any_time`

```bash
cd src/linkedin_job_search
scrapy crawl job_scraper -a country=finland -a period=past_2_hours
```

Note: LinkedIn has a 1000-result limit per search query. For larger datasets, use overlapping time windows to ensure complete coverage. For instance, set the period for the past two hours and run the scraper every hour.

Running the scraper periodically can be done with `crontab` job with the `run_scrapy.sh` helper script. The script already guards against overlapping/stuck runs with a `flock` lock and caps each run with a `timeout`, so the cron job itself just needs to append to a single log file.

Open and edit the cron table with the following command:
```bash
crontab -e
```
Then, add the job and modify the command:
```bash
0 */1 * * * /bin/bash /path/to/run_scrapy.sh >> /path/to/scrapy.log 2>&1
```

Set up log rotation for that file (e.g. with `logrotate`) rather than writing a new timestamped log per run, to keep disk usage bounded.

## How normalization works

Scraped items pass through two pipelines, in this order:

1. `LinkedinJobSearchPipeline` cleans the raw scraped strings: it parses relative dates
   ("3 days ago") into timestamps, strips HTML from the description, and maps the free-text
   fields onto structured ones — `location` into `city`/`region`/`country`, and
   `job_function` into one or more canonical `job_fields`.

   That mapping is driven entirely by the JSON files in `resources/<country>/`, not by
   per-country code. `cities_and_regions_<country>.json` resolves a location string to a
   city and its region; `job_fields_<country>.json` lists each canonical job field together
   with the alternative names LinkedIn uses for it. Improving the mapping means editing
   those files, not the pipeline.

2. `PostgresPipeline` creates the `jobs` table if it is missing and inserts the item,
   skipping the insert if the same `job_url` was already inserted within the past two hours.
   That window is what makes the overlapping scrape schedule above safe: a post seen by two
   consecutive runs is stored once.

## Adding a new country

`configs/scrapy_config.json` already carries the LinkedIn `geo_id` for every country, so
adding one is a matter of supplying its reference data:

1. Create `resources/<country>/` with three files, matching the shape of the Finland ones:
   - `cities_and_regions_<country>.json`
   - `job_fields_<country>.json`
   - `seniority_levels_<country>.json`
2. Add an entry for the country to `configs/streamlit_config.json` with its dashboard
   defaults. The dashboard validates these against the loaded options at startup, so a
   default that isn't present in the resource files raises immediately rather than being
   silently replaced.

## Tests

Unit tests cover `pipelines.py` (date/location/job-field normalization, Postgres dedup logic) and the spider's `parse`/`parse_job` callbacks (using saved HTML fixtures, no network calls). Run from this directory so relative resource paths resolve:

```bash
cd src/linkedin_job_search
pytest tests/
```
