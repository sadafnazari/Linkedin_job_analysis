# queries.py
"""This module provides functions for different queries that the application requires."""

import pandas as pd

from theme import ALL_FIELDS, ALL_LEVELS, ALL_REGIONS

# The dashboard's time-period options, in the order they appear in the sidebar.
# These are a design decision rather than per-country data, so the label and the
# window it means are kept on one line here instead of in a resource file, where
# the two could drift apart.
PERIOD_OFFSETS = {
    "Past week": pd.DateOffset(weeks=1),
    "Past month": pd.DateOffset(months=1),
    "Past 3 months": pd.DateOffset(months=3),
    "Past 6 months": pd.DateOffset(months=6),
    "Past year": pd.DateOffset(years=1),
}

TREND_MONTHS = 24

# A posting carries a list of job fields, so that column needs exploding before
# it can be counted; every other dimension is one value per row.
_MULTI_VALUE_COLUMN = "job_fields"


def filter_by_period(df, period):
    """
    Filters the DataFrame down to postings inside the selected time period.

    Args:
    df (pandas.DataFrame): Job data with a 'date_posted' column.
    period (str): One of the keys of PERIOD_OFFSETS.

    Returns:
    pandas.DataFrame: Only the postings inside that period.

    Raises:
    KeyError: If the period is not one of the dashboard's options, rather than
              silently returning everything.
    """
    if period not in PERIOD_OFFSETS:
        raise KeyError(
            f"filter_by_period: unknown period {period!r}; "
            f"expected one of {sorted(PERIOD_OFFSETS)}"
        )
    cutoff = pd.Timestamp.now() - PERIOD_OFFSETS[period]
    return df[df["date_posted"] >= cutoff]


def filter_jobs(df, region, job_field, seniority_level):
    """
    Filters by region, job field and seniority level, skipping any set to "All".

    Args:
    df (pandas.DataFrame): Job data with 'region', 'job_fields' and
                           'seniority_level' columns.
    region (str): A region name, or ALL_REGIONS to skip this filter.
    job_field (str): A job field, or ALL_FIELDS to skip this filter.
    seniority_level (str): A seniority level, or ALL_LEVELS to skip this filter.

    Returns:
    pandas.DataFrame: The matching postings.
    """
    filtered_df = df
    if region != ALL_REGIONS:
        filtered_df = filtered_df[filtered_df["region"] == region]
    if job_field != ALL_FIELDS:
        filtered_df = filtered_df[
            filtered_df["job_fields"].apply(lambda fields: job_field in fields)
        ]
    if seniority_level != ALL_LEVELS:
        filtered_df = filtered_df[filtered_df["seniority_level"] == seniority_level]
    return filtered_df


def monthly_counts(df, months=TREND_MONTHS):
    """
    Counts postings per calendar month over the trailing window.

    Args:
    df (pandas.DataFrame): Job data with a 'date_posted' column.
    months (int): How many months back the window reaches.

    The month in progress is dropped. Scraping runs hourly, so that month is
    always a partial count, and leaving it in reads as a collapse in hiring and
    poisons any month-over-month comparison drawn from this series.

    Returns:
    pandas.DataFrame: Columns 'month' (Timestamp, month end) and 'job_count',
                      oldest first, ending with the last complete month. Empty
                      input yields an empty frame.
    """
    if df.empty:
        return pd.DataFrame({"month": [], "job_count": []})

    cutoff = pd.Timestamp.now() - pd.DateOffset(months=months)
    windowed_df = df[df["date_posted"] >= cutoff]
    if windowed_df.empty:
        return pd.DataFrame({"month": [], "job_count": []})

    counts = (
        windowed_df.groupby(pd.Grouper(key="date_posted", freq="ME"))
        .size()
        .reset_index(name="job_count")
        .rename(columns={"date_posted": "month"})
    )
    # Grouper labels each bucket with its month end at midnight, so compare
    # against the start of the current month rather than its end.
    current_month_start = pd.Timestamp.now().to_period("M").start_time
    counts = counts[counts["month"] < current_month_start]
    return counts.sort_values("month").reset_index(drop=True)


def momentum(monthly, sparkline_months=6):
    """
    Measures month-over-month change, with recent months for context.

    The most recent month in the data is compared against the one before it. The
    sparkline carries the trailing months' relative volume so a single noisy
    month is not read as a trend.

    Args:
    monthly (pandas.DataFrame): Output of :func:`monthly_counts`.
    sparkline_months (int): How many trailing months the sparkline covers.

    Returns:
    tuple: (change_percent, sparkline_percents). change_percent is a float, or
           None when there is no previous month to compare against. The
           sparkline is a list of floats from 0 to 100, oldest first.
    """
    if len(monthly) < 2:
        return None, []

    counts = monthly["job_count"].tolist()
    current, previous = counts[-1], counts[-2]
    change_percent = None if previous == 0 else (current - previous) / previous * 100

    recent = counts[-sparkline_months:]
    largest = max(recent) or 1
    return change_percent, [value / largest * 100 for value in recent]


def ranked_counts(df, column, limit=None):
    """
    Counts postings per distinct value of a column, largest first.

    Every ranked bar list on the page is built from this, so they all read the
    same way. The 'job_fields' column is exploded first, since one posting can
    belong to several fields.

    Args:
    df (pandas.DataFrame): Job data.
    column (str): The column to count by, e.g. 'company', 'region',
                  'seniority_level' or 'job_fields'.
    limit (int): Optional cap on the number of rows returned.

    Returns:
    list of dict: Each with 'name' and 'value', ordered by descending value.
    """
    if df.empty:
        return []

    values = df.explode(column)[column] if column == _MULTI_VALUE_COLUMN else df[column]
    counts = values.value_counts()
    if limit is not None:
        counts = counts.head(limit)
    return [{"name": name, "value": int(count)} for name, count in counts.items()]


def top_entity(df, column):
    """
    Finds the most common value of a column and its share of all postings.

    Args:
    df (pandas.DataFrame): Job data.
    column (str): The column to rank, as for :func:`ranked_counts`.

    Returns:
    tuple: (name, share_percent, value). Returns ("None", 0.0, 0) for empty input.
           Because one posting can carry several job fields, shares are taken
           against the number of postings and do not sum to 100.
    """
    ranked = ranked_counts(df, column, limit=1)
    if not ranked:
        return "None", 0.0, 0
    top = ranked[0]
    return top["name"], top["value"] / len(df) * 100, top["value"]


def entity_share(df, column, name):
    """
    Measures one named value's share of all postings.

    Used when the user has already narrowed a dimension, where showing an
    unrelated "top" value next to their own selection would be misleading.

    Args:
    df (pandas.DataFrame): Job data.
    column (str): The column the value belongs to.
    name (str): The value to measure.

    Returns:
    tuple: (share_percent, value).
    """
    if df.empty:
        return 0.0, 0
    values = df.explode(column)[column] if column == _MULTI_VALUE_COLUMN else df[column]
    value = int((values == name).sum())
    return value / len(df) * 100, value


def search_jobs(df, query):
    """
    Filters postings by a case-insensitive match on title or company.

    Args:
    df (pandas.DataFrame): Job data with 'title' and 'company' columns.
    query (str): The search text. Blank returns everything.

    Returns:
    pandas.DataFrame: The matching postings.
    """
    query = (query or "").strip()
    if not query:
        return df
    matches_title = df["title"].str.contains(query, case=False, na=False)
    matches_company = df["company"].str.contains(query, case=False, na=False)
    return df[matches_title | matches_company]


def paginate(df, page, page_size=10):
    """
    Takes one page of rows, clamping the page number into range.

    Args:
    df (pandas.DataFrame): The rows to page through.
    page (int): 1-indexed page number.
    page_size (int): Rows per page.

    Returns:
    tuple: (page_df, page, total_pages). page is the clamped page actually shown,
           so a stale page number from session state cannot produce a blank page.
    """
    total_pages = max(1, -(-len(df) // page_size))
    page = min(max(1, page), total_pages)
    start = (page - 1) * page_size
    return df.iloc[start : start + page_size], page, total_pages
