import pandas as pd
import pytest
import streamlit as st

import plots
import theme


@pytest.fixture
def captured_chart(monkeypatch):
    captured = {}

    def fake_plotly_chart(fig, **kwargs):
        captured["fig"] = fig
        captured["kwargs"] = kwargs

    monkeypatch.setattr(st, "plotly_chart", fake_plotly_chart)
    return captured


MONTHLY = pd.DataFrame(
    {
        "month": pd.date_range("2025-01-31", periods=6, freq="ME"),
        "Mid-Senior level": [6, 9, 5, 12, 11, 15],
        "Entry level": [4, 5, 4, 8, 7, 10],
    }
)
TOTALS = [10, 14, 9, 20, 18, 25]


class TestPlotTrend:
    def test_one_stacked_band_per_seniority_level(self, captured_chart):
        plots.plot_trend(MONTHLY)

        bands = [trace for trace in captured_chart["fig"].data if trace.stackgroup]
        assert [band.name for band in bands] == ["Mid-Senior level", "Entry level"]
        assert list(bands[0].y) == list(MONTHLY["Mid-Senior level"])

    def test_bands_carry_their_level_color_not_the_series_order(self, captured_chart):
        plots.plot_trend(MONTHLY)

        bands = [trace for trace in captured_chart["fig"].data if trace.stackgroup]
        assert [band.fillcolor for band in bands] == [
            theme.seniority_color("Mid-Senior level"),
            theme.seniority_color("Entry level"),
        ]

    def test_month_total_is_hoverable_without_being_drawn(self, captured_chart):
        """The stacked bands can only report their own value, so the total is
        carried by an invisible line along the top of the stack."""
        plots.plot_trend(MONTHLY)

        total = captured_chart["fig"].data[-1]
        assert total.name == "Total"
        assert list(total.y) == TOTALS
        assert total.line.width == 0

    def test_y_axis_labels_only_zero_and_the_peak_of_the_stack(self, captured_chart):
        plots.plot_trend(MONTHLY)

        assert list(captured_chart["fig"].layout.yaxis.tickvals) == [0, max(TOTALS)]

    def test_x_axis_labels_every_fourth_month_plus_the_last(self, captured_chart):
        plots.plot_trend(MONTHLY)

        ticks = list(captured_chart["fig"].layout.xaxis.tickvals)
        assert ticks == [MONTHLY["month"][0], MONTHLY["month"][4], MONTHLY["month"][5]]

    def test_industry_template_survives_streamlit(self, captured_chart):
        """st.plotly_chart defaults to theme="streamlit", which would replace the
        Industry template and silently undo the design system."""
        plots.plot_trend(MONTHLY)

        assert captured_chart["kwargs"]["theme"] is None
        assert captured_chart["kwargs"]["config"]["displayModeBar"] is False

    def test_empty_history_still_renders(self, captured_chart):
        plots.plot_trend(pd.DataFrame())

        assert len(captured_chart["fig"].data) == 1
