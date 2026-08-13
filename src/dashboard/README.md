# Dashboard

Creates a visualization dashboard for the scraped jobs.

## Introduction

The `dashboard` has been written with `Streamlit`.

The dashobard provides insights on the job market on a country level (currently only Finland) which includes:

- **Trend** — postings per month over a fixed 24-month window, stacked by seniority level, so
  a change in volume can be read back to the levels that moved.
- **Top recruiting companies** — ranked by open roles under the active filters.
- **Momentum** — each seniority level's, or each region's, change against the previous month.
- **Distribution** — job fields stacked by seniority level, or regions stacked by job field.
  Hovering a band reads out its count; each row's sparkline is that row's shape across the
  selected time period, cut into six slices, so it describes the same postings as the bar
  beside it.
- **Latest jobs** — the postings themselves, searchable and paged.

Two rules keep the panels honest, and both are visible on the page:

- A panel relaxes the filters it draws — the field breakdown ignores the job field filter,
  the momentum-by-region view ignores the region filter — or its chart would collapse to a
  single row. Each panel's subtitle states which filters it dropped.
- Every KPI card repeats the filter combination it was measured under, so a scoped "top
  recruiter" is not read as a national one.

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

## Theming

The app is built to a fixed visual design, so most of the page is markup the app authors
rather than stock Streamlit widgets. A few constraints follow from that:

- The design tokens are mirrored in three places, and all three have to be changed
  together: `.streamlit/config.toml` (Streamlit's own chrome), `theme.py` (the Plotly
  template and the Python constants) and `styles.py` (the injected stylesheet).
- The injected CSS targets `data-testid`, `data-baseweb` and the `st-key-*` classes
  Streamlit derives from container keys. It never targets the hashed
  `.st-emotion-cache-*` class names, which change between Streamlit releases and would
  break the styling on upgrade.
- Plotly figures are rendered with `theme=None`. Without it Streamlit substitutes its own
  template and discards the figure's.
- Every stacked chart draws from one palette, `theme.STACK_RAMP_STEPS`. Its steps are spread
  across the accent ramp on purpose: neighbouring steps cannot be told apart once two
  segments touch, and the lightest step disappears against the page. For the same reason
  each swatch and segment boundary carries a hairline outline. Seniority colors are bound to
  the level name; job field colors are bound to rank, because which fields are on screen
  depends on the filters, and the legend above the bars is what names them.
- Fonts are vendored under `static/fonts/` and served through
  `[server] enableStaticServing`, so the app does not depend on an external font host.
- Every value rendered into the hand-written HTML in `components.py` is passed through
  `html.escape`, because it comes from scraped job posts.

## Tests

Unit tests cover `queries.py`, `pre_processing.py`, `load_resources.py`/`load_defaults.py`, `load_data.py` (mocked DB/secrets), `plots.py`, and `tables.py`. Run from this directory:

```bash
cd src/dashboard
pytest tests/
```
