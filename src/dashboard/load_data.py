import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

@st.cache_data(ttl=43200)  # Cache data for 12 hours
def load_data_local(db_path):
    """
    Loads data from the local sqlite database.

    Parameters:
    db_path (str): Path of the database, e.g. jobs.db, and filters out bad data.

    Returns:
    pd.DataFrame: A Dataframe containing the date_posted, job_fields, region, country, seniority_level, and company from the job table and filters out rows in which the region and seniority_level is not defined.
    """
    query = """
        SELECT date_posted, job_fields, region, country, seniority_level, company
        FROM jobs
        WHERE seniority_level != 'Not Applicable' AND region != 'Unspecified'
    """
    
    engine = create_engine(f"sqlite:///{db_path}")
    df = pd.read_sql(query, engine)
    return df


@st.cache_data(ttl=43200)  # Cache data for 12 hours
def load_data_cloud():
    """
    Loads data from the postgres database on the cloud.

    This function does not have any parameters. It retrives the database information from .streamlit/secrets.toml.

    Returns:
    pd.DataFrame: A Dataframe containing the date_posted, job_fields, region, country, seniority_level, and company from the job table and filters out rows in which the region and seniority_level is not defined.
    """
    user = st.secrets["postgres"]["user"]
    password = st.secrets["postgres"]["password"]
    dbname = st.secrets["postgres"]["dbname"]
    host = st.secrets["postgres"]["host"]
    port = st.secrets["postgres"]["port"]

    connection_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    engine = create_engine(connection_url)

    query = """
        SELECT date_posted, job_fields, region, country, seniority_level, company
        FROM jobs
        WHERE seniority_level != 'Not Applicable' AND region != 'Unspecified'
    """

    df = pd.read_sql(query, engine)

    return df