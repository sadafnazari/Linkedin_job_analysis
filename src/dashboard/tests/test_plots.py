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


MONTHLY = pd.DataFrame(
    {
        "month": pd.date_range("2025-01-31", periods=6, freq="ME"),
        "job_count": [10, 14, 9, 20, 18, 25],
    }
)


class TestPlotTrend:
    def test_renders_one_filled_series(self, captured_chart):
        plots.plot_trend(MONTHLY)

        fig = captured_chart["fig"]
        assert len(fig.data) == 1
        assert fig.data[0].fill == "tozeroy"
        assert list(fig.data[0].y) == list(MONTHLY["job_count"])

    def test_y_axis_labels_only_zero_and_the_peak(self, captured_chart):
        plots.plot_trend(MONTHLY)

        assert list(captured_chart["fig"].layout.yaxis.tickvals) == [0, 25]

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
        plots.plot_trend(pd.DataFrame({"month": [], "job_count": []}))

        assert len(captured_chart["fig"].data) == 1
