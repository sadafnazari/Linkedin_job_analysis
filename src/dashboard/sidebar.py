# sidebar.py
"""This module provides functions for rendering the sidebar menu."""
import streamlit as st


def sidebar_selectbox_country(countries, default_country_index):
    """
    This function generates a selectbox in the sidebar menu for the user to choose a country.

    Args:
    countries (list): A list of countries as strings to display in the selectbox.
    default_country_index (int): The index of the default country to pre-select in the selectbox.

    Returns:
    str: The selected country in lowercase.
    """
    countries = [country[0].upper() + country[1:] for country in countries]
    st.sidebar.header("Filters")
    selected_country = st.sidebar.selectbox(
        "Select country", options=countries, index=default_country_index
    )
    return selected_country.lower()


def sidebar_selectbox_rest(
    regions,
    job_fields,
    seniority_levels,
    time_periods,
    default_region_index,
    default_job_field_index,
    default_seniority_level_index,
    default_time_period_index,
):
    """
    This function creates a set of selectboxes in the side menu for filtering data by region, job field,
    seniority level, and time period.

    Args:
    - regions (list): A list of available regions to select from.
    - job_fields (list): A list of job fields to select from.
    - seniority_levels (list): A list of seniority levels to select from.
    - time_periods (list): A list of available time periods to select from.
    - default_region_index (int): The default index for the region selectbox.
    - default_job_field_index (int): The default index for the job field selectbox.
    - default_seniority_level_index (int): The default index for the seniority level selectbox.
    - default_time_period_index (int): The default index for the time period selectbox.

    Returns:
    - Tuple: The selected values for region, job field, seniority level, and time period.
    """
    filter_container = st.sidebar.container()
    with filter_container:
        region_col, job_field_col, seniority_level_col, time_period_col = st.columns(4)
        with region_col:
            selected_region = st.sidebar.selectbox(
                "Select region", options=regions, index=default_region_index
            )
        with job_field_col:
            selected_job_field = st.sidebar.selectbox(
                "Select job field", options=job_fields, index=default_job_field_index
            )
        with seniority_level_col:
            selected_seniority_level = st.sidebar.selectbox(
                "Select seniority level",
                options=seniority_levels,
                index=default_seniority_level_index,
            )
        with time_period_col:
            selected_time_period = st.sidebar.selectbox(
                "Select time period",
                options=[
                    "Past " + item if item != "Any time" else item
                    for item in time_periods
                ],
                index=default_time_period_index,
            )
            selected_time_period = (
                selected_time_period[selected_time_period.find(" ") + 1 :]
                if selected_time_period != "Any time"
                else selected_time_period
            )

    return (
        selected_region,
        selected_job_field,
        selected_seniority_level,
        selected_time_period,
    )


def sidebar_put_result(filtered_df):
    """
    This function writes out the total number of jobs for the selected values in the side menu selectboxes

    Args:
    filtered_df (pandas.DataFrame): A DataFrame containing the job data that is filtered based on the selected filters in the side menu selectboxes.

    This function does not return a value. It directly writes the total number of jobs with Streamlit.
    """
    total_jobs_by_selectbox = filtered_df.shape[0]

    st.sidebar.metric("Total jobs for selected critria", total_jobs_by_selectbox)
