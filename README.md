# LinkedIn_job_analysis

LinkedIn Job Analysis project is based on the jobs, that are publicly available on Linkedin and the scraped data will remain under LinkedIn ownership.

This project is only implemented for learning purposes, and any inappropriate use of data is not the author's responsibility.

# Introduction

This project has been written with `Scrapy`. It can be customized with different criteria, as one can choose the country and the period of scraping, e.g. Finland.

The retrieved information is:
- date_posted
- title
- company
- location
- seniority_level
- employment_type
- job_function
- industries
- description
- job_url

The job information will be stored in a `SQLite` database.

# Setup

It is recommended to use `conda` for this project.
```bash
conda create --name lja python==3.12.0
conda activate lja 
```

The requirements can be installed with the following command:
```bash
pip install -r requirements.txt
```

# Usage

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
# Note 

LinkedIn has set a limit on the publicly available jobs number, and only allows scraping the first 1000 jobs.