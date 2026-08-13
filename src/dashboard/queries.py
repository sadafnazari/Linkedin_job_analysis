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

# How many slices of the selected period a sparkline is drawn from.
SPARKLINE_BUCKETS = 6

# Below this share of the largest segment's volume, a month-over-month percentage
# swings on a handful of postings and is not worth reading as a trend.
LOW_VOLUME_SHARE = 0.15

# A posting carries a list of job fields, so that column needs exploding before
# it can be counted; every other dimension is one value per row.
_MULTI_VALUE_COLUMN = "job_fields"

OTHER_STACK_LABEL = "Other fields"


def _explode_multi_value(df, column):
    """Gives one row per value where a column holds a list, otherwise passes through."""
    return df.explode(column) if column == _MULTI_VALUE_COLUMN else df


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
    pivot = monthly_pivot(df, None, months)
    if pivot.empty:
        return pd.DataFrame({"month": [], "job_count": []})
    return (
        pivot.sum(axis=1)
        .reset_index(name="job_count")
        .rename(columns={"date_posted": "month"})
    )


def monthly_pivot(df, column, months=TREND_MONTHS):
    """
    Counts postings per calendar month, split by a column's values.

    This is the one place the monthly window is built, so the trend, the
    sparklines and the per-segment momentum all read the same months. As in
    :func:`monthly_counts`, the month in progress is dropped: scraping runs
    hourly, so it is always a partial count.

    Args:
    df (pandas.DataFrame): Job data with a 'date_posted' column.
    column (str): The column to split by, or None to count every posting into a
                  single unnamed column.
    months (int): How many months back the window reaches.

    Returns:
    pandas.DataFrame: Indexed by month end (oldest first), one column per value
                      of the split column, zero-filled. Empty input, or a window
                      holding only the month in progress, yields an empty frame.
    """
    if df.empty:
        return pd.DataFrame()

    cutoff = pd.Timestamp.now() - pd.DateOffset(months=months)
    windowed_df = df[df["date_posted"] >= cutoff]
    if column is not None:
        windowed_df = _explode_multi_value(windowed_df, column).dropna(subset=[column])
    if windowed_df.empty:
        return pd.DataFrame()

    month_buckets = pd.Grouper(key="date_posted", freq="ME")
    group_by = [month_buckets] if column is None else [month_buckets, column]
    counts = windowed_df.groupby(group_by).size()
    counts = counts.to_frame("job_count") if column is None else counts.unstack()
    counts = counts.fillna(0).astype(int)

    # Grouper labels each bucket with its month end at midnight, so compare
    # against the start of the current month rather than its end.
    current_month_start = pd.Timestamp.now().to_period("M").start_time
    return counts[counts.index < current_month_start].sort_index()


def monthly_counts_by(df, column, order, months=TREND_MONTHS):
    """
    Counts postings per calendar month for each named value of a column.

    Feeds the stacked trend chart, which needs its bands in a fixed order and
    present even in months where a band has no postings — a band that appears and
    disappears between months would read as a gap in the data.

    Args:
    df (pandas.DataFrame): Job data with a 'date_posted' column.
    column (str): The column to split by, e.g. 'seniority_level'.
    order (sequence of str): The values to return, in stacking order.
    months (int): How many months back the window reaches.

    Returns:
    pandas.DataFrame: Column 'month' followed by one column per value in order,
                      oldest month first. Empty input yields an empty frame.
    """
    pivot = monthly_pivot(df, column, months)
    if pivot.empty:
        return pd.DataFrame()
    pivot = pivot.reindex(columns=list(order), fill_value=0).fillna(0).astype(int)
    return pivot.reset_index().rename(columns={"date_posted": "month"})


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

    counts = _explode_multi_value(df, column)[column].value_counts()
    if limit is not None:
        counts = counts.head(limit)
    return [{"name": name, "value": int(count)} for name, count in counts.items()]


def stack_order(df, column, limit=None):
    """
    Returns a column's values in descending order of postings, largest first.

    Args:
    df (pandas.DataFrame): Job data.
    column (str): The column to rank, as for :func:`ranked_counts`.
    limit (int): Optional cap on how many values are returned.

    Returns:
    list of str: The value names.
    """
    return [row["name"] for row in ranked_counts(df, column, limit)]


def stacked_counts(df, dimension, stack_by, stacks, limit=None):
    """
    Counts postings per value of one column, broken into bands of another.

    The bar's length is the number of postings in that row, and the bands divide
    it by composition. The two are measured separately on purpose: a posting
    carries several job fields, so counting the bands would total more than the
    postings the row actually represents.

    Args:
    df (pandas.DataFrame): Job data.
    dimension (str): The column the rows are, e.g. 'job_fields' or 'region'.
    stack_by (str): The column the bands are, e.g. 'seniority_level'.
    stacks (sequence of str): The bands to report, in stacking order. Values
                              outside this list are gathered into
                              OTHER_STACK_LABEL, which is appended when non-empty.
    limit (int): Optional cap on the number of rows returned.

    Returns:
    list of dict: Each with 'name', 'value' and 'segments' — itself a list of
                  {'name', 'value'} in the given band order, rows largest first.
    """
    rows = ranked_counts(df, dimension, limit)
    if not rows:
        return []

    exploded = _explode_multi_value(df, dimension)
    exploded = _explode_multi_value(exploded, stack_by)
    composition = (
        exploded.dropna(subset=[dimension, stack_by])
        .groupby([dimension, stack_by])
        .size()
        .unstack(fill_value=0)
    )

    named_stacks = [stack for stack in stacks if stack in composition.columns]
    other_columns = [
        column for column in composition.columns if column not in set(stacks)
    ]
    band_counts = composition[named_stacks].copy()
    if other_columns:
        band_counts[OTHER_STACK_LABEL] = composition[other_columns].sum(axis=1)

    for row in rows:
        counts = (
            band_counts.loc[row["name"]] if row["name"] in band_counts.index else {}
        )
        row["segments"] = [
            {"name": band, "value": int(counts.get(band, 0))}
            for band in band_counts.columns
        ]
    return rows


def period_series(df, dimension, names, period, buckets=SPARKLINE_BUCKETS):
    """
    Builds each named value's shape across the selected period, for its sparkline.

    The window is cut into equal slices of the period the panel is already
    showing, rather than a fixed run of months: a sparkline covering six months
    beside a panel labelled "Past month" describes a different set of postings
    from the bar it sits next to.

    Each series is scaled against its own peak, because the sparkline sits beside
    a bar that already carries the volume — its job is only to say whether the
    row is rising or falling inside that window.

    Args:
    df (pandas.DataFrame): Postings inside the selected period.
    dimension (str): The column the names belong to.
    names (sequence of str): The values to build a series for.
    period (str): One of the keys of PERIOD_OFFSETS, which sets the window.
    buckets (int): How many slices the window is cut into.

    Returns:
    dict: name -> list of floats from 0 to 100, oldest slice first. A value with
          no postings in the window maps to an empty list.

    Raises:
    KeyError: If the period is not one of the dashboard's options.
    """
    if period not in PERIOD_OFFSETS:
        raise KeyError(
            f"period_series: unknown period {period!r}; "
            f"expected one of {sorted(PERIOD_OFFSETS)}"
        )
    if df.empty:
        return dict.fromkeys(names, [])

    now = pd.Timestamp.now()
    edges = pd.date_range(now - PERIOD_OFFSETS[period], now, periods=buckets + 1)
    exploded = _explode_multi_value(df, dimension)
    slices = pd.cut(exploded["date_posted"], bins=edges, include_lowest=True)
    counts = exploded.groupby([slices, exploded[dimension]], observed=False).size()
    counts = counts.unstack(fill_value=0)

    series = {}
    for name in names:
        values = list(counts[name]) if name in counts.columns else []
        largest = max(values) if values else 0
        series[name] = [value / largest * 100 for value in values] if largest else []
    return series


def segment_momentum(df, column, months=TREND_MONTHS):
    """
    Measures each segment's month-over-month change, largest segment first.

    Args:
    df (pandas.DataFrame): Job data ignoring the time period, since the two
                           months compared are chosen here.
    column (str): The column whose values are the segments, e.g. 'region'.
    months (int): How many months back the window reaches.

    Returns:
    list of dict: Each with 'name', 'postings' (the last complete month's count),
                  'change_percent' (float, or None when the previous month held no
                  postings) and 'is_low_volume' — True when the segment is too
                  small for its percentage to be worth reading. Segments with no
                  postings in the last complete month are dropped. Returns an
                  empty list when there are not two complete months to compare.
    """
    pivot = monthly_pivot(df, column, months)
    if len(pivot) < 2:
        return []

    current, previous = pivot.iloc[-1], pivot.iloc[-2]
    segments = []
    for name in current[current > 0].sort_values(ascending=False).index:
        previous_count = int(previous.get(name, 0))
        segments.append(
            {
                "name": name,
                "postings": int(current[name]),
                "change_percent": (
                    None
                    if previous_count == 0
                    else (int(current[name]) - previous_count) / previous_count * 100
                ),
            }
        )

    low_volume_cutoff = segments[0]["postings"] * LOW_VOLUME_SHARE
    for segment in segments:
        segment["is_low_volume"] = segment["postings"] < low_volume_cutoff
    return segments


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
    value = int((_explode_multi_value(df, column)[column] == name).sum())
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
