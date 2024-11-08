import pandas as pd


def total_jobs_per_time_frequency(df, selected_time_period):
    if selected_time_period == 'day':
        job_counts = (
            df.groupby(pd.Grouper(key="date_posted", freq="D"))
            .size()
            .reset_index(name="job_count")
        )
    elif selected_time_period == 'week':
        job_counts = (
            df.groupby(pd.Grouper(key="date_posted", freq="W"))
            .size()
            .reset_index(name="job_count")
        )
    elif selected_time_period == 'month':
        job_counts = (
            df.groupby(pd.Grouper(key="date_posted", freq="ME"))
            .size()
            .reset_index(name="job_count")
        )
    elif selected_time_period == 'year' or selected_time_period == 'Any time':
        job_counts = (
            df.groupby(pd.Grouper(key="date_posted", freq="YE"))
            .size()
            .reset_index(name="job_count")
        )

    job_counts.rename(columns={"date_posted": selected_time_period}, inplace=True)
    job_counts = job_counts.sort_values(selected_time_period).reset_index(
        drop=True
    )

    return job_counts


def filter_by_time_period(df, time_period):
    if time_period == "Any time":
        return df
    elif time_period == "year":
        return df[df["date_posted"] >= pd.Timestamp.now() - pd.DateOffset(years=1)]
    elif time_period == "month":
        return df[df["date_posted"] >= pd.Timestamp.now() - pd.DateOffset(months=1)]
    elif time_period == "week":
        return df[df["date_posted"] >= pd.Timestamp.now() - pd.DateOffset(weeks=1)]
    elif time_period == "day":
        return df[df["date_posted"] >= pd.Timestamp.now() - pd.DateOffset(days=1)]


def filter_jobs_by_selectbox(
    df,
    selected_region,
    selected_job_field,
    selected_seniority_level
):
    filtered_df = df[
        (df["region"] == selected_region)
        & (df["job_fields"].apply(lambda x: selected_job_field in x))
        & (df["seniority_level"] == selected_seniority_level)
    ]
    return filtered_df

def separate_for_seniority_levels(df, selected_region, selected_job_field, seniority_levels, selected_time_period):
    count_seniority_levels = []
    for level in seniority_levels:
        df_seniority_level = filter_jobs_by_selectbox(df, selected_region, selected_job_field, level)
        level_count = total_jobs_per_time_frequency(df_seniority_level, selected_time_period)
        count_seniority_levels.append(level_count)
    return count_seniority_levels

def top_10_companies_by_selectbox(filtered_df):
    company_job_counts_field = (
        filtered_df.groupby("company").size().reset_index(name="job_count")
    )
    top_15_companies_selectbox = company_job_counts_field.nlargest(10, "job_count")

    return top_15_companies_selectbox


def top_10_companies_by_job_field_and_time_period(
    df, selected_job_field, selected_time_period
):
    company_job_counts_field = df[
        df["job_fields"].apply(lambda x: selected_job_field in x)
    ][["company", "date_posted"]]

    company_job_counts_field = filter_by_time_period(
        company_job_counts_field, selected_time_period
    )
    company_job_counts_field = (
        company_job_counts_field.groupby("company").size().reset_index(name="job_count")
    )
    top_15_companies_field = company_job_counts_field.nlargest(10, "job_count")

    return top_15_companies_field


def top_10_companies_by_region_and_time_period(
    df, selected_region, selected_time_period
):
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
    top_15_companies_region = company_job_counts_region.nlargest(10, "job_count")

    return top_15_companies_region

def total_jobs_by_region_and_time_period_across_job_fields_and_seniority_levels(
    df, selected_region, selected_time_period, seniority_levels
):
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

