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
from theme import ALL_FIELDS, ALL_LEVELS, ALL_REGIONS, seniority_color

# Only Finland has resource data today; the sidebar's country control is shown
# but disabled, so the screens are built against this one country.
COUNTRY = "finland"

TOP_COMPANY_ROWS = 8
BREAKDOWN_ROWS = 14


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


def scope_note(relaxed_dimension, *applied_filters):
    """
    Builds the muted line under a panel title stating which filters it obeys.

    The breakdown panels each ignore their own dimension, so without this line a
    chart looks like the filter failed to apply.

    Args:
    relaxed_dimension (str): The filter the panel deliberately ignores, e.g.
                             "Job field", or None when it obeys every filter.
    *applied_filters (str): The filter values the panel does obey, in display
                            order.

    Returns:
    str: The scope line, e.g.
         "Job field filter not applied · Uusimaa · Mid-Senior level · Past month".
    """
    applied = list(applied_filters)
    if relaxed_dimension:
        applied.insert(0, f"{relaxed_dimension} filter not applied")
    return " · ".join(applied)


def render_kpi_row(filtered_df, untimed_df, job_field, region):
    """
    Renders the four KPI cards above the trend chart.

    The field and region cards switch from "the top one" to "the selected one"
    when that dimension is already filtered, so a card never reports a value the
    user has just filtered away.

    Args:
    filtered_df (pandas.DataFrame): Postings matching every active filter.
    untimed_df (pandas.DataFrame): The same postings ignoring the time period,
                                   used for month-over-month momentum.
    job_field (str): The selected job field, or ALL_FIELDS.
    region (str): The selected region, or ALL_REGIONS.

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
                ui.momentum_card_html(change_percent, sparkline),
                ui.stat_card_html(
                    field_kicker, field_name, f"{field_share:.0f}% of all postings"
                ),
                ui.stat_card_html(
                    region_kicker, region_name, f"{region_share:.0f}% of all postings"
                ),
                ui.stat_card_html(
                    "Top recruiter", company_name, f"{company_jobs:,} open roles"
                ),
            ]
        )
    )


def render_analysis(
    df, period_df, filtered_df, summary, region, job_field, seniority, period
):
    """
    Renders the Analysis screen: KPI row, trend chart and four ranked lists.

    The job field and region breakdowns deliberately ignore their own filter, so
    narrowing one of them does not collapse its chart to a single row — they stay
    comparison views.

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
    render_kpi_row(filtered_df, trend_df, job_field, region)

    with ui.blueprint_container("bp-trend"):
        ui.render(
            '<div class="industry"><div class="card-kicker">Trend</div>'
            '<h4 class="card-title" style="margin-bottom:2px">Job postings over time</h4>'
            '<div class="text-muted" style="font-size:12px">'
            f"{summary} · last {qs.TREND_MONTHS} months · "
            "hover the line for a month's value</div></div>"
        )
        ps.plot_trend(qs.monthly_counts(trend_df))

    companies_panel = ui.panel_html(
        "Top recruiting companies",
        "Companies hiring for the selected filters",
        ui.ranked_bar_list_html(
            qs.ranked_counts(filtered_df, "company", TOP_COMPANY_ROWS)
        ),
        subtitle=scope_note(None, job_field, region, seniority, period),
    )

    # Every level is shown whatever the seniority filter says, so the mix reads
    # as context instead of collapsing to a single row.
    all_levels_df = qs.filter_jobs(period_df, region, job_field, ALL_LEVELS)
    seniority_rows = qs.ranked_counts(all_levels_df, "seniority_level")
    for row in seniority_rows:
        row["color"] = seniority_color(row["name"])
    seniority_panel = ui.panel_html(
        "Seniority mix",
        "Every seniority level, not just the selected one",
        ui.ranked_bar_list_html(seniority_rows),
        subtitle=scope_note("Seniority", job_field, region, period),
    )

    ui.render(ui.two_column_row_html(companies_panel, seniority_panel))

    all_fields_df = qs.filter_jobs(period_df, region, ALL_FIELDS, seniority)
    ui.render(
        ui.panel_html(
            "By job field",
            "Every job field, not just the selected one",
            ui.ranked_bar_list_html(
                qs.ranked_counts(all_fields_df, "job_fields", BREAKDOWN_ROWS),
                label_width=220,
                value_width=44,
            ),
            subtitle=scope_note("Job field", region, seniority, period),
        )
    )

    st.write("")
    all_regions_df = qs.filter_jobs(period_df, ALL_REGIONS, job_field, seniority)
    ui.render(
        ui.panel_html(
            "By region",
            "Every region, not just the selected one",
            ui.ranked_bar_list_html(
                qs.ranked_counts(all_regions_df, "region", BREAKDOWN_ROWS),
                label_width=220,
                value_width=44,
            ),
            subtitle=scope_note("Region", job_field, seniority, period),
        )
    )


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
                "Tech hiring trends" if is_analysis else "Latest jobs",
                (
                    (
                        "Job postings across Finland, broken down by field, "
                        "region and seniority."
                    )
                    if is_analysis
                    else summary
                ),
            )
        )
    with tab_column:
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
