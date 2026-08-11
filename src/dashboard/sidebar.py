# sidebar.py
"""This module provides functions for rendering the sidebar menu."""

import components as ui
import streamlit as st

FILTER_STATE_KEYS = ("region", "job_field", "seniority_level", "period")


def initialise_filter_state(configured_defaults, filter_options):
    """
    Seeds the filter, tab and table state on the first run of a session.

    Every filter opens on the value configured in streamlit_config.json, so a
    deployment decides which view the dashboard lands on. A configured value
    that is not one of the loaded options is rejected here, because a selectbox
    would otherwise swap it for its first option without saying so.

    Args:
    configured_defaults (dict): Opening value for each key in FILTER_STATE_KEYS.
    filter_options (dict): Selectable values for each key in FILTER_STATE_KEYS.

    Raises:
    ValueError: If a configured default is not among that filter's options.

    This function does not return a value. It writes to st.session_state.
    """
    for key in FILTER_STATE_KEYS:
        if configured_defaults[key] not in filter_options[key]:
            raise ValueError(
                f"initialise_filter_state: configured default for {key!r} is "
                f"{configured_defaults[key]!r}, which is not one of "
                f"{filter_options[key]}. Correct configs/streamlit_config.json "
                f"or the matching resources file."
            )

    defaults = {
        **configured_defaults,
        "tab": "Analysis",
        "search_query": "",
        "page": 1,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    st.session_state["_filter_defaults"] = defaults


def reset_filters():
    """
    Returns every filter to its default and sends the table back to page one.

    Runs as a button callback so the new values are in place before the widgets
    are instantiated on the next run — Streamlit rejects writes to a widget's
    state after it has been created.

    This function does not return a value. It writes to st.session_state.
    """
    defaults = st.session_state["_filter_defaults"]
    for key in (*FILTER_STATE_KEYS, "search_query", "page"):
        st.session_state[key] = defaults[key]


def _reset_page():
    """Any change of filter invalidates the current page of the jobs table."""
    st.session_state["page"] = 1


def render_filters(countries, filter_options):
    """
    Renders the sidebar's filter card.

    Selections are held in st.session_state under the keys in FILTER_STATE_KEYS,
    so callers read them from there rather than from a return value. The options
    are the same lists initialise_filter_state validated the defaults against.

    Args:
    countries (list of str): Countries with resource data. Only one is tracked
                             today, so the control is shown but disabled.
    filter_options (dict): Selectable values for each key in FILTER_STATE_KEYS.

    This function does not return a value. It renders widgets with Streamlit.
    """
    with st.sidebar:
        with ui.blueprint_container("bp-filters"):
            st.markdown(
                '<div class="industry"><h6>Filters</h6></div>',
                unsafe_allow_html=True,
            )
            st.selectbox(
                "Country",
                options=[country.capitalize() for country in countries],
                disabled=True,
                help="Only Finland is tracked right now",
            )
            st.selectbox(
                "Region",
                options=filter_options["region"],
                key="region",
                on_change=_reset_page,
            )
            st.selectbox(
                "Job field",
                options=filter_options["job_field"],
                key="job_field",
                on_change=_reset_page,
            )
            st.selectbox(
                "Seniority level",
                options=filter_options["seniority_level"],
                key="seniority_level",
                on_change=_reset_page,
            )
            st.selectbox(
                "Time period",
                options=filter_options["period"],
                key="period",
                on_change=_reset_page,
            )
            with st.container(key="ghost-reset"):
                st.button("Reset filters", on_click=reset_filters)


def render_total_matched(total_jobs, filter_summary):
    """
    Renders the sidebar's live count of postings matching the active filters.

    Called after filtering so the count is the one actually on screen.

    Args:
    total_jobs (int): Number of matching postings.
    filter_summary (str): One-line description of the active filters.

    This function does not return a value. It writes the card with Streamlit.
    """
    with st.sidebar:
        ui.render(ui.total_matched_card_html(total_jobs, filter_summary))
