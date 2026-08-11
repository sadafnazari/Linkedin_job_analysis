import pandas as pd
import pytest

import queries as qs
from theme import ALL_FIELDS, ALL_LEVELS, ALL_REGIONS


def jobs_frame(rows):
    """Build a job frame from (days_ago, region, fields, seniority, company) tuples."""
    now = pd.Timestamp.now()
    return pd.DataFrame(
        {
            "date_posted": [now - pd.Timedelta(days=days) for days, *_ in rows],
            "region": [row[1] for row in rows],
            "job_fields": [row[2] for row in rows],
            "seniority_level": [row[3] for row in rows],
            "company": [row[4] for row in rows],
            "title": [f"Role {index}" for index in range(len(rows))],
        }
    )


SAMPLE = jobs_frame(
    [
        (1, "Uusimaa", ["Information Technology", "Research"], "Entry level", "Tieto"),
        (3, "Uusimaa", ["Information Technology"], "Director", "Tieto"),
        (40, "Pirkanmaa", ["Sales"], "Entry level", "Wolt"),
        (200, "Lapland", ["Sales", "Marketing"], "Executive", "Hiab"),
    ]
)


class TestFilterByPeriod:
    def test_keeps_only_postings_inside_the_window(self):
        assert len(qs.filter_by_period(SAMPLE, "Past week")) == 2
        assert len(qs.filter_by_period(SAMPLE, "Past 3 months")) == 3
        assert len(qs.filter_by_period(SAMPLE, "Past year")) == 4

    def test_unknown_period_fails_loudly(self):
        """Silently returning everything would quietly widen the user's filter."""
        with pytest.raises(KeyError):
            qs.filter_by_period(SAMPLE, "Any time")

    def test_every_option_is_ordered_shortest_first(self):
        """The sidebar lists the windows in order, so each must be wider."""
        windows = [len(qs.filter_by_period(SAMPLE, p)) for p in qs.PERIOD_OFFSETS]
        assert windows == sorted(windows)


class TestFilterJobs:
    def test_all_sentinels_skip_their_filter(self):
        result = qs.filter_jobs(SAMPLE, ALL_REGIONS, ALL_FIELDS, ALL_LEVELS)
        assert len(result) == len(SAMPLE)

    def test_job_field_matches_inside_the_list(self):
        result = qs.filter_jobs(SAMPLE, ALL_REGIONS, "Sales", ALL_LEVELS)
        assert len(result) == 2

    def test_filters_combine(self):
        result = qs.filter_jobs(SAMPLE, "Uusimaa", "Information Technology", "Director")
        assert len(result) == 1


class TestRankedCounts:
    def test_orders_by_descending_count(self):
        rows = qs.ranked_counts(SAMPLE, "company")
        assert rows[0] == {"name": "Tieto", "value": 2}
        assert [row["value"] for row in rows] == sorted(
            [row["value"] for row in rows], reverse=True
        )

    def test_multi_value_column_is_exploded(self):
        """A posting belongs to several fields, so each one must be counted."""
        rows = qs.ranked_counts(SAMPLE, "job_fields")
        counts = {row["name"]: row["value"] for row in rows}
        assert counts["Information Technology"] == 2
        assert counts["Sales"] == 2
        assert counts["Marketing"] == 1

    def test_limit_caps_the_rows(self):
        assert len(qs.ranked_counts(SAMPLE, "job_fields", limit=2)) == 2

    def test_empty_frame_yields_no_rows(self):
        assert qs.ranked_counts(SAMPLE.iloc[:0], "company") == []


class TestTopEntityAndShare:
    def test_top_entity_reports_name_share_and_count(self):
        name, share, value = qs.top_entity(SAMPLE, "company")
        assert (name, value) == ("Tieto", 2)
        assert share == pytest.approx(50.0)

    def test_share_is_measured_against_postings_not_field_mentions(self):
        share, value = qs.entity_share(SAMPLE, "job_fields", "Sales")
        assert value == 2
        assert share == pytest.approx(50.0)

    def test_empty_frame_is_reported_rather_than_raising(self):
        assert qs.top_entity(SAMPLE.iloc[:0], "company") == ("None", 0.0, 0)


class TestMonthlyCountsAndMomentum:
    def test_counts_are_grouped_by_month_oldest_first(self):
        monthly = qs.monthly_counts(SAMPLE)
        current_month_start = pd.Timestamp.now().to_period("M").start_time
        complete_months_total = (SAMPLE["date_posted"] < current_month_start).sum()

        assert list(monthly.columns) == ["month", "job_count"]
        assert monthly["month"].is_monotonic_increasing
        assert monthly["job_count"].sum() == complete_months_total

    def test_empty_frame_yields_empty_result(self):
        assert qs.monthly_counts(SAMPLE.iloc[:0]).empty

    def test_month_in_progress_is_excluded(self):
        """Scraping runs hourly, so the current month is always a partial count
        and would read as a collapse in hiring."""
        monthly = qs.monthly_counts(SAMPLE)
        current_month_start = pd.Timestamp.now().to_period("M").start_time
        assert (monthly["month"] < current_month_start).all()

    def test_momentum_compares_the_last_two_months(self):
        monthly = pd.DataFrame({"month": [1, 2, 3], "job_count": [100, 50, 75]})
        change, sparkline = qs.momentum(monthly)
        assert change == pytest.approx(50.0)
        assert sparkline == pytest.approx([100.0, 50.0, 75.0])

    def test_momentum_needs_two_months(self):
        monthly = pd.DataFrame({"month": [1], "job_count": [10]})
        assert qs.momentum(monthly) == (None, [])

    def test_momentum_is_undefined_when_the_previous_month_was_empty(self):
        monthly = pd.DataFrame({"month": [1, 2], "job_count": [0, 10]})
        change, _ = qs.momentum(monthly)
        assert change is None


class TestSearchJobs:
    def test_matches_title_or_company_case_insensitively(self):
        assert len(qs.search_jobs(SAMPLE, "tieto")) == 2
        assert len(qs.search_jobs(SAMPLE, "role 0")) == 1

    def test_blank_query_returns_everything(self):
        assert len(qs.search_jobs(SAMPLE, "  ")) == len(SAMPLE)


class TestPaginate:
    def test_returns_the_requested_page(self):
        page_df, page, total_pages = qs.paginate(SAMPLE, page=2, page_size=2)
        assert (page, total_pages) == (2, 2)
        assert len(page_df) == 2

    def test_out_of_range_page_is_clamped(self):
        """A stale page number in session state must not blank the table."""
        _, page, total_pages = qs.paginate(SAMPLE, page=99, page_size=2)
        assert page == total_pages == 2

    def test_empty_frame_still_has_one_page(self):
        page_df, page, total_pages = qs.paginate(SAMPLE.iloc[:0], page=1)
        assert page_df.empty
        assert (page, total_pages) == (1, 1)
