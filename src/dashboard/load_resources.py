import json
import os


def load_countries(app_path):
    """
    Loads the the list of countries that sufficient resources are defined for them.
    
    This function lists all the items in the 'resources' folder and returns a list of
    directory names that represent countries. Only directories (not files) are included in the list.

    Parameters:
    app_path (str): The base path to the application directory.

    Returns:
    list: A list of strings representing the directory names in the 'resources' folder.
          Each string corresponds to a country directory.
    """
    items = os.listdir(f"{app_path}/resources")
    countries = [
        item for item in items if os.path.isdir(os.path.join("resources", item))
    ]
    return countries


def load_regions(app_path, country):
    """
    Loads and returns a sorted list of regions for the specified country.

    This function reads a JSON file containing region data for a specific country,
    extracts the 'region_en' values, and returns a sorted list of unique region names.

    Parameters:
    app_path (str): The base path to the application directory.
    country (str): The name of the country for which regions are to be loaded.

    Returns:
    list: A sorted list of strings, each representing a region name in English
          for the specified country.
    """
    with open(
        f"{app_path}/resources/{country.lower()}/cities_and_regions_{country.lower()}.json",
        "r",
    ) as file:
        regions_data = json.load(file)
    regions = sorted(set([item["region_en"] for item in regions_data]))
    return regions


def load_job_fields(app_path, country):
    """
    Loads and returns a sorted list of job fields for the specified country.

    This function reads a JSON file containing job field data for a specific country,
    extracts the 'name' values, and returns a sorted list of unique job field names.

    Parameters:
    app_path (str): The base path to the application directory.
    country (str): The name of the country for which job fields are to be loaded.

    Returns:
    list: A sorted list of strings, each representing a job field name for the specified country.
    """
    with open(
        f"{app_path}/resources/{country.lower()}/job_fields_{country.lower()}.json", "r"
    ) as file:
        job_fields_data = json.load(file)
    job_fields = sorted(set([item["name"] for item in job_fields_data]))
    return job_fields


def load_seniority_levels(app_path, country):
    """
    Loads and returns a sorted list of seniority levels for the specified country.

    This function reads a JSON file containing seniority level data for a specific country,
    extracts the 'level' values, and returns a sorted list of unique seniority level names.

    Parameters:
    app_path (str): The base path to the application directory.
    country (str): The name of the country for which seniority levels are to be loaded.

    Returns:
    list: A sorted list of strings, each representing a seniority level for the specified country.
    """
    with open(
        f"{app_path}/resources/{country.lower()}/seniority_levels_{country.lower()}.json",
        "r",
    ) as file:
        seniority_levels_data = json.load(file)
        seniority_levels = sorted(
            set([item["level"] for item in seniority_levels_data])
        )
    return seniority_levels


def load_time_periods(app_path, country):
    """
    Loads and returns a list of time periods for the specified country.

    This function reads a JSON file containing time period data for a specific country,
    extracts the 'time_period' values, and returns a list of time periods.

    Parameters:
    app_path (str): The base path to the application directory.
    country (str): The name of the country for which time periods are to be loaded.

    Returns:
    list: A list of strings, each representing a time period for the specified country.
    """
    with open(
        f"{app_path}/resources/{country.lower()}/time_periods_{country.lower()}.json",
        "r",
    ) as file:
        time_periods_data = json.load(file)
        time_periods = [item["time_period"] for item in time_periods_data]
    return time_periods
