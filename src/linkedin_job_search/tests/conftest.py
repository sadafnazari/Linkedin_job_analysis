import json

import pytest

CITIES_AND_REGIONS = [
    {
        "city": "Helsinki",
        "region_fi": "Uusimaa",
        "region_en": "Uusimaa",
        "country": "Finland",
    },
    {
        "city": "Tampere",
        "region_fi": "Pirkanmaa",
        "region_en": "Pirkanmaa",
        "country": "Finland",
    },
    {
        "city": "Turku",
        "region_fi": "Varsinais Suomi",
        "region_en": "Southwest Finland",
        "country": "Finland",
    },
]

JOB_FIELDS = [
    {"name": "Accounting", "alternatives": ["Account", "Audit"]},
    {
        "name": "Software Development",
        "alternatives": ["Software", "Engineering", "Developer"],
    },
]

SCRAPY_CONFIG = {
    "countries": [
        {"name": "Finland", "geo_id": "100456013"},
        {"name": "Sweden", "geo_id": "105117694"},
    ],
    "periods": {
        "past_2_hours": "r7200",
        "past_24_hours": "r86400",
        "past_week": "r604800",
        "past_month": "r2592000",
        "any_time": "",
    },
    "user_agent": "test-agent",
}

FAKE_ENV = (
    "POSTGRES_USER=test_user\n"
    "POSTGRES_PASSWORD=test_password\n"
    "POSTGRES_HOST=localhost\n"
    "POSTGRES_PORT=5432\n"
    "POSTGRES_DBNAME=test_db\n"
)


@pytest.fixture
def fake_project(tmp_path, monkeypatch):
    """Mirror the real repo layout (scrapy_dir/../../resources, ../../configs)
    and chdir into scrapy_dir, since the pipeline/spider resolve resource and
    config paths relative to cwd.
    """
    scrapy_dir = tmp_path / "src" / "linkedin_job_search"
    resources_dir = tmp_path / "resources" / "finland"
    configs_dir = tmp_path / "configs"
    scrapy_dir.mkdir(parents=True)
    resources_dir.mkdir(parents=True)
    configs_dir.mkdir(parents=True)

    (resources_dir / "cities_and_regions_finland.json").write_text(
        json.dumps(CITIES_AND_REGIONS)
    )
    (resources_dir / "job_fields_finland.json").write_text(json.dumps(JOB_FIELDS))
    (configs_dir / "scrapy_config.json").write_text(json.dumps(SCRAPY_CONFIG))
    (configs_dir / ".env").write_text(FAKE_ENV)

    monkeypatch.chdir(scrapy_dir)
    return tmp_path
