import pandas as pd

import tables


def job_row(job_fields):
    return pd.Series(
        {
            "date_posted": pd.Timestamp("2026-07-23"),
            "title": "Research Specialist",
            "company": "Gridle",
            "region": "North Karelia",
            "seniority_level": "Executive",
            "job_fields": job_fields,
            "job_url": "https://example.com/job",
        }
    )


class TestRowForDisplay:
    def test_dates_are_formatted_for_display(self):
        row = tables._row_for_display(job_row(["Research"]), "All fields")
        assert row["date"] == "23/07/2026"

    def test_tag_shows_the_filtered_field_when_the_posting_has_it(self):
        """A posting carries several fields; the one the user filtered on is the
        one worth showing."""
        row = tables._row_for_display(job_row(["Research", "Education"]), "Education")
        assert row["field"] == "Education"

    def test_tag_falls_back_to_the_first_field(self):
        row = tables._row_for_display(job_row(["Research", "Education"]), "All fields")
        assert row["field"] == "Research"

    def test_posting_without_fields_still_renders(self):
        row = tables._row_for_display(job_row([]), "All fields")
        assert row["field"] == "—"


class TestPageWindow:
    def test_window_is_centered_on_the_current_page(self):
        assert list(tables._page_window(page=5, total_pages=20)) == [3, 4, 5, 6, 7]

    def test_window_sticks_to_the_start(self):
        assert list(tables._page_window(page=1, total_pages=20)) == [1, 2, 3, 4, 5]

    def test_window_sticks_to_the_end(self):
        assert list(tables._page_window(page=20, total_pages=20)) == [
            16,
            17,
            18,
            19,
            20,
        ]

    def test_fewer_pages_than_the_window_shows_them_all(self):
        assert list(tables._page_window(page=1, total_pages=3)) == [1, 2, 3]
