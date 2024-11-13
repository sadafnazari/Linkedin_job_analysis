# pre_processing.py
"""
This module provides function(s) for pre processing data before retriving
information from it.
"""
import pandas as pd


def pre_processing(df, selected_country):
    """
    Pre-processes the data DataFrame by cleaning and filtering based on the selected country.

    Args:
    df (pandas.DataFrame): A DataFrame containing job data, including columns such as 'job_fields', 'date_posted', 'country', and 'region'.
    selected_country (str): The country to filter.

    Returns:
    pandas.DataFrame: A filtered and cleaned DataFrame.
    """
    df["job_fields"] = df["job_fields"].apply(
        lambda x: eval(x) if isinstance(x, str) else x
    )
    df["date_posted"] = pd.to_datetime(df["date_posted"])

    df = df[
        (df["country"].str.lower() == selected_country)
        & (df["region"] != "Unspecified")
    ]
    return df
