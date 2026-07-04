from unittest.mock import MagicMock

import pandas as pd
import streamlit as st

import load_data


class TestLoadData:
    def test_queries_with_expected_filters_and_columns(self, monkeypatch):
        monkeypatch.setattr(
            st,
            "secrets",
            {
                "postgres": {
                    "user": "test_user",
                    "password": "test_password",
                    "dbname": "test_db",
                    "host": "localhost",
                    "port": "5432",
                }
            },
        )
        fake_engine = MagicMock()
        monkeypatch.setattr(load_data, "create_engine", lambda url: fake_engine)

        captured_query = {}

        def fake_read_sql(query, engine):
            captured_query["query"] = query
            captured_query["engine"] = engine
            return pd.DataFrame(
                {
                    "date_posted": ["2026-07-01"],
                    "title": ["Software Engineer"],
                    "company": ["Acme Oy"],
                    "region": ["Uusimaa"],
                    "country": ["Finland"],
                    "seniority_level": ["Entry level"],
                    "job_fields": ['["Software Development"]'],
                    "job_url": ["https://example.com/1"],
                }
            )

        monkeypatch.setattr(pd, "read_sql", fake_read_sql)
        load_data.load_data.clear()

        result = load_data.load_data()

        assert "seniority_level != 'Not Applicable'" in captured_query["query"]
        assert "region != 'Unspecified'" in captured_query["query"]
        assert captured_query["engine"] is fake_engine
        assert list(result.columns) == [
            "date_posted",
            "title",
            "company",
            "region",
            "country",
            "seniority_level",
            "job_fields",
            "job_url",
        ]
