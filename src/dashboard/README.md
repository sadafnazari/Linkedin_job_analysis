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

### Running against a local snapshot

`preview_with_snapshot.py` runs the same app against a parquet export of the
`jobs` table instead of Postgres, so the dashboard can be developed and reviewed
without database credentials:

```bash
streamlit run src/dashboard/preview_with_snapshot.py
```

It expects the snapshot at `data/jobs.parquet` (gitignored). To create one, read
the same columns `load_data.py` selects and write them out:

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:password@host:port/dbname")
pd.read_sql("SELECT * FROM jobs", engine).to_parquet("data/jobs.parquet")
```

Because a snapshot goes stale, the harness shifts `date_posted` forward so its
most recent post lands at today — otherwise the default "Past month" filter would
match nothing. Row counts and rankings are real; the dates are not.

## Tests

Unit tests cover `queries.py`, `pre_processing.py`, `load_resources.py`/`load_defaults.py`, `load_data.py` (mocked DB/secrets), `plots.py`, and `tables.py`. Run from this directory:

```bash
cd src/dashboard
pytest tests/
```
