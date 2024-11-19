# load_data.py

"""
This module provides function(s) for loading data from the database
to Pandas data frame.
"""
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine


@st.cache_data(ttl=43200)  # Cache data for 12 hours
def load_data():
    """
    Loads data from the postgres database on the cloud.

    This function does not have any parameters. It retrives the database
    information from .streamlit/secrets.toml.

    Returns:
    pd.DataFrame: A Dataframe containing the date_posted, job_fields, region,
                  country, seniority_level, and company from the job table and
                    filters out rows in which the region and seniority_level
                    is not defined.
    """
    user = st.secrets["postgres"]["user"]
    password = st.secrets["postgres"]["password"]
    dbname = st.secrets["postgres"]["dbname"]
    host = st.secrets["postgres"]["host"]
    port = st.secrets["postgres"]["port"]

    connection_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    engine = create_engine(connection_url)

    query = """
        SELECT
        date_posted, title, company, region, country, seniority_level, job_fields, job_url
        FROM jobs
        WHERE seniority_level != 'Not Applicable' AND region != 'Unspecified'
    """

    df = pd.read_sql(query, engine)

    return df
