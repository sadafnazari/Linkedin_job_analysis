# plots.py
"""This module provides functions for plotting data in streamlit.

Only the trend chart is drawn with Plotly. Every other figure in the design is a
ranked bar list, built as markup in :mod:`components` so it can carry the design
system's framing directly.
"""

import plotly.graph_objects as go
import streamlit as st

# Importing theme registers the Industry Plotly template as the default.
from theme import ACCENT, DIVIDER, TREND_FILL

# st.plotly_chart defaults to theme="streamlit", which replaces the figure's
# template with Streamlit's own and would silently undo the design system.
_CHART_KWARGS = {
    "theme": None,
    "width": "stretch",
    "config": {"displayModeBar": False},
}

_X_LABEL_EVERY = 4


def _month_tick_values(months):
    """Label every fourth month plus the last, so the axis stays uncrowded."""
    ticks = list(months[::_X_LABEL_EVERY])
    if len(months) and months[-1] not in ticks:
        ticks.append(months[-1])
    return ticks


def plot_trend(monthly):
    """
    Plots postings over time as a filled area chart.

    The design strips this chart to the line, its fill and two y labels: hovering
    is how a month's exact value is read, so grid, legend and axis lines are all
    removed as furniture.

    Args:
    monthly (pandas.DataFrame): Columns 'month' and 'job_count', oldest first,
                                as returned by queries.monthly_counts.

    Returns:
    None: This function does not return a value. It directly renders the chart
          using Streamlit's plotly_chart function.
    """
    months = list(monthly["month"])
    counts = list(monthly["job_count"])
    highest_count = max(counts) if counts else 0

    fig_trend = go.Figure(
        go.Scatter(
            x=months,
            y=counts,
            mode="lines",
            fill="tozeroy",
            fillcolor=TREND_FILL,
            line={"color": ACCENT, "width": 2},
            hovertemplate="<b>%{y:,}</b> jobs · %{x|%b '%y}<extra></extra>",
        )
    )
    fig_trend.update_layout(
        height=260,
        hovermode="x unified",
        # Set on the figure as well as the template: Streamlit paints its own
        # theme colors into the chart, and only figure-level values survive it.
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={
            "tickvals": _month_tick_values(months),
            "tickformat": "%b %y",
            "showspikes": True,
            "spikecolor": DIVIDER,
            "spikethickness": 1,
            "spikemode": "across",
            "spikedash": "solid",
        },
        # Only the top value and zero are labelled — the design draws no axis.
        yaxis={
            "tickvals": [0, highest_count],
            "tickformat": ",d",
            "range": [0, highest_count * 1.05 if highest_count else 1],
        },
    )
    st.plotly_chart(fig_trend, **_CHART_KWARGS)
