# tables.py
"""This module provides function(s) for showing latest job posts on demand."""

import components as ui
import queries as qs
import streamlit as st

PAGE_SIZE = 10
_MAX_PAGE_BUTTONS = 5


def _reset_page():
    """A new search query invalidates the current page."""
    st.session_state["page"] = 1


def _reset_search():
    """Clear the query and return to the first page."""
    st.session_state["search_query"] = ""
    st.session_state["page"] = 1


def _row_for_display(job, selected_job_field):
    """Flatten one posting into the strings the table renders."""
    job_fields = job["job_fields"]
    field = (
        selected_job_field
        if selected_job_field in job_fields
        else (job_fields[0] if job_fields else "—")
    )
    return {
        "date": job["date_posted"].strftime("%d/%m/%Y"),
        "title": job["title"],
        "company": job["company"],
        "region": job["region"],
        "seniority": job["seniority_level"],
        "field": field,
        "url": job["job_url"],
    }


def _page_window(page, total_pages):
    """Center the numbered page buttons on the current page."""
    first = max(
        1, min(page - _MAX_PAGE_BUTTONS // 2, total_pages - _MAX_PAGE_BUTTONS + 1)
    )
    return range(first, min(first + _MAX_PAGE_BUTTONS, total_pages + 1))


def _render_pagination(page, total_pages):
    """Render the centered Prev / numbers / Next bar beneath the table."""
    if total_pages <= 1:
        return

    page_numbers = list(_page_window(page, total_pages))
    columns = st.columns([3, 1.4, *[0.6] * len(page_numbers), 1.4, 3])

    with columns[1]:
        if st.button("← Prev", disabled=page == 1, key="page_prev"):
            st.session_state["page"] = page - 1
            st.rerun()

    for column, page_number in zip(columns[2 : 2 + len(page_numbers)], page_numbers):
        with column:
            # The current page is outlined in the accent rather than disabled,
            # so the bar keeps its shape as the user moves through it.
            container_key = (
                "page-current" if page_number == page else f"page-other-{page_number}"
            )
            with st.container(key=container_key):
                if st.button(str(page_number), key=f"page_{page_number}"):
                    st.session_state["page"] = page_number
                    st.rerun()

    with columns[-2]:
        if st.button("Next →", disabled=page == total_pages, key="page_next"):
            st.session_state["page"] = page + 1
            st.rerun()


def render_latest_jobs(filtered_df, selected_job_field):
    """
    Renders the Latest jobs screen: search, the postings table and pagination.

    Args:
    filtered_df (pandas.DataFrame): Postings already narrowed by the sidebar
                                    filters, most recent first.
    selected_job_field (str): The active job field filter, used to choose which
                              of a posting's fields to show in its tag.

    This function does not return a value. It renders the screen with Streamlit.
    """
    search_column, range_column = st.columns([1, 1])
    with search_column:
        st.text_input(
            "Search",
            key="search_query",
            placeholder="Search by title or company…",
            label_visibility="collapsed",
            on_change=_reset_page,
        )

    query = st.session_state["search_query"]
    matching_df = qs.search_jobs(filtered_df, query)

    if matching_df.empty:
        ui.render(
            ui.card_html(
                f'<p style="margin:0">No postings match "{query}".</p>',
                extra_style="text-align:center;padding:var(--space-6) var(--space-4)",
            )
        )
        with st.container(key="ghost-clear-search"):
            st.button("Clear search", on_click=_reset_search)
        return

    page_df, page, total_pages = qs.paginate(
        matching_df, st.session_state["page"], PAGE_SIZE
    )
    st.session_state["page"] = page

    first_index = (page - 1) * PAGE_SIZE + 1
    with range_column:
        ui.render(
            ui.search_range_label_html(
                first_index, first_index + len(page_df) - 1, len(matching_df)
            )
        )

    rows = [_row_for_display(job, selected_job_field) for _, job in page_df.iterrows()]
    ui.render(ui.jobs_table_html(rows))
    _render_pagination(page, total_pages)
