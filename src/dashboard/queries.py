# queries.py
"""This module provides functions for different queries that the application requires."""
import pandas as pd


def total_jobs_per_time_frequency(df, selected_time_period):
    """
    A query to calculate the total number of jobs posted, grouped by the specified time period (day, week, month, or year).

    Args:
    df (pandas.DataFrame): The DataFrame containing job data, including the `date_posted` column.
    selected_time_period (str): The time period to group the data by. It can be one of the following:
        - "day": Groups data by day.
        - "week": Groups data by week.
        - "month": Groups data by month.
        - "year" or "Any time": Groups data by year.

    Returns:
    pandas.DataFrame: A DataFrame containing the aggregated job count for each selected time period.
                        The resulting DataFrame has columns:
                        - `selected_time_period`: The time period (e.g., day, week, month, year).
                        - `job_count`: The number of jobs posted in that time period.
    """
    if selected_time_period == "day":
        job_counts = (
            df.groupby(pd.Grouper(key="date_posted", freq="D"))
            .size()
            .reset_index(name="job_count")
        )
    elif selected_time_period == "week":
        job_counts = (
            df.groupby(pd.Grouper(key="date_posted", freq="W"))
            .size()
            .reset_index(name="job_count")
        )
    elif selected_time_period == "month":
        job_counts = (
            df.groupby(pd.Grouper(key="date_posted", freq="ME"))
            .size()
            .reset_index(name="job_count")
        )
    elif selected_time_period == "year" or selected_time_period == "Any time":
        job_counts = (
            df.groupby(pd.Grouper(key="date_posted", freq="YE"))
            .size()
            .reset_index(name="job_count")
        )

    job_counts.rename(columns={"date_posted": selected_time_period}, inplace=True)
    job_counts = job_counts.sort_values(selected_time_period).reset_index(drop=True)

    return job_counts


def filter_by_time_period(df, time_period, quantity=1):
    """
    A query to filter the DataFrame based on the selected time period, returning only rows where the 'date_posted'
    is within the specified period.

    Args:
    df (pandas.DataFrame): The DataFrame containing job data with a 'date_posted' column.
    time_period (str): The time period to filter the data by. It can be one of the following:
        - "Any time": No filtering, returns all data.
        - "year": Filters for jobs posted in the past year.
        - "month": Filters for jobs posted in the past month.
        - "week": Filters for jobs posted in the past week.
        - "day": Filters for jobs posted in the past day.

    Returns:
    pandas.DataFrame: A DataFrame filtered to include only jobs posted within the selected time period.
    """
    if time_period == "Any time":
        return df
    elif time_period == "year":
        return df[
            df["date_posted"] >= pd.Timestamp.now() - pd.DateOffset(years=quantity)
        ]
    elif time_period == "month":
        return df[
            df["date_posted"] >= pd.Timestamp.now() - pd.DateOffset(months=quantity)
        ]
    elif time_period == "week":
        return df[
            df["date_posted"] >= pd.Timestamp.now() - pd.DateOffset(weeks=quantity)
        ]
    elif time_period == "day":
        return df[
            df["date_posted"] >= pd.Timestamp.now() - pd.DateOffset(days=quantity)
        ]


def filter_jobs_by_selectbox(
    df, selected_region, selected_job_field, selected_seniority_level
):
    """
    A query to filter the DataFrame based on selected filters from the selectbox: region, job field, and seniority level.

    Args:
    df (pandas.DataFrame): The DataFrame containing job data with 'region', 'job_fields', and 'seniority_level' columns.
    selected_region (str): The region to filter the jobs by.
    selected_job_field (str): The job field to filter the jobs by.
    selected_seniority_level (str): The seniority level to filter the jobs by.

    Returns:
    pandas.DataFrame: A filtered DataFrame containing only jobs that match the selected region, job field, and seniority level.
    """
    filtered_df = df[
        (df["region"] == selected_region)
        & (df["job_fields"].apply(lambda x: selected_job_field in x))
        & (df["seniority_level"] == selected_seniority_level)
    ]
    return filtered_df


def separate_for_seniority_levels(
    df, selected_region, selected_job_field, seniority_levels, selected_time_period
):
    """
    A query to separate job counts by seniority level for a selected region, job field, and time period.

    Args:
    df (pandas.DataFrame): The DataFrame containing job data.
    selected_region (str): The region to filter the jobs by.
    selected_job_field (str): The job field to filter the jobs by.
    seniority_levels (list): A list of seniority levels to analyze.
    selected_time_period (str): The time period for aggregating job counts (e.g., "day", "week", "month", "year").

    Returns:
    list: A list of DataFrames, where each DataFrame contains job counts for a specific seniority level.
    """
    count_seniority_levels = []
    for level in seniority_levels:
        df_seniority_level = filter_jobs_by_selectbox(
            df, selected_region, selected_job_field, level
        )
        level_count = total_jobs_per_time_frequency(
            df_seniority_level, selected_time_period
        )
        count_seniority_levels.append(level_count)
    return count_seniority_levels


def top_10_companies_by_selectbox(filtered_df):
    """
    A query to compute the top 10 companies with the most job postings based on selected filters from the selectbox.

    Args:
    filtered_df (pandas.DataFrame): A DataFrame containing job data, including a 'company' column.

    Returns:
    pandas.DataFrame: A DataFrame containing the top 10 companies with the highest job counts.
    """
    company_job_counts_field = (
        filtered_df.groupby("company").size().reset_index(name="job_count")
    )
    top_10_companies_selectbox = company_job_counts_field.nlargest(10, "job_count")

    return top_10_companies_selectbox


def top_10_companies_by_job_field_and_time_period(
    df, selected_job_field, selected_time_period
):
    """
    A query to retrieve the top 10 companies posting jobs in the selected job field
    within a specified time period. This function then filters the DataFrame by the job field and time period,
    groups by company, and counts the number of job postings per company.

    Args:
    df (pandas.DataFrame): The DataFrame containing job data, including 'company', 'job_fields',
                            and 'date_posted' columns.
    selected_job_field (str): The job field to filter the data by.
    selected_time_period (str): The time period for filtering job postings (e.g., "year", "month").

    Returns:
    pandas.DataFrame: A DataFrame containing the top 10 companies with the most job postings
                       in the selected job field and time period.
    """
    company_job_counts_field = df[
        df["job_fields"].apply(lambda x: selected_job_field in x)
    ][["company", "date_posted"]]

    company_job_counts_field = filter_by_time_period(
        company_job_counts_field, selected_time_period
    )
    company_job_counts_field = (
        company_job_counts_field.groupby("company").size().reset_index(name="job_count")
    )
    top_10_companies_field = company_job_counts_field.nlargest(10, "job_count")

    return top_10_companies_field


def top_10_companies_by_region_and_time_period(
    df, selected_region, selected_time_period
):
    """
    A query to retrieve the top 10 companies posting jobs in the selected region
    within a specified time period. The function then filters the DataFrame by region and time period,
    groups by company, and counts the number of job postings per company.

    Args:
    df (pandas.DataFrame): The DataFrame containing job data, including 'company', 'region',
                            and 'date_posted' columns.
    selected_region (str): The region to filter the data by.
    selected_time_period (str): The time period for filtering job postings (e.g., "year", "month").

    Returns:
    pandas.DataFrame: A DataFrame containing the top 10 companies with the most job postings
                       in the selected region and time period.
    """
    company_job_counts_region = df[df["region"] == selected_region][
        ["company", "date_posted"]
    ]

    company_job_counts_region = filter_by_time_period(
        company_job_counts_region, selected_time_period
    )
    company_job_counts_region = (
        company_job_counts_region.groupby("company")
        .size()
        .reset_index(name="job_count")
    )
    top_10_companies_region = company_job_counts_region.nlargest(10, "job_count")

    return top_10_companies_region


def total_jobs_by_region_and_time_period_across_job_fields_and_seniority_levels(
    df, selected_region, selected_time_period, seniority_levels
):
    """
    A query to calculate the total number of jobs for a selected region and time period across all job fields and seniority levels.
    The function then returns the job counts by field, seniority level, and the sorted list of job fields based on total job count.

    Args:
    df (pandas.DataFrame): The DataFrame containing job data with columns such as
                            'region', 'job_fields', 'seniority_level', and 'date_posted'.
    selected_region (str): The region to filter the data by.
    selected_time_period (str): The time period to filter the job postings (e.g., "year", "month").
    seniority_levels (list): The list of seniority levels for ordering the data.

    Returns:
    pandas.DataFrame: A DataFrame with job counts for each job field and seniority level in the selected region
                       and time period.
    list: A sorted list of job fields based on the total number of job postings.
    """
    region_job_counts = df[(df["region"] == selected_region)][
        ["job_fields", "seniority_level", "date_posted"]
    ]

    region_job_counts = filter_by_time_period(region_job_counts, selected_time_period)

    job_counts_by_field = region_job_counts.explode("job_fields")
    job_counts_by_field = (
        job_counts_by_field.groupby(["job_fields", "seniority_level"])
        .size()
        .reset_index(name="count")
    )

    total_job_counts_by_field = (
        job_counts_by_field.groupby("job_fields")["count"]
        .sum()
        .reset_index(name="total_count")
    )
    sorted_job_fields = total_job_counts_by_field.sort_values(
        by="total_count", ascending=False
    )["job_fields"]

    job_counts_by_field["job_fields"] = pd.Categorical(
        job_counts_by_field["job_fields"], categories=sorted_job_fields, ordered=True
    )
    job_counts_by_field["seniority_level"] = pd.Categorical(
        job_counts_by_field["seniority_level"],
        categories=seniority_levels,
        ordered=True,
    )

    return job_counts_by_field, sorted_job_fields


def total_jobs_by_job_field_and_time_period_across_regions_and_seniority_levels(
    df, selected_job_field, selected_time_period, seniority_levels
):
    """
    A query to calculate the total number of jobs for a given job field and time period across all regions and seniority levels.
    The function then returns the job counts by region and seniority level along with the sorted list of regions based on total job count.

    Args:
    df (pandas.DataFrame): The DataFrame containing job data with columns such as
                            'region', 'job_fields', 'seniority_level', and 'date_posted'.
    selected_job_field (str): The job field to filter the data by.
    selected_time_period (str): The time period to filter the job postings (e.g., "year", "month").
    seniority_levels (list): The list of seniority levels for ordering the data.

    Returns:
    pandas.DataFrame: A DataFrame with job counts for each region and seniority level in the selected
                       job field and time period.
    list: A sorted list of regions based on the total number of job postings.
    """
    field_job_counts = df[(df["job_fields"].apply(lambda x: selected_job_field in x))][
        ["region", "seniority_level", "date_posted"]
    ]

    field_job_counts = filter_by_time_period(field_job_counts, selected_time_period)
    job_counts_by_region = (
        field_job_counts.groupby(["region", "seniority_level"])
        .size()
        .reset_index(name="count")
    )
    total_job_counts_by_region = (
        job_counts_by_region.groupby("region")["count"]
        .sum()
        .reset_index(name="total_count")
    )
    sorted_regions = total_job_counts_by_region.sort_values(
        by="total_count", ascending=False
    )["region"]

    job_counts_by_region["region"] = pd.Categorical(
        job_counts_by_region["region"], categories=sorted_regions, ordered=True
    )
    job_counts_by_region["seniority_level"] = pd.Categorical(
        job_counts_by_region["seniority_level"],
        categories=seniority_levels,
        ordered=True,
    )

    return job_counts_by_region, sorted_regions
