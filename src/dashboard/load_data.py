import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

@st.cache_data(ttl=43200)  # Cache data for 12 hours
def load_data_local(db_path):
    query = "SELECT date_posted, job_fields, region, country, seniority_level, company FROM jobs WHERE seniority_level != 'Not Applicable' AND region != 'Unspecified'"
    engine = create_engine(f"sqlite:///{db_path}")
    df = pd.read_sql(query, engine)
    return df


@st.cache_data(ttl=43200)  # Cache data for 12 hours
def load_data_cloud():
    # Get credentials from Streamlit's secrets management
    user = st.secrets["postgres"]["user"]
    password = st.secrets["postgres"]["password"]
    dbname = st.secrets["postgres"]["dbname"]
    host = st.secrets["postgres"]["host"]
    port = st.secrets["postgres"]["port"]

    # Construct the connection URL
    connection_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    # Create a SQLAlchemy engine
    engine = create_engine(connection_url)

    # SQL query to retrieve the data
    query = """
        SELECT date_posted, job_fields, region, country, seniority_level, company
        FROM jobs
        WHERE seniority_level != 'Not Applicable' AND region != 'Unspecified'
    """

    # Execute the query and store the result in a DataFrame
    df = pd.read_sql(query, engine)

    # Return the DataFrame
    return df