import datetime
import json
from unittest.mock import MagicMock

import psycopg2
import pytest

from linkedin_job_search.pipelines import LinkedinJobSearchPipeline, PostgresPipeline


@pytest.fixture
def pipeline(fake_project):
    return LinkedinJobSearchPipeline(country_name="finland")


def raw_item(**overrides):
    item = {
        "title": "Software Engineer",
        "company": "Acme Oy",
        "location": "Helsinki, Uusimaa, Finland",
        "date_posted": "3 days ago",
        "seniority_level": "Mid-Senior level",
        "employment_type": "Full-time",
        "job_function": "Engineering",
        "industries": "IT Services",
        "description": "<p>Build <b>things</b>.</p>",
        "job_url": "https://www.linkedin.com/jobs/view/123",
    }
    item.update(overrides)
    return item


def normalized_item(**overrides):
    """An item as it looks after LinkedinJobSearchPipeline has run,
    which is what PostgresPipeline receives in the real chain."""
    item = raw_item()
    item.update(
        city="Helsinki",
        region="Uusimaa",
        country="Finland",
        job_fields=json.dumps(["Software Development"]),
        date_posted="2026-07-01 00:00:00",
    )
    item.update(overrides)
    return item


class TestNormalizeDate:
    def test_days_ago(self, pipeline):
        result = pipeline.normalize_date("3 days ago")
        expected = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime(
            "%Y-%m-%d"
        )
        assert result.startswith(expected)

    def test_weeks_ago(self, pipeline):
        result = pipeline.normalize_date("2 weeks ago")
        expected = (datetime.datetime.now() - datetime.timedelta(weeks=2)).strftime(
            "%Y-%m-%d"
        )
        assert result.startswith(expected)

    def test_months_ago_does_not_raise(self, pipeline):
        result = pipeline.normalize_date("1 month ago")
        assert isinstance(result, str)

    def test_months_ago_handles_day_overflow(self, pipeline):
        march_31 = datetime.datetime(2026, 3, 31)
        result = pipeline.subtract_months(march_31, 1)
        assert result == datetime.datetime(2026, 2, 28)

    def test_years_ago_does_not_raise(self, pipeline):
        result = pipeline.normalize_date("2 years ago")
        assert isinstance(result, str)

    def test_years_ago_is_24_months_back(self, pipeline):
        now = datetime.datetime(2026, 7, 4)
        assert pipeline.subtract_months(now, 24) == datetime.datetime(2024, 7, 4)

    def test_no_recognized_unit_defaults_to_now(self, pipeline):
        result = pipeline.normalize_date("just now")
        now = datetime.datetime.now()
        parsed = datetime.datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert abs((now - parsed).total_seconds()) < 5


class TestNormalizeDescription:
    def test_strips_html_and_collapses_whitespace(self, pipeline):
        result = pipeline.normalize_description("<p>Build   <b>things</b>.</p>")
        assert result == "Build things ."


class TestNormalizeLocation:
    def test_matches_known_city(self, pipeline):
        # normalize_location receives location text with commas already
        # stripped, as process_item does before calling it.
        city, region, country = pipeline.normalize_location("Helsinki Uusimaa Finland")
        assert (city, region, country) == ("Helsinki", "Uusimaa", "Finland")

    def test_matches_region_only(self, pipeline):
        city, region, country = pipeline.normalize_location("Uusimaa Finland")
        assert region == "Uusimaa"
        assert country == "Finland"

    def test_matches_country_only(self, pipeline):
        city, region, country = pipeline.normalize_location("Finland")
        assert (city, region, country) == ("Unspecified", "Unspecified", "Finland")

    def test_no_match_falls_back_to_unspecified(self, pipeline):
        city, region, country = pipeline.normalize_location("Atlantis")
        assert (city, region, country) == ("Unspecified", "Unspecified", "Unspecified")


class TestNormalizeJobFunction:
    def test_exact_alternative_match(self, pipeline):
        result = json.loads(pipeline.normalize_job_function("Account"))
        assert result == ["Accounting"]

    def test_substring_match(self, pipeline):
        result = json.loads(pipeline.normalize_job_function("Senior Software Engineer"))
        assert result == ["Software Development"]

    def test_no_match_returns_other(self, pipeline):
        result = json.loads(pipeline.normalize_job_function("Astronaut"))
        assert result == ["Other"]


class TestProcessItem:
    def test_full_item_normalization(self, pipeline):
        result = pipeline.process_item(raw_item(), spider=None)
        assert result["title"] == "Software Engineer"
        assert result["city"] == "Helsinki"
        assert result["region"] == "Uusimaa"
        assert result["country"] == "Finland"
        assert json.loads(result["job_fields"]) == ["Software Development"]
        assert result["description"] == "Build things ."

    def test_missing_optional_fields_default_to_unspecified(self, pipeline):
        result = pipeline.process_item(
            raw_item(title=None, company=None, location=None), spider=None
        )
        assert result["title"] == "Unspecified"
        assert result["company"] == "Unspecified"
        assert result["country"] == "Unspecified"


@pytest.fixture
def postgres_pipeline(fake_project):
    return PostgresPipeline()


class TestPostgresPipelineProcessItem:
    def test_skips_insert_when_duplicate_found(self, postgres_pipeline):
        postgres_pipeline.cursor = MagicMock()
        postgres_pipeline.cursor.fetchone.return_value = (1,)
        postgres_pipeline.conn = MagicMock()

        postgres_pipeline.process_item(normalized_item(), spider=None)

        insert_calls = [
            call
            for call in postgres_pipeline.cursor.execute.call_args_list
            if "INSERT INTO jobs" in call.args[0]
        ]
        assert insert_calls == []

    def test_inserts_when_no_duplicate(self, postgres_pipeline):
        postgres_pipeline.cursor = MagicMock()
        postgres_pipeline.cursor.fetchone.return_value = None
        postgres_pipeline.conn = MagicMock()

        postgres_pipeline.process_item(normalized_item(), spider=None)

        insert_calls = [
            call
            for call in postgres_pipeline.cursor.execute.call_args_list
            if "INSERT INTO jobs" in call.args[0]
        ]
        assert len(insert_calls) == 1
        postgres_pipeline.conn.commit.assert_called_once()

    def test_swallows_db_error_on_insert(self, postgres_pipeline):
        postgres_pipeline.cursor = MagicMock()
        postgres_pipeline.cursor.fetchone.return_value = None
        postgres_pipeline.cursor.execute.side_effect = [
            None,
            psycopg2.Error("boom"),
        ]
        postgres_pipeline.conn = MagicMock()

        result = postgres_pipeline.process_item(normalized_item(), spider=None)

        assert result is not None
