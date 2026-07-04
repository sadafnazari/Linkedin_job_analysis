import pandas as pd

from pre_processing import pre_processing


def raw_df():
    return pd.DataFrame(
        [
            {
                "date_posted": "2026-07-01 10:00:00",
                "job_fields": '["Software Development"]',
                "country": "Finland",
                "region": "Uusimaa",
            },
            {
                "date_posted": "2026-07-02 10:00:00",
                "job_fields": '["Accounting", "Consulting"]',
                "country": "finland",
                "region": "Unspecified",
            },
            {
                "date_posted": "2026-07-03 10:00:00",
                "job_fields": '["Accounting"]',
                "country": "Sweden",
                "region": "Stockholm",
            },
        ]
    )


class TestPreProcessing:
    def test_parses_job_fields_string_into_list(self):
        result = pre_processing(raw_df(), "finland")
        assert result.iloc[0]["job_fields"] == ["Software Development"]

    def test_converts_date_posted_to_datetime(self):
        result = pre_processing(raw_df(), "finland")
        assert pd.api.types.is_datetime64_any_dtype(result["date_posted"])

    def test_filters_by_country_matching_lowercase_directory_name(self):
        # selected_country is always a lowercase resources/<country> directory
        # name in practice (see load_resources.load_countries / app.py), so
        # that's the input pre_processing actually receives.
        result = pre_processing(raw_df(), "finland")
        assert set(result["country"].str.lower()) == {"finland"}

    def test_uppercase_selected_country_matches_nothing(self):
        # pre_processing.py compares df["country"].str.lower() == selected_country
        # without lowercasing selected_country, so anything but an
        # already-lowercase value silently matches zero rows. This only
        # doesn't bite today because callers always pass a lowercase
        # directory name.
        result = pre_processing(raw_df(), "FINLAND")
        assert result.empty

    def test_excludes_unspecified_region(self):
        result = pre_processing(raw_df(), "finland")
        assert "Unspecified" not in set(result["region"])

    def test_excludes_other_countries(self):
        result = pre_processing(raw_df(), "finland")
        assert "Sweden" not in set(result["country"])

    def test_leaves_already_parsed_job_fields_untouched(self):
        df = raw_df()
        df.loc[0, "job_fields"] = ["Software Development"]
        result = pre_processing(df, "finland")
        assert result.iloc[0]["job_fields"] == ["Software Development"]
