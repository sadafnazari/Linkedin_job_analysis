import streamlit as st


def sidebar_selectbox_country(countries, default_country_index):
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
    total_jobs_by_selectbox = filtered_df.shape[0]

    st.sidebar.metric("Total jobs for selected critria", total_jobs_by_selectbox)
