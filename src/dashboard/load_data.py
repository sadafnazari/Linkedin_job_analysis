import streamlit as st
import pandas as pd
from sqlalchemy import create_engine


@st.cache_data(ttl=86400)  # Cache data for 24 hours
def load_data(db_adress):
    query = "SELECT date_posted, job_fields, region, country, seniority_level, company FROM jobs WHERE seniority_level != 'Not Applicable' AND region != 'Unspecified'"
    engine = create_engine(db_adress)
    df = pd.read_sql(query, engine)
    return df
