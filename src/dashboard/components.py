# components.py
"""Builders for the design's HTML components.

Most of this dashboard is markup we author rather than Streamlit widgets: the
blueprint cards, the KPI row, the ranked bar lists and the jobs table. Building
them here keeps the exact structure from ``design/prototype.html`` in one place,
and keeps every value that reaches the page escaped — company names, job titles
and regions all come from scraped data.

Each ``*_html`` function returns a string so callers can compose a whole card in
one ``st.markdown`` block; :func:`render` writes one out.
"""

from contextlib import contextmanager
from html import escape

import streamlit as st

from theme import ACCENT, MUTED_TEXT, NEUTRAL_RAMP

_CORNERS = (
    '<i class="corner tl"></i><i class="corner tr"></i>'
    '<i class="corner bl"></i><i class="corner br"></i>'
)

_SPARKLINE_WIDTH = 36
_SPARKLINE_HEIGHT = 14


def _change_markup(change_percent):
    """
    Renders a month-over-month change the same way wherever it appears.

    Args:
    change_percent (float or None): The change, e.g. -4.0, or None when there is
                                    no previous month to compare against.

    Returns:
    tuple: (arrow, label, color).
    """
    if change_percent is None:
        return "", "n/a", NEUTRAL_RAMP[700]
    is_positive = change_percent > 0
    return (
        "▲" if is_positive else "▼",
        f"{change_percent:+.0f}%",
        ACCENT if is_positive else NEUTRAL_RAMP[700],
    )


def _caption_html(caption):
    """Renders the muted line naming the filters a card's value was measured under."""
    if not caption:
        return ""
    return f'<div class="card-caption">{escape(caption)}</div>'


def render(html):
    """
    Writes a block of component markup to the page.

    Args:
    html (str): Markup produced by the builders in this module.

    This function does not return a value. It writes the markup with Streamlit.
    """
    st.markdown(html, unsafe_allow_html=True)


@contextmanager
def blueprint_container(key):
    """
    Opens a blueprint card that can hold real Streamlit widgets.

    Card markup built as a string cannot wrap a widget, so containers keyed
    ``bp-*`` are styled as cards by the injected sheet, and the four corner marks
    are written inside as absolutely positioned children.

    Args:
    key (str): A container key beginning with "bp-", unique on the page.

    Yields:
    streamlit.delta_generator.DeltaGenerator: The container to write into.

    Raises:
    ValueError: If the key lacks the "bp-" prefix the stylesheet matches on.
    """
    if not key.startswith("bp-"):
        raise ValueError(
            f"blueprint_container: key must start with 'bp-' for the stylesheet "
            f"to match it, got {key!r}"
        )
    container = st.container(key=key)
    with container:
        st.markdown(
            f'<div class="industry" style="height:0">{_CORNERS}</div>',
            unsafe_allow_html=True,
        )
        yield container


def card_html(inner_html, extra_style=""):
    """
    Wraps content in a blueprint card: square, hairline-bordered, corner-marked.

    Args:
    inner_html (str): Already-escaped markup to place inside the card.
    extra_style (str): Optional additional inline CSS for the card element.

    Returns:
    str: The card markup.
    """
    return (
        f'<div class="industry card blueprint elev-sm" '
        f'style="position:relative;{extra_style}">{_CORNERS}{inner_html}</div>'
    )


def top_nav_html(last_updated_label):
    """
    Builds the page's top navigation bar.

    Args:
    last_updated_label (str): The right-hand status line, e.g.
                              "Updated Aug 9, 2026 · updates daily".

    Returns:
    str: The nav markup, fixed to the top of the viewport.
    """
    return (
        '<div class="industry industry-nav-wrap"><div class="industry-nav">'
        '<span class="nav-brand">LinkedIn Job '
        '<span style="color:var(--color-accent)">Analysis</span></span>'
        f'<span class="text-muted" style="margin-left:auto;font-size:12px">'
        f"{escape(last_updated_label)}</span>"
        "</div></div>"
    )


def stat_card_html(kicker, value, meta, caption=None):
    """
    Builds one of the three plain KPI cards (top field, top region, top recruiter).

    Args:
    kicker (str): The small uppercase label above the value.
    value (str): The headline value, e.g. a field or company name.
    meta (str): The supporting line beneath it.
    caption (str): Optional filter combination the value was measured under, so
                   a scoped "top recruiter" is not read as a national one.

    Returns:
    str: The card markup.
    """
    return card_html(
        f'<div class="card-kicker">{escape(kicker)}</div>'
        f'<div class="card-title kpi-value" title="{escape(value)}">{escape(value)}</div>'
        f'<div class="card-meta">{escape(meta)}</div>'
        f"{_caption_html(caption)}"
    )


def momentum_card_html(change_percent, sparkline_percents, caption=None):
    """
    Builds the momentum KPI card: direction, month-over-month change, sparkline.

    The sparkline gives the raw percentage some context, so one noisy month does
    not read as more meaningful than it is. Its final bar is the current month.

    Args:
    change_percent (float or None): Month-over-month change, e.g. -4.0. None when
                                    there is no previous month to compare against.
    sparkline_percents (list of float): Relative heights, 0-100, oldest first.
    caption (str): Optional filter combination the change was measured under.

    Returns:
    str: The card markup.
    """
    arrow, label, color = _change_markup(change_percent)

    last_index = len(sparkline_percents) - 1
    bars = "".join(
        f'<span style="height:{percent:.0f}%;'
        f'background:{ACCENT if index == last_index else "var(--color-accent-300)"}">'
        "</span>"
        for index, percent in enumerate(sparkline_percents)
    )
    return card_html(
        '<div class="card-kicker">Momentum</div>'
        f'<div class="card-title kpi-momentum" style="color:{color}">{arrow} {label}</div>'
        '<div class="card-meta">vs. previous month</div>'
        f'<div class="spark">{bars}</div>'
        f"{_caption_html(caption)}"
    )


def kpi_row_html(cards_html):
    """
    Lays the KPI cards out in one equal-width row.

    Args:
    cards_html (list of str): Card markup, in display order.

    Returns:
    str: The row markup.
    """
    return (
        '<div class="industry" style="display:grid;'
        f"grid-template-columns:repeat({len(cards_html)},1fr);"
        'gap:var(--space-4);margin-bottom:var(--space-6)">'
        f'{"".join(cards_html)}</div>'
    )


def legend_html(entries):
    """
    Builds the color key that sits above a stacked chart, never below it.

    A legend under the bars is read after the colors have already been guessed at,
    so it goes between the description and the first bar. Each swatch carries a
    hairline outline, or the palest steps vanish into the page.

    Args:
    entries (list of dict): Each with 'name' (str) and 'color' (hex), in the same
                            order the segments stack in.

    Returns:
    str: The legend markup, empty when there is nothing to key.
    """
    if not entries:
        return ""
    items = "".join(
        f'<span class="legend-item">'
        f'<i class="legend-swatch" style="background:{entry["color"]}"></i>'
        f'{escape(str(entry["name"]))}</span>'
        for entry in entries
    )
    return f'<div class="legend">{items}</div>'


def sparkline_svg_html(percents):
    """
    Builds the small inline shape showing a row's recent direction.

    Args:
    percents (list of float): Relative heights, 0-100, oldest first.

    Returns:
    str: An inline SVG, or an empty cell's markup when a single month cannot
         describe a direction.
    """
    if len(percents) < 2:
        return '<div class="rank-spark"></div>'

    step = _SPARKLINE_WIDTH / (len(percents) - 1)
    usable_height = _SPARKLINE_HEIGHT - 2
    points = " ".join(
        f"{index * step:.1f},{1 + usable_height - percent / 100 * usable_height:.1f}"
        for index, percent in enumerate(percents)
    )
    return (
        f'<svg class="rank-spark" width="{_SPARKLINE_WIDTH}" '
        f'height="{_SPARKLINE_HEIGHT}" viewBox="0 0 {_SPARKLINE_WIDTH} '
        f'{_SPARKLINE_HEIGHT}" preserveAspectRatio="none" aria-hidden="true">'
        f'<polyline points="{points}" fill="none" stroke="{ACCENT}" '
        'stroke-width="1" vector-effect="non-scaling-stroke"/></svg>'
    )


def ranked_bar_list_html(rows, label_width=120, value_width=40):
    """
    Builds a ranked bar list: a label, a track with a proportional fill, a value.

    Every ranked chart in the design uses this one pattern, so bar length is
    always read against the same track. Rows arrive already ordered.

    Args:
    rows (list of dict): Each with 'name' (str), 'value' (int) and optionally
                         'color' (hex, defaults to the base accent). Fill widths
                         are computed here as a share of the largest value.
    label_width (int): Width of the label column in pixels.
    value_width (int): Width of the value column in pixels.

    Returns:
    str: The list markup, empty when there are no rows.
    """
    if not rows:
        return ""

    largest_value = max(row["value"] for row in rows) or 1
    row_markup = []
    for row in rows:
        fill_percent = row["value"] / largest_value * 100
        color = row.get("color", ACCENT)
        row_markup.append(
            '<div class="rank-row">'
            f'<div class="rank-name" title="{escape(str(row["name"]))}">'
            f'{escape(str(row["name"]))}</div>'
            '<div class="rank-track">'
            f'<div class="rank-fill" style="width:{fill_percent:.1f}%;background:{color}">'
            "</div></div>"
            f'<div class="rank-value">{row["value"]:,}</div>'
            "</div>"
        )
    return (
        f'<div class="rank-list" style="--rank-label-width:{label_width}px;'
        f'--rank-value-width:{value_width}px">{"".join(row_markup)}</div>'
    )


def stacked_bar_list_html(rows, colors, label_width=220, value_width=44):
    """
    Builds a ranked bar list whose bars are divided into colored bands.

    The bar's length still reads as the row's volume, against the same track as
    every other list on the page; the bands divide that length by composition, so
    a row whose bands are counted twice (a posting carries several job fields)
    still measures the postings it represents.

    Args:
    rows (list of dict): Each with 'name' (str), 'value' (int), 'segments' (list
                         of {'name', 'value'} in stacking order) and optionally
                         'spark' (list of float, 0-100).
    colors (dict): Band name -> hex color.
    label_width (int): Width of the label column in pixels.
    value_width (int): Width of the value column in pixels.

    Returns:
    str: The list markup, empty when there are no rows.
    """
    if not rows:
        return ""

    largest_value = max(row["value"] for row in rows) or 1
    row_markup = []
    for row in rows:
        segments = row.get("segments", [])
        band_total = sum(segment["value"] for segment in segments) or 1
        # Hovering a band is how its exact count is read, as on the trend chart.
        bands = "".join(
            f'<span class="rank-segment" '
            f'style="width:{segment["value"] / band_total * 100:.2f}%;'
            f'background:{colors.get(segment["name"], ACCENT)}" '
            f'data-readout="{escape(str(segment["name"]))}: '
            f'{segment["value"]:,} jobs"></span>'
            for segment in segments
            if segment["value"]
        )
        row_markup.append(
            '<div class="rank-row">'
            f'<div class="rank-name" title="{escape(str(row["name"]))}">'
            f'{escape(str(row["name"]))}</div>'
            '<div class="rank-track">'
            f'<div class="rank-stack" style="width:{row["value"] / largest_value * 100:.1f}%">'
            f"{bands}</div></div>"
            f'{sparkline_svg_html(row.get("spark", []))}'
            f'<div class="rank-value">{row["value"]:,}</div>'
            "</div>"
        )
    return (
        f'<div class="rank-list rank-list-stacked" '
        f'style="--rank-label-width:{label_width}px;'
        f'--rank-value-width:{value_width}px">{"".join(row_markup)}</div>'
    )


def momentum_grid_html(segments):
    """
    Builds the per-segment month-over-month grid, three cells to a row.

    A segment too small for its percentage to mean much is marked with a dashed
    border and says so in words. It is deliberately not faded: the reader still
    has to be able to read the number they are being warned about.

    Args:
    segments (list of dict): Each with 'name', 'postings', 'change_percent'
                             (float or None) and 'is_low_volume' (bool), ordered
                             by descending volume.

    Returns:
    str: The grid markup, empty when there are no segments.
    """
    if not segments:
        return ""

    cells = []
    for segment in segments:
        arrow, label, color = _change_markup(segment["change_percent"])
        low_volume = segment["is_low_volume"]
        cells.append(
            f'<div class="momentum-cell{" low-volume" if low_volume else ""}">'
            "<div>"
            f'<div class="momentum-name" title="{escape(str(segment["name"]))}">'
            f'{escape(str(segment["name"]))}</div>'
            f'<div class="momentum-meta">{segment["postings"]:,} postings'
            f'{" · low volume" if low_volume else ""}</div>'
            "</div>"
            f'<div class="momentum-change" style="color:{color}">{arrow} {label}</div>'
            "</div>"
        )
    return f'<div class="momentum-grid">{"".join(cells)}</div>'


def panel_header_html(kicker, title, subtitle=None):
    """
    Builds a panel's kicker, heading and scope line, without the card around them.

    Panels holding a real Streamlit widget — the view switchers — cannot be built
    as one markup string, so they compose this header themselves.

    Args:
    kicker (str): Small uppercase label at the top of the panel.
    title (str): The panel heading.
    subtitle (str): Optional muted line beneath the heading.

    Returns:
    str: The header markup.
    """
    subtitle_markup = (
        f'<div class="text-muted panel-subtitle">{escape(subtitle)}</div>'
        if subtitle
        else ""
    )
    return (
        f'<div class="industry panel-header">'
        f'<div class="card-kicker">{escape(kicker)}</div>'
        f'<h4 class="card-title">{escape(title)}</h4>'
        f"{subtitle_markup}</div>"
    )


def note_html(text):
    """
    Builds a muted line inside a panel, between its header and its content.

    Args:
    text (str): The note, e.g. how the rows beneath it are ordered.

    Returns:
    str: The note markup.
    """
    return f'<div class="industry text-muted panel-subtitle">{escape(text)}</div>'


@contextmanager
def switcher_panel(container_key, state_key, options, header_html):
    """
    Opens a blueprint panel whose header carries a view switcher.

    The switcher is a real Streamlit control, so the panel cannot be built as one
    markup string. It is written first and then pinned to the card's top-right
    corner by the stylesheet, rather than sharing a column row with the header:
    a column row is laid out by Streamlit, and its height and the card's frame
    were not agreeing.

    The control is instantiated from st.session_state[state_key], so callers can
    read the chosen view — and build the header from it — before this runs.

    Args:
    container_key (str): A blueprint container key, unique on the page.
    state_key (str): The st.session_state key holding the chosen option.
    options (list of str): The switcher's options, in display order.
    header_html (str): Markup from :func:`panel_header_html`.

    Yields:
    None: The caller renders the panel's body inside the ``with`` block.
    """
    with blueprint_container(container_key):
        with st.container(key=f"panel-control-{state_key}"):
            st.segmented_control(
                state_key,
                options=options,
                key=state_key,
                label_visibility="collapsed",
            )
        render(header_html)
        yield


def panel_html(kicker, title, body_html, subtitle=None):
    """
    Builds a titled blueprint panel — the shell every chart section sits in.

    Args:
    kicker (str): Small uppercase label at the top of the panel.
    title (str): The panel heading.
    body_html (str): Already-built markup for the panel's content.
    subtitle (str): Optional muted line between the heading and the content.

    Returns:
    str: The panel markup.
    """
    return card_html(f"{panel_header_html(kicker, title, subtitle)}{body_html}")


def page_header_html(title, subtitle):
    """
    Builds the main column's page title and supporting line.

    Args:
    title (str): The screen title, e.g. "Tech hiring trends".
    subtitle (str): The line beneath it.

    Returns:
    str: The header markup.
    """
    return (
        f'<div class="industry"><h1 style="margin-bottom:0">{escape(title)}</h1>'
        f'<p class="text-muted" style="margin-bottom:var(--space-6)">'
        f"{escape(subtitle)}</p></div>"
    )


def total_matched_card_html(total_jobs, filter_summary):
    """
    Builds the sidebar's live count card.

    Args:
    total_jobs (int): Number of postings matching the active filters.
    filter_summary (str): One-line description of those filters.

    Returns:
    str: The card markup.
    """
    return card_html(
        '<div class="card-kicker">Total jobs matched</div>'
        f'<div class="total-count">{total_jobs:,}</div>'
        f'<div class="text-muted" style="font-size:12px">{escape(filter_summary)}</div>'
    )


def empty_state_html(filter_summary):
    """
    Builds the "no matching postings" card shown in place of the page's content.

    The caller renders the "Reset filters" button beneath it, since that needs to
    be a real Streamlit control.

    Args:
    filter_summary (str): One-line description of the active filters.

    Returns:
    str: The card markup.
    """
    return card_html(
        '<div class="card-kicker" style="display:flex;justify-content:center">No results</div>'
        '<h3 class="card-title" style="margin-bottom:var(--space-2)">'
        "No jobs match these filters</h3>"
        '<p class="text-muted" style="margin:0 0 var(--space-4)">'
        f"Try a longer time period, or clear a filter — {escape(filter_summary)} "
        "is a narrow combination.</p>",
        extra_style="text-align:center;padding:var(--space-8) var(--space-4)",
    )


def jobs_table_html(rows):
    """
    Builds the Latest jobs table.

    Args:
    rows (list of dict): Each with 'date', 'title', 'company', 'region',
                         'seniority', 'field' and 'url'.

    Returns:
    str: The table markup, wrapped in a horizontally scrollable blueprint card.
    """
    body_rows = []
    for row in rows:
        body_rows.append(
            "<tr>"
            f'<td class="text-muted">{escape(row["date"])}</td>'
            f'<td>{escape(row["title"])}</td>'
            f'<td>{escape(row["company"])}</td>'
            f'<td>{escape(row["region"])}</td>'
            f'<td>{escape(row["seniority"])}</td>'
            f'<td><span class="tag tag-accent">{escape(row["field"])}</span></td>'
            f'<td><a href="{escape(row["url"])}" target="_blank" rel="noopener">'
            "View job →</a></td>"
            "</tr>"
        )
    return card_html(
        '<table class="table"><thead><tr>'
        "<th>Date posted</th><th>Title</th><th>Company</th><th>Region</th>"
        "<th>Seniority</th><th>Field</th><th></th>"
        f'</tr></thead><tbody>{"".join(body_rows)}</tbody></table>',
        extra_style="overflow-x:auto",
    )


def search_range_label_html(first_index, last_index, total):
    """
    Builds the muted "X-Y of N" label beside the search box.

    Args:
    first_index (int): 1-indexed position of the first row shown.
    last_index (int): 1-indexed position of the last row shown.
    total (int): Total matching rows.

    Returns:
    str: The label markup.
    """
    return (
        '<div class="industry text-muted" '
        'style="font-size:12px;text-align:right;padding-top:12px">'
        f"{first_index:,}–{last_index:,} of {total:,}</div>"
    )


def trend_scale_html(max_label):
    """
    Builds the trend chart's minimal y-axis: a top value and a zero, no axis line.

    Args:
    max_label (int): The chart's top value.

    Returns:
    str: Markup positioning both labels over the chart area.
    """
    return (
        f'<div class="industry text-muted" style="font-size:11px;color:{MUTED_TEXT}">'
        f"{max_label:,}</div>"
    )
