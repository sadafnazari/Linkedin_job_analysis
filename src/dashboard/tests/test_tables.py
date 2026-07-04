import pandas as pd
import pytest
import streamlit as st

import tables


@pytest.fixture
def captured_data_editor(monkeypatch):
    captured = {}

    monkeypatch.setattr(st, "markdown", lambda *a, **k: None)

    def fake_data_editor(df, **kwargs):
        captured["df"] = df
        captured["kwargs"] = kwargs

    monkeypatch.setattr(st, "data_editor", fake_data_editor)
    return captured


class TestCreateDfLatestJobs:
    def test_sorts_by_date_posted_descending(self, captured_data_editor):
        df = pd.DataFrame(
            {
                "date_posted": ["2026-07-01", "2026-07-03", "2026-07-02"],
                "title": ["A", "B", "C"],
                "company": ["Acme", "Beta", "Gamma"],
                "region": ["Uusimaa", "Uusimaa", "Uusimaa"],
                "seniority_level": ["Entry level"] * 3,
                "job_fields": [["Software Development"]] * 3,
                "job_url": ["u1", "u2", "u3"],
            }
        )

        tables.create_df_latest_jobs(df, "Software Development")

        result = captured_data_editor["df"]
        assert list(result["title"]) == ["B", "C", "A"]

    def test_overwrites_job_fields_with_selected_job_field(self, captured_data_editor):
        df = pd.DataFrame(
            {
                "date_posted": ["2026-07-01"],
                "title": ["A"],
                "company": ["Acme"],
                "region": ["Uusimaa"],
                "seniority_level": ["Entry level"],
                "job_fields": [["Software Development", "Consulting"]],
                "job_url": ["u1"],
            }
        )

        tables.create_df_latest_jobs(df, "Software Development")

        result = captured_data_editor["df"]
        assert list(result["job_fields"]) == ["Software Development"]

    def test_only_includes_expected_columns(self, captured_data_editor):
        df = pd.DataFrame(
            {
                "date_posted": ["2026-07-01"],
                "title": ["A"],
                "company": ["Acme"],
                "region": ["Uusimaa"],
                "seniority_level": ["Entry level"],
                "job_fields": [["Software Development"]],
                "job_url": ["u1"],
                "industries": ["IT Services"],
            }
        )

        tables.create_df_latest_jobs(df, "Software Development")

        result = captured_data_editor["df"]
        assert "industries" not in result.columns
