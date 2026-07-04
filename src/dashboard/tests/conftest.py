import pandas as pd
import pytest


@pytest.fixture
def sample_jobs_df():
    """A small hand-built DataFrame shaped like the post-pre_processing
    data queries.py operates on: job_fields already parsed into lists,
    date_posted already a real Timestamp.
    """
    now = pd.Timestamp.now()
    data = [
        {
            "date_posted": now - pd.Timedelta(hours=1),
            "company": "Acme Oy",
            "region": "Uusimaa",
            "job_fields": ["Software Development"],
            "seniority_level": "Entry level",
        },
        {
            "date_posted": now - pd.Timedelta(days=2),
            "company": "Acme Oy",
            "region": "Uusimaa",
            "job_fields": ["Software Development", "Consulting"],
            "seniority_level": "Mid-Senior level",
        },
        {
            "date_posted": now - pd.Timedelta(days=10),
            "company": "Beta Ltd",
            "region": "Uusimaa",
            "job_fields": ["Accounting"],
            "seniority_level": "Entry level",
        },
        {
            "date_posted": now - pd.Timedelta(days=40),
            "company": "Gamma Inc",
            "region": "Pirkanmaa",
            "job_fields": ["Software Development"],
            "seniority_level": "Mid-Senior level",
        },
        {
            "date_posted": now - pd.Timedelta(days=400),
            "company": "Delta Oy",
            "region": "Pirkanmaa",
            "job_fields": ["Accounting"],
            "seniority_level": "Entry level",
        },
    ]
    return pd.DataFrame(data)
