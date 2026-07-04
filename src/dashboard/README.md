# Dashboard

Creates a visualization dashboard for the scraped jobs.

## Introduction

The `dashboard` has been written with `Streamlit`.

The dashobard provides insights on the job market on a country level (currently only Finland) which includes:

- Demonstrating total number of jobs over a certain period (daily, weekly, monthly, yearly).
- Demonstrating the companies with highest recruiting companies based on filters on the region, job field, seniority level and time period.
- Demonstrating the demand for jobs based on selected filters.
- Demonstrating the latest job posts.

## Usage

For running locally, the following command should be executed in the root project directory:
```bash
streamlit run src/dashboard/app.py
```

## Tests

Unit tests cover `queries.py`, `pre_processing.py`, `load_resources.py`/`load_defaults.py`, `load_data.py` (mocked DB/secrets), `plots.py`, and `tables.py`. Run from this directory:

```bash
cd src/dashboard
pytest tests/
```
