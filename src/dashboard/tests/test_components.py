import pytest

import components as ui
from theme import ACCENT


class TestBlueprintFraming:
    def test_cards_carry_all_four_registration_marks(self):
        """The corner marks are the design system's signature and must never be
        dropped from a framed element."""
        markup = ui.card_html("<p>body</p>")
        for position in ("tl", "tr", "bl", "br"):
            assert f'class="corner {position}"' in markup

    def test_blueprint_container_rejects_an_unmatched_key(self):
        with pytest.raises(ValueError):
            with ui.blueprint_container("filters"):
                pass


class TestRankedBarList:
    def test_bars_are_sized_against_the_largest_value(self):
        markup = ui.ranked_bar_list_html(
            [{"name": "Tieto", "value": 100}, {"name": "Wolt", "value": 25}]
        )
        assert "width:100.0%" in markup
        assert "width:25.0%" in markup

    def test_per_row_color_overrides_the_default_accent(self):
        markup = ui.ranked_bar_list_html(
            [{"name": "Director", "value": 5, "color": "#416180"}]
        )
        assert "#416180" in markup

    def test_default_fill_is_the_base_accent(self):
        markup = ui.ranked_bar_list_html([{"name": "Tieto", "value": 5}])
        assert ACCENT in markup

    def test_all_zero_values_do_not_divide_by_zero(self):
        markup = ui.ranked_bar_list_html([{"name": "Sport", "value": 0}])
        assert "width:0.0%" in markup

    def test_no_rows_yields_no_markup(self):
        assert ui.ranked_bar_list_html([]) == ""


class TestMomentumCard:
    def test_rising_months_get_an_up_arrow_in_the_accent(self):
        markup = ui.momentum_card_html(8.0, [50.0, 100.0])
        assert "▲" in markup and "+8%" in markup
        assert ACCENT in markup

    def test_falling_months_get_a_down_arrow(self):
        markup = ui.momentum_card_html(-4.0, [100.0, 50.0])
        assert "▼" in markup and "-4%" in markup

    def test_missing_comparison_is_labelled_rather_than_faked(self):
        markup = ui.momentum_card_html(None, [])
        assert "n/a" in markup

    def test_only_the_final_sparkline_bar_is_the_current_month(self):
        markup = ui.momentum_card_html(5.0, [40.0, 100.0])
        assert markup.count("var(--color-accent-300)") == 1


class TestEscaping:
    def test_scraped_text_cannot_inject_markup(self):
        """Company names and titles come from scraped pages, so they are data,
        never markup."""
        markup = ui.jobs_table_html(
            [
                {
                    "date": "01/01/2026",
                    "title": "<script>alert(1)</script>",
                    "company": "A & B",
                    "region": "Uusimaa",
                    "seniority": "Director",
                    "field": "Sales",
                    "url": "https://example.com/job",
                }
            ]
        )
        assert "<script>" not in markup
        assert "&lt;script&gt;" in markup
        assert "A &amp; B" in markup

    def test_ranked_rows_are_escaped_too(self):
        markup = ui.ranked_bar_list_html([{"name": "<b>X</b>", "value": 1}])
        assert "<b>X</b>" not in markup
