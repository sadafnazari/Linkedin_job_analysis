import pandas as pd


def pre_processing(df, selected_country):
    df["job_fields"] = df["job_fields"].apply(
        lambda x: eval(x) if isinstance(x, str) else x
    )
    df["date_posted"] = pd.to_datetime(df["date_posted"])

    df = df[
        (df["country"] == selected_country)
    ]
    return df
