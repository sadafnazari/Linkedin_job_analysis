# LinkedIn job analysis

Scrapes publicly available LinkedIn job posts and turns them into a job-market analytics
dashboard. The scraped data remains under LinkedIn ownership.

The dashboard is deployed on the
[Streamlit Community Cloud](https://linkedin-job-analysis-dashboard.streamlit.app/).

## Architecture

A scheduled scraper collects job posts hourly and writes them to a Postgres database; the
dashboard reads from that same database and renders the analytics.

```
scheduled scraper (Scrapy)  →  Postgres  →  dashboard (Streamlit)
```

The two halves are independent — they only share the configuration and reference data in
`configs/` and `resources/`. Each has its own README:

- [`src/linkedin_job_search`](src/linkedin_job_search/README.md) — the Scrapy project that
  collects and normalizes job posts.
- [`src/dashboard`](src/dashboard/README.md) — the Streamlit app that visualizes them.

## Quickstart

```bash
git clone https://github.com/<your-account>/Linkedin_job_analysis.git
cd Linkedin_job_analysis

# conda
conda create -n lja python=3.12 && conda activate lja
# or venv
python -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt
```

Then follow the sub-README for whichever half you want to run — the scraper needs database
credentials, the dashboard can be run against a local snapshot without any.

## Configuration

| File | Controls |
| --- | --- |
| `configs/scrapy_config.json` | LinkedIn `geo_id` per country, the scraper's time-range codes and user agent. |
| `configs/streamlit_config.json` | Per-country dashboard defaults (region, job field, seniority level, time period). Validated against the loaded options at startup. |
| `resources/<country>/*.json` | Reference data for one country: cities and regions, job fields with their alternative names, seniority levels. Used by both halves. |

Credentials are not checked in: the scraper reads `configs/.env` and the dashboard reads
`.streamlit/secrets.toml`.

## Repository layout

```
configs/       shared configuration (see above)
resources/     per-country reference data, one directory per country
src/           the two halves of the project
data/          local snapshots and scratch data (gitignored)
```

## Tests and linting

Each half has its own test suite. Run each from inside its own directory, so the relative
resource and config paths resolve:

```bash
cd src/linkedin_job_search && pytest tests/
cd src/dashboard && pytest tests/
```

Formatting and static checks run through pre-commit (black, isort, mypy, pyupgrade,
autoflake):

```bash
pre-commit run --all-files
```

## Notes

- This project is only implemented for learning purposes, and any inappropriate use of data
  is not the author's responsibility.

- While the project is designed to be country-generic, only Finland currently has the full
  reference data in `resources/`, and the functionality has only been tested on the Finnish
  job market.

## References

The `cities_and_regions_finland.json` file is a modified version of the list of cities and
regions from [simplemaps](https://simplemaps.com/data/fi-cities).
