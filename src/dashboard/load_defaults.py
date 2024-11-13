# load_defaults.py
"""This module provides functions for loading the default values for the
filters in the selectboxes in the side menu."""
import json


def load_defaults(app_path, country):
    """Loads the default values for the selected country to be shown in the
       sidebar menu's selectboxes.

    Args:
    app_path (str): The base path to the application directory.
    country (str): Selected country from the first selectbox
                   in the sidebar menu.

    Returns:
    tuple: A tuple containing the following elements:
        - default_region (str): The default region value.
        - default_job_field (str): The default job_field value.
        - default_seniority_level (str): The default seniority_level.
        - default_time_period (str): The default time_period value.
    """
    with open(f"{app_path}/configs/streamlit_config.json") as file:
        defulats_data = json.load(file)
    countries = defulats_data["countries"]
    for item in countries:
        if item["name"].lower() == country.lower():
            return (
                item["default_region"],
                item["default_job_field"],
                item["default_seniority_level"],
                item["default_time_period"],
            )
