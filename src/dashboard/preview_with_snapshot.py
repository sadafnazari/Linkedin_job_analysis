"""Local preview harness: runs the dashboard against a parquet snapshot.

Lets the app be run and reviewed without Postgres credentials, using a local
export of the ``jobs`` table instead. Development aid only — the deployed app
always goes through ``load_data.py``. See the README for making the snapshot.

    streamlit run src/dashboard/preview_with_snapshot.py

It lives beside app.py so Streamlit still serves the vendored fonts from
``static/``, which are resolved relative to the entrypoint's directory.
"""

import runpy
from pathlib import Path

import pandas as pd
import streamlit as st

import load_data as load_data_module

DASHBOARD_DIR = Path(__file__).resolve().parent
SNAPSHOT = DASHBOARD_DIR / "../../data/jobs.parquet"

COLUMNS = [
    "date_posted",
    "title",
    "company",
    "region",
    "country",
    "seniority_level",
    "job_fields",
    "job_url",
]


@st.cache_data(ttl=43200)
def load_snapshot():
    """Stand in for load_data(), reading the snapshot instead of Postgres."""
    df = pd.read_parquet(SNAPSHOT, columns=COLUMNS)
    df = df[
        (df["seniority_level"] != "Not Applicable") & (df["region"] != "Unspecified")
    ].copy()
    # The snapshot stops before today, so the default "Past month" filter would
    # select nothing. Shift the whole series forward so recent windows populate.
    posted = pd.to_datetime(df["date_posted"])
    df["date_posted"] = posted + (pd.Timestamp.now() - posted.max())
    return df.reset_index(drop=True)


load_data_module.load_data = load_snapshot

runpy.run_path(str(DASHBOARD_DIR / "app.py"), run_name="__main__")
