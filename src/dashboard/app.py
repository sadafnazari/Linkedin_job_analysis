# app.py
"""

This is the main module for visualizing data with streamlit.
"""

import os

import components as ui
import load_resources as loader
import plots as ps
import queries as qs
import sidebar as sb
import streamlit as st
import styles as sty
import tables as tb
from load_data import load_data
from load_defaults import load_defaults
from pre_processing import pre_processing
from theme import (
    ALL_FIELDS,
    ALL_LEVELS,
    ALL_REGIONS,
    SENIORITY_ORDER,
    seniority_color,
    stack_color,
)

# Only Finland has resource data today; the sidebar's country control is shown
# but disabled, so the screens are built against this one country.
COUNTRY = "finland"

TOP_COMPANY_ROWS = 8

# Beyond five bands a stacked bar is a color-matching exercise, so the rest of
# the job fields share one bucket.
TOP_STACK_FIELDS = 5

DISTRIBUTION_VIEWS = ["Field", "Region"]
MOMENTUM_VIEWS = ["Seniority", "Region"]


def filter_summary(job_field, region, seniority_level, period):
    """
    Builds the one-line description of the active filters shown around the page.

    Args:
    job_field (str): The selected job field, or ALL_FIELDS.
    region (str): The selected region, or ALL_REGIONS.
    seniority_level (str): The selected seniority level, or ALL_LEVELS.
    period (str): The selected time period.

    Returns:
    str: The filters joined for display, e.g.
         "All fields · All regions · All levels · Past month".
    """
    return " · ".join([job_field, region, seniority_level, period])


def scope_note(relaxed_dimensions, *applied_filters):
    """
    Builds the muted line under a panel title stating which filters it obeys.

    The breakdown panels each ignore the dimensions they draw, so without this
    line a chart looks like the filter failed to apply.

    Args:
    relaxed_dimensions (sequence of str): The filters the panel deliberately
                                          ignores, e.g. ("Job field",).
    *applied_filters (str): The filter values the panel does obey, in display
                            order.

    Returns:
    str: The scope line, e.g.
         "Job field filter not applied · Uusimaa · Mid-Senior level · Past month".
    """
    relaxed = [f"{dimension} filter not applied" for dimension in relaxed_dimensions]
    return " · ".join([*relaxed, *applied_filters])


def selected_view(state_key, options):
    """
    Reads a panel's chosen view, seeding it before its control is built.

    A segmented control clears its own state when its selected option is clicked
    again, so the chosen view is repaired here rather than read as "no view".

    Args:
    state_key (str): The st.session_state key the control writes to.
    options (list of str): The control's options; the first is the default.

    Returns:
    str: The view to build the panel for.
    """
    if st.session_state.get(state_key) not in options:
        st.session_state[state_key] = options[0]
    return st.session_state[state_key]


def seniority_bands(df):
    """
    Lists the seniority levels present, in the order they stack in.

    Args:
    df (pandas.DataFrame): Job data with a 'seniority_level' column.

    Returns:
    list of str: The design's levels first, in its order, then any level the
                 scrape produced that the design does not name.
    """
    present = set(df["seniority_level"].dropna().unique())
    known = [level for level in SENIORITY_ORDER if level in present]
    return known + sorted(present - set(known))


def legend_entries(names, colors):
    """Pairs band names with their colors, in stacking order, for the legend."""
    return [{"name": name, "color": colors[name]} for name in names]


def render_kpi_row(filtered_df, untimed_df, job_field, region, summary):
    """
    Renders the four KPI cards above the trend chart.

    The field and region cards switch from "the top one" to "the selected one"
    when that dimension is already filtered, so a card never reports a value the
    user has just filtered away. Every card repeats the filter combination it was
    measured under, because "Top recruiter: Tieto" otherwise reads as a national
    fact rather than a filtered one.

    Args:
    filtered_df (pandas.DataFrame): Postings matching every active filter.
    untimed_df (pandas.DataFrame): The same postings ignoring the time period,
                                   used for month-over-month momentum.
    job_field (str): The selected job field, or ALL_FIELDS.
    region (str): The selected region, or ALL_REGIONS.
    summary (str): The one-line filter description shown under each card.

    This function does not return a value. It renders the row with Streamlit.
    """
    change_percent, sparkline = qs.momentum(qs.monthly_counts(untimed_df))

    if job_field == ALL_FIELDS:
        field_kicker = "Top job field"
        field_name, field_share, _ = qs.top_entity(filtered_df, "job_fields")
    else:
        field_kicker = "Selected field share"
        field_name = job_field
        field_share, _ = qs.entity_share(filtered_df, "job_fields", job_field)

    if region == ALL_REGIONS:
        region_kicker = "Top region"
        region_name, region_share, _ = qs.top_entity(filtered_df, "region")
    else:
        region_kicker = "Selected region share"
        region_name = region
        region_share, _ = qs.entity_share(filtered_df, "region", region)

    company_name, _, company_jobs = qs.top_entity(filtered_df, "company")

    ui.render(
        ui.kpi_row_html(
            [
                ui.momentum_card_html(change_percent, sparkline, caption=summary),
                ui.stat_card_html(
                    field_kicker,
                    field_name,
                    f"{field_share:.0f}% of all postings",
                    caption=summary,
                ),
                ui.stat_card_html(
                    region_kicker,
                    region_name,
                    f"{region_share:.0f}% of all postings",
                    caption=summary,
                ),
                ui.stat_card_html(
                    "Top recruiter",
                    company_name,
                    f"{company_jobs:,} open roles",
                    caption=summary,
                ),
            ]
        )
    )


def render_trend(trend_df, summary):
    """
    Renders the trend panel: postings per month, stacked by seniority level.

    Args:
    trend_df (pandas.DataFrame): Postings matching every filter but the period —
                                 the chart covers a fixed window of its own.
    summary (str): The one-line filter description.

    This function does not return a value. It renders the panel with Streamlit.
    """
    bands = seniority_bands(trend_df)
    colors = {level: seniority_color(level) for level in bands}

    with ui.blueprint_container("bp-trend"):
        ui.render(
            ui.panel_header_html(
                "Trend",
                "Job postings over time",
                f"{summary} · last {qs.TREND_MONTHS} months · stacked by seniority"
                " · hover for a month's values",
            )
            + ui.legend_html(legend_entries(bands, colors))
        )
        ps.plot_trend(qs.monthly_counts_by(trend_df, "seniority_level", bands))


def render_momentum_panel(df, region, job_field, seniority):
    """
    Renders the per-segment momentum panel, by seniority level or by region.

    It compares the last two complete months rather than the selected period, so
    the period filter is deliberately not applied here.

    Args:
    df (pandas.DataFrame): All postings for the country.
    region (str): The selected region, or ALL_REGIONS.
    job_field (str): The selected job field, or ALL_FIELDS.
    seniority (str): The selected seniority level, or ALL_LEVELS.

    This function does not return a value. It renders the panel with Streamlit.
    """
    view = selected_view("momentum_view", MOMENTUM_VIEWS)
    if view == "Seniority":
        segment_column = "seniority_level"
        source_df = qs.filter_jobs(df, region, job_field, ALL_LEVELS)
        subtitle = scope_note(("Seniority",), job_field, region)
    else:
        segment_column = "region"
        source_df = qs.filter_jobs(df, ALL_REGIONS, job_field, seniority)
        subtitle = scope_note(("Region",), job_field, seniority)

    header = ui.panel_header_html(
        "Momentum",
        "Change vs. previous month, by segment",
        f"{subtitle} · last complete month vs. the one before",
    )
    with ui.switcher_panel("bp-momentum", "momentum_view", MOMENTUM_VIEWS, header):
        ui.render(
            ui.note_html(
                "Sorted by volume — dashed cells have too few postings for the "
                "% to be reliable"
            )
            + ui.momentum_grid_html(qs.segment_momentum(source_df, segment_column))
        )


def render_distribution_panel(period_df, region, job_field, seniority, period):
    """
    Renders the distribution panel: job fields or regions, stacked and sparklined.

    One panel replaces the three ranked lists this screen used to carry, which
    asked the same question of three dimensions. Each view relaxes both the
    dimension it ranks and the one it stacks by, or the bars would collapse to a
    single band.

    Args:
    period_df (pandas.DataFrame): Postings inside the selected time period.
    region (str): The selected region, or ALL_REGIONS.
    job_field (str): The selected job field, or ALL_FIELDS.
    seniority (str): The selected seniority level, or ALL_LEVELS.
    period (str): The selected time period.

    This function does not return a value. It renders the panel with Streamlit.
    """
    view = selected_view("distribution_view", DISTRIBUTION_VIEWS)
    if view == "Field":
        dimension, stack_by = "job_fields", "seniority_level"
        source_df = qs.filter_jobs(period_df, region, ALL_FIELDS, ALL_LEVELS)
        stacks = seniority_bands(source_df)
        colors = {level: seniority_color(level) for level in stacks}
        title = "Job fields, stacked by seniority level"
        # The dimensions this view draws are named in its own title, so listing
        # them again as "not applied" only crowds the line.
        subtitle = scope_note((), region, period)
    else:
        dimension, stack_by = "region", "job_fields"
        source_df = qs.filter_jobs(period_df, ALL_REGIONS, ALL_FIELDS, seniority)
        # Which fields are on screen depends on the filters, so these bands are
        # bound to rank rather than to a name; the legend is what names them.
        stacks = qs.stack_order(source_df, "job_fields", TOP_STACK_FIELDS)
        colors = {
            name: stack_color(index)
            for index, name in enumerate([*stacks, qs.OTHER_STACK_LABEL])
        }
        title = "Regions, stacked by job field"
        subtitle = scope_note((), seniority, period)

    # Every field and every region is listed: a cut-off list reads as the whole
    # picture, and the sidebar offers values the panel would then never show.
    rows = qs.stacked_counts(source_df, dimension, stack_by, stacks)
    sparklines = qs.period_series(
        source_df, dimension, [row["name"] for row in rows], period
    )
    for row in rows:
        row["spark"] = sparklines[row["name"]]
    bands = [segment["name"] for segment in rows[0]["segments"]] if rows else []

    header = ui.panel_header_html("Distribution", title, subtitle)
    with ui.switcher_panel(
        "bp-distribution", "distribution_view", DISTRIBUTION_VIEWS, header
    ):
        ui.render(
            ui.legend_html(legend_entries(bands, colors))
            + ui.stacked_bar_list_html(rows, colors)
        )


def render_analysis(
    df, period_df, filtered_df, summary, region, job_field, seniority, period
):
    """
    Renders the Analysis screen: KPI row, trend, recruiters, momentum, distribution.

    Args:
    df (pandas.DataFrame): All postings for the country.
    period_df (pandas.DataFrame): Postings inside the selected time period.
    filtered_df (pandas.DataFrame): Postings matching every active filter.
    summary (str): The one-line filter description.
    region (str): The selected region, or ALL_REGIONS.
    job_field (str): The selected job field, or ALL_FIELDS.
    seniority (str): The selected seniority level, or ALL_LEVELS.
    period (str): The selected time period.

    This function does not return a value. It renders the screen with Streamlit.
    """
    # The trend covers a fixed 24-month window, so it ignores the period filter.
    trend_df = qs.filter_jobs(df, region, job_field, seniority)
    render_kpi_row(filtered_df, trend_df, job_field, region, summary)
    render_trend(trend_df, summary)

    ui.render(
        ui.panel_html(
            "Top recruiting companies",
            "Ranked by open roles",
            ui.ranked_bar_list_html(
                qs.ranked_counts(filtered_df, "company", TOP_COMPANY_ROWS),
                label_width=220,
                value_width=44,
            ),
            subtitle=scope_note((), job_field, region, seniority, period),
        )
    )

    st.write("")
    render_momentum_panel(df, region, job_field, seniority)
    st.write("")
    render_distribution_panel(period_df, region, job_field, seniority, period)


def render_empty_state(summary):
    """
    Renders the "no matching postings" card in place of a screen's content.

    Args:
    summary (str): The one-line filter description.

    This function does not return a value. It renders the card with Streamlit.
    """
    ui.render(ui.empty_state_html(summary))
    with st.container(key="ghost-reset-empty"):
        st.button("Reset filters", on_click=sb.reset_filters, key="reset_empty")


if __name__ == "__main__":
    app_path = os.path.dirname(os.path.abspath(__file__))
    app_path += "/../.."

    st.set_page_config(page_title="LinkedIn Job Analysis", layout="wide")
    sty.apply_page_style()

    df = load_data()
    df = pre_processing(df, COUNTRY)

    countries = loader.load_countries(app_path)
    regions = loader.load_regions(app_path, COUNTRY)
    job_fields = loader.load_job_fields(app_path, COUNTRY)
    seniority_levels = loader.load_seniority_levels(app_path, COUNTRY)
    filter_options = {
        "region": [ALL_REGIONS, *regions],
        "job_field": [ALL_FIELDS, *job_fields],
        "seniority_level": [ALL_LEVELS, *seniority_levels],
        "period": list(qs.PERIOD_OFFSETS),
    }
    default_region, default_job_field, default_seniority, default_period = (
        load_defaults(app_path, COUNTRY)
    )
    sb.initialise_filter_state(
        {
            "region": default_region,
            "job_field": default_job_field,
            "seniority_level": default_seniority,
            "period": default_period,
        },
        filter_options,
    )

    last_updated = df["date_posted"].max()
    ui.render(
        ui.top_nav_html(
            f"Updated {last_updated:%b} {last_updated.day}, {last_updated.year}"
            " · updates daily"
        )
    )

    sb.render_filters(countries, filter_options)

    selected_region = st.session_state["region"]
    selected_job_field = st.session_state["job_field"]
    selected_seniority = st.session_state["seniority_level"]
    selected_period = st.session_state["period"]
    summary = filter_summary(
        selected_job_field, selected_region, selected_seniority, selected_period
    )

    period_df = qs.filter_by_period(df, selected_period)
    filtered_df = qs.filter_jobs(
        period_df, selected_region, selected_job_field, selected_seniority
    )
    sb.render_total_matched(len(filtered_df), summary)

    is_analysis = st.session_state["tab"] != "Latest jobs"
    title_column, tab_column = st.columns([3, 1])
    with title_column:
        ui.render(
            ui.page_header_html(
                "Hiring trends" if is_analysis else "Latest jobs",
                (
                    (
                        "LinkedIn job postings across Finland, collected hourly "
                        "and updated daily."
                    )
                    if is_analysis
                    else summary
                ),
            )
        )
    with tab_column, st.container(key="page-tabs"):
        st.segmented_control(
            "View",
            options=["Analysis", "Latest jobs"],
            key="tab",
            label_visibility="collapsed",
        )

    if filtered_df.empty:
        render_empty_state(summary)
    elif is_analysis:
        render_analysis(
            df,
            period_df,
            filtered_df,
            summary,
            selected_region,
            selected_job_field,
            selected_seniority,
            selected_period,
        )
    else:
        tb.render_latest_jobs(
            filtered_df.sort_values("date_posted", ascending=False),
            selected_job_field,
        )
