import pandas as pd

from queries import (
    filter_by_time_period,
    filter_jobs_by_selectbox,
    top_10_companies_by_job_field_and_time_period,
    top_10_companies_by_region_and_time_period,
    top_10_companies_by_selectbox,
    total_jobs_by_job_field_and_time_period_across_regions_and_seniority_levels,
    total_jobs_by_region_and_time_period_across_job_fields_and_seniority_levels,
    total_jobs_per_time_frequency,
)

SENIORITY_LEVELS = ["Entry level", "Mid-Senior level"]


class TestTotalJobsPerTimeFrequency:
    def test_groups_by_day(self, sample_jobs_df):
        result = total_jobs_per_time_frequency(sample_jobs_df, "day")
        assert "day" in result.columns
        assert "job_count" in result.columns
        assert result["job_count"].sum() == len(sample_jobs_df)

    def test_groups_by_year(self, sample_jobs_df):
        result = total_jobs_per_time_frequency(sample_jobs_df, "year")
        assert result["job_count"].sum() == len(sample_jobs_df)

    def test_result_is_sorted_by_period(self, sample_jobs_df):
        result = total_jobs_per_time_frequency(sample_jobs_df, "day")
        assert list(result["day"]) == sorted(result["day"])


class TestFilterByTimePeriod:
    def test_any_time_returns_everything(self, sample_jobs_df):
        result = filter_by_time_period(sample_jobs_df, "Any time")
        assert len(result) == len(sample_jobs_df)

    def test_day_excludes_older_rows(self, sample_jobs_df):
        result = filter_by_time_period(sample_jobs_df, "day")
        assert len(result) == 1
        assert result.iloc[0]["company"] == "Acme Oy"

    def test_week_excludes_rows_older_than_a_week(self, sample_jobs_df):
        result = filter_by_time_period(sample_jobs_df, "week")
        assert set(result["company"]) == {"Acme Oy"}

    def test_month_excludes_the_400_day_old_row(self, sample_jobs_df):
        result = filter_by_time_period(sample_jobs_df, "month")
        assert "Delta Oy" not in set(result["company"])

    def test_year_excludes_only_the_400_day_old_row(self, sample_jobs_df):
        result = filter_by_time_period(sample_jobs_df, "year")
        assert "Delta Oy" not in set(result["company"])
        assert "Gamma Inc" in set(result["company"])


class TestFilterJobsBySelectbox:
    def test_matches_region_field_and_seniority(self, sample_jobs_df):
        result = filter_jobs_by_selectbox(
            sample_jobs_df, "Uusimaa", "Software Development", "Entry level"
        )
        assert len(result) == 1
        assert result.iloc[0]["company"] == "Acme Oy"

    def test_no_match_returns_empty(self, sample_jobs_df):
        result = filter_jobs_by_selectbox(
            sample_jobs_df, "Uusimaa", "Astronaut", "Entry level"
        )
        assert result.empty


class TestTop10CompaniesBySelectbox:
    def test_counts_and_sorts_by_job_count(self, sample_jobs_df):
        filtered = sample_jobs_df[sample_jobs_df["region"] == "Uusimaa"]
        result = top_10_companies_by_selectbox(filtered)
        assert list(result["company"]) == ["Acme Oy", "Beta Ltd"]
        assert result[result["company"] == "Acme Oy"]["job_count"].iloc[0] == 2

    def test_truncates_to_top_10(self):
        df = pd.DataFrame(
            [{"company": f"Company {i}"} for i in range(15) for _ in range(i + 1)]
        )
        result = top_10_companies_by_selectbox(df)
        assert len(result) == 10


class TestTop10CompaniesByJobFieldAndTimePeriod:
    def test_filters_by_field_and_time(self, sample_jobs_df):
        result = top_10_companies_by_job_field_and_time_period(
            sample_jobs_df, "Software Development", "Any time"
        )
        assert set(result["company"]) == {"Acme Oy", "Gamma Inc"}


class TestTop10CompaniesByRegionAndTimePeriod:
    def test_filters_by_region_and_time(self, sample_jobs_df):
        result = top_10_companies_by_region_and_time_period(
            sample_jobs_df, "Pirkanmaa", "Any time"
        )
        assert set(result["company"]) == {"Gamma Inc", "Delta Oy"}


class TestTotalJobsByRegionAcrossFieldsAndSeniority:
    def test_sorts_fields_by_total_count_descending(self, sample_jobs_df):
        job_counts_by_field, sorted_job_fields = (
            total_jobs_by_region_and_time_period_across_job_fields_and_seniority_levels(
                sample_jobs_df, "Uusimaa", "Any time", SENIORITY_LEVELS
            )
        )
        assert list(sorted_job_fields)[0] == "Software Development"
        assert job_counts_by_field["seniority_level"].dtype.name == "category"


class TestTotalJobsByJobFieldAcrossRegionsAndSeniority:
    def test_sorts_regions_by_total_count_descending(self, sample_jobs_df):
        job_counts_by_region, sorted_regions = (
            total_jobs_by_job_field_and_time_period_across_regions_and_seniority_levels(
                sample_jobs_df, "Software Development", "Any time", SENIORITY_LEVELS
            )
        )
        assert set(sorted_regions) == {"Uusimaa", "Pirkanmaa"}
        assert job_counts_by_region["region"].dtype.name == "category"
