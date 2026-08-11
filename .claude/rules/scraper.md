---
paths:
  - "src/linkedin_job_search/**"
---

# Scraper rules

- Run `scrapy crawl` and `pytest` from `src/linkedin_job_search/`. Relative resource and
  config paths break from anywhere else.
- Location and job-field mapping is resource-driven. Fix a bad mapping by editing
  `resources/<country>/*.json`, never by adding a per-country branch to `pipelines.py`.
  See "How normalization works" in the README.
- Keep the two-hour `job_url` dedup guard in `PostgresPipeline`. The overlapping hourly
  scrape schedule relies on it to avoid duplicate rows.
- The spider self-retries login-wall and empty-page responses; LinkedIn serves those
  intermittently. Treat them as expected, not as fatal errors.
- Spider tests run against the saved HTML in `tests/fixtures/`. Tests must not make network
  calls — add a fixture instead.
