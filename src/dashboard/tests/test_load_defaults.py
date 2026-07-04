import json

import pytest

from load_defaults import load_defaults


@pytest.fixture
def app_dir(tmp_path):
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir(parents=True)
    (configs_dir / "streamlit_config.json").write_text(
        json.dumps(
            {
                "countries": [
                    {
                        "name": "Finland",
                        "default_region": "Uusimaa",
                        "default_job_field": "Software Development",
                        "default_seniority_level": "Entry level",
                        "default_time_period": "Any time",
                    }
                ]
            }
        )
    )
    return tmp_path


class TestLoadDefaults:
    def test_returns_defaults_tuple(self, app_dir):
        result = load_defaults(str(app_dir), "finland")
        assert result == ("Uusimaa", "Software Development", "Entry level", "Any time")

    def test_is_case_insensitive_on_country(self, app_dir):
        result = load_defaults(str(app_dir), "FINLAND")
        assert result == ("Uusimaa", "Software Development", "Entry level", "Any time")

    def test_unknown_country_returns_none(self, app_dir):
        result = load_defaults(str(app_dir), "sweden")
        assert result is None
