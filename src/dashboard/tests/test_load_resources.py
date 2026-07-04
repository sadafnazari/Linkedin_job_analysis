import json

import pytest

from load_resources import (
    load_countries,
    load_job_fields,
    load_regions,
    load_seniority_levels,
    load_time_periods,
)


@pytest.fixture
def app_dir(tmp_path):
    resources_dir = tmp_path / "resources" / "finland"
    resources_dir.mkdir(parents=True)
    (tmp_path / "resources" / "sweden").mkdir(parents=True)

    (resources_dir / "cities_and_regions_finland.json").write_text(
        json.dumps(
            [
                {"city": "Helsinki", "region_en": "Uusimaa"},
                {"city": "Espoo", "region_en": "Uusimaa"},
                {"city": "Tampere", "region_en": "Pirkanmaa"},
            ]
        )
    )
    (resources_dir / "job_fields_finland.json").write_text(
        json.dumps(
            [
                {"name": "Accounting", "alternatives": ["Account"]},
                {"name": "Consulting", "alternatives": ["Consult"]},
            ]
        )
    )
    (resources_dir / "seniority_levels_finland.json").write_text(
        json.dumps([{"level": "Entry level"}, {"level": "Mid-Senior level"}])
    )
    (resources_dir / "time_periods_finland.json").write_text(
        json.dumps([{"time_period": "Any time"}, {"time_period": "day"}])
    )
    return tmp_path


class TestLoadCountries:
    def test_lists_country_directories(self, app_dir, monkeypatch):
        # load_countries lists app_path/resources but then filters with
        # os.path.isdir(os.path.join("resources", item)) -- a hardcoded
        # relative "resources", not app_path-joined. It only works in
        # production because streamlit is launched from the repo root,
        # so cwd == app_path there. Reproduce that here explicitly.
        monkeypatch.chdir(app_dir)
        countries = load_countries(str(app_dir))
        assert set(countries) == {"finland", "sweden"}

    def test_returns_nothing_when_cwd_differs_from_app_path(self, app_dir):
        countries = load_countries(str(app_dir))
        assert countries == []


class TestLoadRegions:
    def test_returns_sorted_unique_regions(self, app_dir):
        regions = load_regions(str(app_dir), "finland")
        assert regions == ["Pirkanmaa", "Uusimaa"]

    def test_is_case_insensitive_on_country(self, app_dir):
        regions = load_regions(str(app_dir), "Finland")
        assert regions == ["Pirkanmaa", "Uusimaa"]


class TestLoadJobFields:
    def test_returns_sorted_job_field_names(self, app_dir):
        fields = load_job_fields(str(app_dir), "finland")
        assert fields == ["Accounting", "Consulting"]


class TestLoadSeniorityLevels:
    def test_returns_sorted_levels(self, app_dir):
        levels = load_seniority_levels(str(app_dir), "finland")
        assert levels == ["Entry level", "Mid-Senior level"]


class TestLoadTimePeriods:
    def test_returns_time_periods_in_file_order(self, app_dir):
        periods = load_time_periods(str(app_dir), "finland")
        assert periods == ["Any time", "day"]
