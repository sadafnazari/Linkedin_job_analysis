# plots.py
"""This module provides functions for plotting data in streamlit.

Only the trend chart is drawn with Plotly. Every other figure in the design is a
ranked bar list, built as markup in :mod:`components` so it can carry the design
system's framing directly.
"""

import plotly.graph_objects as go
import streamlit as st

# Importing theme registers the Industry Plotly template as the default.
from theme import DIVIDER, SEGMENT_OUTLINE, seniority_color

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
    Plots postings over time as an area chart stacked by seniority level.

    The bands answer "which levels moved" without a second chart, and carry the
    same colors as every other stack on the page. The design strips the rest to
    two y labels: hovering is how a month's values are read, so grid, in-chart
    legend and axis lines are all removed as furniture. The legend lives above the
    chart, drawn as markup.

    Args:
    monthly (pandas.DataFrame): Column 'month' followed by one column per
                                seniority level in stacking order, oldest month
                                first, as returned by queries.monthly_counts_by.

    Returns:
    None: This function does not return a value. It directly renders the chart
          using Streamlit's plotly_chart function.
    """
    months = list(monthly["month"]) if "month" in monthly else []
    levels = [column for column in monthly.columns if column != "month"]
    totals = monthly[levels].sum(axis=1) if levels else []
    highest_count = int(max(totals)) if len(totals) else 0

    fig_trend = go.Figure()
    for level in levels:
        fig_trend.add_trace(
            go.Scatter(
                x=months,
                y=list(monthly[level]),
                name=level,
                mode="lines",
                stackgroup="seniority",
                fillcolor=seniority_color(level),
                # A hairline between bands, so the palest one still has an edge.
                line={"color": SEGMENT_OUTLINE, "width": 1},
                hovertemplate=f"{level}: <b>%{{y:,}}</b><extra></extra>",
            )
        )
    # The stack's own traces can only report their own band, so the month's total
    # is carried by an invisible line drawn along the top of the stack.
    fig_trend.add_trace(
        go.Scatter(
            x=months,
            y=list(totals),
            name="Total",
            mode="lines",
            line={"width": 0},
            hovertemplate="All levels: <b>%{y:,}</b> jobs<extra></extra>",
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
