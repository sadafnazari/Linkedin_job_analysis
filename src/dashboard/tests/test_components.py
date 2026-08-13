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


class TestFilterCaptions:
    def test_kpi_cards_state_the_filters_they_were_measured_under(self):
        """ "Top recruiter: Tieto" otherwise reads as a national fact."""
        markup = ui.stat_card_html(
            "Top recruiter", "Tieto", "1,183 open roles", caption="Uusimaa · Past month"
        )
        assert "Uusimaa · Past month" in markup

    def test_momentum_card_carries_the_same_caption(self):
        markup = ui.momentum_card_html(-4.0, [100.0, 96.0], caption="All fields")
        assert "All fields" in markup

    def test_a_card_without_a_caption_gains_no_empty_line(self):
        assert "card-caption" not in ui.stat_card_html("Top region", "Uusimaa", "36%")


STACK_COLORS = {"Entry level": "#1d2d3d", "Director": "#94bce3"}
STACK_ROWS = [
    {
        "name": "Information Technology",
        "value": 100,
        "segments": [
            {"name": "Entry level", "value": 75},
            {"name": "Director", "value": 25},
        ],
        "spark": [50.0, 100.0],
    },
    {
        "name": "Sales",
        "value": 20,
        "segments": [
            {"name": "Entry level", "value": 20},
            {"name": "Director", "value": 0},
        ],
    },
]


class TestStackedBarList:
    def test_bar_length_is_the_row_value_and_bands_divide_it(self):
        markup = ui.stacked_bar_list_html(STACK_ROWS, STACK_COLORS)

        assert "width:100.0%" in markup and "width:20.0%" in markup
        assert "width:75.00%" in markup and "width:25.00%" in markup

    def test_empty_bands_are_not_drawn(self):
        markup = ui.stacked_bar_list_html(STACK_ROWS[1:], STACK_COLORS)
        assert "width:0.00%" not in markup

    def test_bands_carry_the_color_bound_to_their_name(self):
        markup = ui.stacked_bar_list_html(STACK_ROWS, STACK_COLORS)
        assert STACK_COLORS["Entry level"] in markup
        assert STACK_COLORS["Director"] in markup

    def test_every_band_carries_its_own_hover_readout(self):
        markup = ui.stacked_bar_list_html(STACK_ROWS, STACK_COLORS)
        assert 'data-readout="Entry level: 75 jobs"' in markup
        assert 'data-readout="Director: 25 jobs"' in markup

    def test_no_rows_yields_no_markup(self):
        assert ui.stacked_bar_list_html([], STACK_COLORS) == ""


class TestSparkline:
    def test_a_single_month_cannot_show_a_direction(self):
        assert "<svg" not in ui.sparkline_svg_html([100.0])

    def test_the_peak_sits_at_the_top_of_the_shape(self):
        markup = ui.sparkline_svg_html([0.0, 100.0])
        assert "0.0,13.0" in markup and "36.0,1.0" in markup


class TestLegend:
    def test_swatches_are_keyed_in_stacking_order(self):
        markup = ui.legend_html(
            [
                {"name": "Entry level", "color": "#1d2d3d"},
                {"name": "X", "color": "#fff"},
            ]
        )
        assert markup.index("Entry level") < markup.index("X")
        assert markup.count("legend-swatch") == 2

    def test_nothing_to_key_yields_no_markup(self):
        assert ui.legend_html([]) == ""


class TestMomentumGrid:
    def test_low_volume_is_marked_in_words_not_by_fading(self):
        """The reader still has to be able to read the number being warned about."""
        markup = ui.momentum_grid_html(
            [
                {
                    "name": "Lapland",
                    "postings": 12,
                    "change_percent": 30.0,
                    "is_low_volume": True,
                }
            ]
        )
        assert "low volume" in markup
        assert "opacity" not in markup

    def test_reliable_segments_are_left_unmarked(self):
        markup = ui.momentum_grid_html(
            [
                {
                    "name": "Uusimaa",
                    "postings": 2503,
                    "change_percent": -7.0,
                    "is_low_volume": False,
                }
            ]
        )
        assert "low-volume" not in markup
        assert "▼ -7%" in markup

    def test_a_segment_without_a_comparison_says_so(self):
        markup = ui.momentum_grid_html(
            [
                {
                    "name": "Kainuu",
                    "postings": 4,
                    "change_percent": None,
                    "is_low_volume": True,
                }
            ]
        )
        assert "n/a" in markup

    def test_no_segments_yields_no_markup(self):
        assert ui.momentum_grid_html([]) == ""


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

    def test_stacked_rows_and_their_band_titles_are_escaped(self):
        markup = ui.stacked_bar_list_html(
            [
                {
                    "name": "<b>X</b>",
                    "value": 1,
                    "segments": [{"name": "<i>Y</i>", "value": 1}],
                }
            ],
            {},
        )
        assert "<b>X</b>" not in markup and "<i>Y</i>" not in markup

    def test_legend_and_momentum_names_are_escaped(self):
        assert "<b>X</b>" not in ui.legend_html([{"name": "<b>X</b>", "color": "#fff"}])
        assert "<b>X</b>" not in ui.momentum_grid_html(
            [
                {
                    "name": "<b>X</b>",
                    "postings": 1,
                    "change_percent": 1.0,
                    "is_low_volume": False,
                }
            ]
        )
