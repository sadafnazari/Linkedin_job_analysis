import json


def load_defaults(app_path, country):
    with open(f"{app_path}/configs/streamlit_config.json", "r") as file:
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
