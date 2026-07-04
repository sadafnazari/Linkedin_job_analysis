from pathlib import Path

import pytest
import scrapy
from scrapy.http import HtmlResponse

from linkedin_job_search.spiders.job_scraper import JobScraperSpider

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name):
    return (FIXTURES_DIR / name).read_text()


def make_response(url, fixture_name, meta=None):
    request = scrapy.Request(url=url, meta=meta or {})
    return HtmlResponse(
        url=url,
        request=request,
        body=load_fixture(fixture_name).encode("utf-8"),
        encoding="utf-8",
    )


@pytest.fixture
def spider(fake_project):
    return JobScraperSpider(country="finland", period="past_2_hours")


class TestInit:
    def test_resolves_geo_id_and_period_code(self, spider):
        assert spider.geo_id == "100456013"
        assert spider.period_code == "r7200"
        assert spider.country_name == "Finland"

    def test_unknown_country_raises(self, fake_project):
        with pytest.raises(ValueError, match="not found in configuration"):
            JobScraperSpider(country="Atlantis", period="past_2_hours")

    def test_unknown_period_raises(self, fake_project):
        with pytest.raises(ValueError, match="not found in configuration"):
            JobScraperSpider(country="finland", period="past_decade")

    def test_missing_country_raises(self, fake_project):
        with pytest.raises(ValueError, match="must be specified"):
            JobScraperSpider(country=None, period="past_2_hours")


class TestParse:
    def test_login_wall_retries_same_url(self, spider):
        url = spider.base_url
        response = make_response(url, "login_wall.html", meta={"url": url})

        results = list(spider.parse(response))

        assert len(results) == 1
        assert results[0].url == url
        assert results[0].callback == spider.parse

    def test_empty_page_on_first_request_retries(self, spider):
        url = spider.base_url
        response = make_response(url, "empty_listing.html", meta={"url": url})

        results = list(spider.parse(response))

        assert len(results) == 1
        assert results[0].url == url

    def test_yields_job_requests_and_pagination(self, spider):
        url = spider.base_url
        response = make_response(url, "job_listing.html", meta={"url": url})

        results = list(spider.parse(response))

        job_requests = [r for r in results if r.callback == spider.parse_job]
        pagination_requests = [r for r in results if r.callback == spider.parse]

        assert len(job_requests) == 2
        assert all("?position" not in r.url for r in job_requests)
        assert job_requests[0].url == "https://www.linkedin.com/jobs/view/111"
        assert job_requests[1].url == "https://www.linkedin.com/jobs/view/222"

        assert len(pagination_requests) == 1
        assert "start=2" in pagination_requests[0].url

    def test_no_more_pages_stops_pagination(self, spider):
        url = spider.base_url
        spider.counter = 5
        spider.counter_job_based_on_scraped = 5
        response = make_response(url, "empty_listing.html", meta={"url": url})

        results = list(spider.parse(response))

        assert results == []


class TestParseJob:
    def test_extracts_all_fields(self, spider):
        job_url = "https://www.linkedin.com/jobs/view/111"
        response = make_response(job_url, "job_detail.html", meta={"job_url": job_url})

        items = list(spider.parse_job(response))

        assert len(items) == 1
        item = items[0]
        assert item["title"] == "Software Engineer"
        assert item["company"] == "Acme Oy"
        assert item["location"] == "Helsinki Uusimaa Finland"
        assert item["date_posted"] == "3 days ago"
        assert item["seniority_level"] == "Mid-Senior level"
        assert item["employment_type"] == "Full-time"
        assert item["job_function"] == "Engineering"
        assert item["industries"] == "IT Services"
        assert "Build" in item["description"]
        assert item["job_url"] == job_url

    def test_missing_title_retries_same_url(self, spider):
        job_url = "https://www.linkedin.com/jobs/view/111"
        response = make_response(
            job_url, "job_detail_missing_title.html", meta={"job_url": job_url}
        )

        results = list(spider.parse_job(response))

        assert len(results) == 1
        assert results[0].url == job_url
        assert results[0].callback == spider.parse_job
