import pandas as pd
import pytest
import streamlit as st

import plots


@pytest.fixture
def captured_chart(monkeypatch):
    captured = {}

    def fake_plotly_chart(fig, **kwargs):
        captured["fig"] = fig
        captured["kwargs"] = kwargs

    monkeypatch.setattr(st, "plotly_chart", fake_plotly_chart)
    return captured


class TestPlotLineTotalJobs:
    def test_renders_line_with_matching_data(self, captured_chart):
        job_counts = pd.DataFrame({"day": ["2026-07-01", "2026-07-02"], "job_count": [3, 5]})
        plots.plot_line_total_jobs(job_counts, "day")

        fig = captured_chart["fig"]
        assert len(fig.data) == 1
        assert list(fig.data[0].x) == list(job_counts["day"])
        assert list(fig.data[0].y) == list(job_counts["job_count"])


class TestPlotLinesTotalJobsSelectboxPerSeniorityLevel:
    def test_one_trace_per_seniority_level(self, captured_chart):
        seniority_levels = ["Entry level", "Mid-Senior level"]
        color_mapping = {"Entry level": "#111111", "Mid-Senior level": "#222222"}
        count_seniority_levels = [
            pd.DataFrame({"day": ["2026-07-01"], "job_count": [2]}),
            pd.DataFrame({"day": ["2026-07-01"], "job_count": [4]}),
        ]

        plots.plot_lines_total_jobs_selectbox_per_seniority_level(
            count_seniority_levels,
            "Uusimaa",
            "Software Development",
            seniority_levels,
            "day",
            color_mapping,
        )

        fig = captured_chart["fig"]
        assert len(fig.data) == 2
        assert [trace.name for trace in fig.data] == seniority_levels
        assert list(fig.data[0].y) == [2]
        assert list(fig.data[1].y) == [4]


class TestPlotPieTopCompaniesSelectbox:
    def test_pie_slices_match_input(self, captured_chart):
        df = pd.DataFrame(
            {"company": ["Acme Oy", "Beta Ltd"], "job_count": [7, 3]}
        )
        plots.plot_pie_top_companies_seletbox(
            df, "Uusimaa", "Software Development", "Entry level", "day"
        )

        fig = captured_chart["fig"]
        assert set(fig.data[0].labels) == {"Acme Oy", "Beta Ltd"}
        assert sorted(fig.data[0].values) == [3, 7]


class TestPlotPieTopCompaniesField:
    def test_pie_slices_match_input(self, captured_chart):
        df = pd.DataFrame({"company": ["Acme Oy"], "job_count": [5]})
        plots.plot_pie_top_companies_field(df, "Software Development", "Any time")

        fig = captured_chart["fig"]
        assert list(fig.data[0].labels) == ["Acme Oy"]
        assert list(fig.data[0].values) == [5]


class TestPlotPieTopCompaniesRegion:
    def test_pie_slices_match_input(self, captured_chart):
        df = pd.DataFrame({"company": ["Gamma Inc"], "job_count": [9]})
        plots.plot_pie_top_companies_region(df, "Pirkanmaa", "month")

        fig = captured_chart["fig"]
        assert list(fig.data[0].labels) == ["Gamma Inc"]
        assert list(fig.data[0].values) == [9]


class TestPlotStackedBarChartByRegion:
    def test_stacks_bars_by_seniority_level(self, captured_chart):
        job_counts_by_field = pd.DataFrame(
            {
                "job_fields": ["Software Development", "Accounting"],
                "seniority_level": ["Entry level", "Mid-Senior level"],
                "count": [4, 2],
            }
        )
        plots.plot_stacked_bar_chart_jobs_by_region_across_job_fields_and_seniority_levels_over_selected_time(
            job_counts_by_field,
            "Uusimaa",
            ["#111111", "#222222"],
            ["Software Development", "Accounting"],
            ["Entry level", "Mid-Senior level"],
            "Any time",
        )

        fig = captured_chart["fig"]
        assert {trace.name for trace in fig.data} == {"Entry level", "Mid-Senior level"}


class TestPlotStackedBarChartByJobField:
    def test_stacks_bars_by_seniority_level(self, captured_chart):
        job_counts_by_region = pd.DataFrame(
            {
                "region": ["Uusimaa", "Pirkanmaa"],
                "seniority_level": ["Entry level", "Mid-Senior level"],
                "count": [6, 1],
            }
        )
        plots.plot_stacked_bar_chart_jobs_by_job_field_across_regions_and_seniority_levels_over_selected_time(
            job_counts_by_region,
            "Software Development",
            ["#111111", "#222222"],
            ["Uusimaa", "Pirkanmaa"],
            ["Entry level", "Mid-Senior level"],
            "week",
        )

        fig = captured_chart["fig"]
        assert {trace.name for trace in fig.data} == {"Entry level", "Mid-Senior level"}
