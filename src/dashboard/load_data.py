import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import os

@st.cache_data(ttl=86400)  # Cache data for 24 hours
def load_data_local(db_path):
    query = "SELECT date_posted, job_fields, region, country, seniority_level, company FROM jobs WHERE seniority_level != 'Not Applicable' AND region != 'Unspecified'"
    engine = create_engine(f"sqlite:///{db_path}" )
    df = pd.read_sql(query, engine)
    return df

@st.cache_data(ttl=86400) # Cache data for 24 hours
def load_data_cloud(db_path):
    FILE_ID = '1hX4mGdPYXruU_No_rf0c6Vubx3Jp2Kst'
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["google_api"]
    )
    drive_service = build('drive', 'v3', credentials=credentials)
    request = drive_service.files().get_media(fileId=FILE_ID)

    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download progress: {int(status.progress() * 100)}%")

    file_data.seek(0)
    with open(db_path, 'wb') as f:
        f.write(file_data.read())

    engine = create_engine(f"sqlite:///{db_path}" )
    with engine.connect() as connection:
        query = "SELECT date_posted, job_fields, region, country, seniority_level, company FROM jobs WHERE seniority_level != 'Not Applicable' AND region != 'Unspecified'"
        df = pd.read_sql(query, connection)
    return df