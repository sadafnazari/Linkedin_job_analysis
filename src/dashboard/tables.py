# tables.py
"""This module provides function(s) for showing latest job posts on demand."""
import pandas as pd
import streamlit as st


def create_df_latest_jobs(df, selected_job_field):
    """
    This function creates a table of the latest jobs.

    Args:
    df (pandas.DataFrame): The DataFrame containing job data.
    selected_job_field (str): The job field to filter the jobs by.

    This function does not return a value. It directly creates the data frame
      of the latest jobs with Streamlit.
    """
    filtered_df = df[
        [
            "date_posted",
            "title",
            "company",
            "region",
            "seniority_level",
            "job_fields",
            "job_url",
        ]
    ]
    filtered_df = filtered_df.sort_values(by="date_posted", ascending=False)
    filtered_df["job_fields"] = selected_job_field
    st.markdown(
        """
    <p style='text-align: center;'>
        <b>Latest job posts based on the selected filters</b>
    </p>
    """,
        unsafe_allow_html=True,
    )
    st.data_editor(
        filtered_df,
        column_config={
            "date_posted": st.column_config.DateColumn(
                "Date posted", format="DD.MM.YYYY"
            ),
            "title": st.column_config.TextColumn("Title"),
            "company": st.column_config.TextColumn("Company"),
            "region": st.column_config.TextColumn("Region"),
            "seniority_level": st.column_config.TextColumn("Seniority level"),
            "job_fields": st.column_config.ListColumn("Job field"),
            "job_url": st.column_config.LinkColumn("Job url", display_text="View job"),
        },
        disabled=True,
        hide_index=True,
        use_container_width=True,
    )
