import json
import os


def load_countries():
    items = os.listdir('resources')
    countries = [item for item in items if os.path.isdir(os.path.join('resources', item))]
    return countries


def load_regions(country):
    with open(
        f"resources/{country.lower()}/cities_and_regions_{country.lower()}.json", "r"
    ) as file:
        regions_data = json.load(file)
    regions = sorted(set([item["region_en"] for item in regions_data]))
    return regions


def load_job_fields(country):
    with open(
        f"resources/{country.lower()}/job_fields_{country.lower()}.json", "r"
    ) as file:
        job_fields_data = json.load(file)
    job_fields = sorted(set([item["name"] for item in job_fields_data]))
    return job_fields


def load_seniority_levels(country):
    with open(
        f"resources/{country.lower()}/seniority_levels_{country.lower()}.json", "r"
    ) as file:
        seniority_levels_data = json.load(file)
        seniority_levels = sorted(
            set([item["level"] for item in seniority_levels_data])
        )
    return seniority_levels


def load_time_periods(country):
    with open(
        f"resources/{country.lower()}/time_periods_{country.lower()}.json", "r"
    ) as file:
        time_periods_data = json.load(file)
        time_periods = [item["time_period"] for item in time_periods_data]
    return time_periods
