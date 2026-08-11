# styles.py
"""The Industry stylesheet, injected into the Streamlit page.

Two layers live here:

1. The design system's own sheet, copied from ``design/prototype.html``'s token
   and component CSS — ``:root`` variables, the tonal ramps, ``.blueprint`` and
   its corner marks, and the card/button/input/table/tag classes. The markup
   built in :mod:`components` targets these classes directly, so this layer is
   kept verbatim rather than paraphrased.
2. An app layer that maps Streamlit's own widgets onto those classes. Its
   selectors use ``data-testid`` and BaseWeb ``data-baseweb`` attributes, never
   the generated ``.st-emotion-cache-*`` hashes, which change between releases.

The font faces themselves are vendored and declared in ``.streamlit/config.toml``;
this sheet only refers to the families.
"""

import streamlit as st

_DESIGN_SYSTEM_CSS = """
:root {
  --color-bg: #f2f2f3;
  --color-surface: #e9e9ea;
  --color-text: #1d1f20;
  --color-accent: #5980a6;
  --color-divider: color-mix(in srgb, #1d1f20 16%, transparent);

  --color-neutral-100: #f5f5f8;
  --color-neutral-200: #e7e7ea;
  --color-neutral-300: #d4d4d7;
  --color-neutral-400: #b7b7ba;
  --color-neutral-500: #98989b;
  --color-neutral-600: #7a7a7d;
  --color-neutral-700: #5d5d60;
  --color-neutral-800: #424244;
  --color-neutral-900: #2b2b2d;

  --color-accent-100: #eef6ff;
  --color-accent-200: #d6ebff;
  --color-accent-300: #b5d9fd;
  --color-accent-400: #94bce3;
  --color-accent-500: #749dc4;
  --color-accent-600: #597ea3;
  --color-accent-700: #416180;
  --color-accent-800: #2c455d;
  --color-accent-900: #1d2d3d;

  --font-heading: "Barlow Condensed", system-ui, sans-serif;
  --font-heading-weight: 600;
  --font-body: "Barlow", system-ui, sans-serif;

  --space-1: 3.4px;
  --space-2: 6.8px;
  --space-3: 10.2px;
  --space-4: 13.6px;
  --space-6: 20.4px;
  --space-8: 27.2px;

  --shadow-sm: 0 1px 2px color-mix(in srgb, #2b2b2d 14%, transparent);
  --shadow-md: 0 3px 10px color-mix(in srgb, #2b2b2d 16%, transparent);
}

/* — the wireframe frame every card wears — */
.blueprint {
  position: relative;
  border: 1px solid var(--color-divider);
  border-radius: 0;
}
/* The design system scopes these as `.blueprint > .corner`. Cards that hold
   Streamlit widgets cannot have the marks as direct children — Streamlit wraps
   every element — so the marks are matched wherever they sit and positioned
   against the nearest framed ancestor. */
.corner {
  position: absolute; width: 11px; height: 11px;
  color: color-mix(in srgb, var(--color-text) 55%, transparent);
}
.corner::before, .corner::after {
  content: ""; position: absolute; background: currentColor;
}
.corner::before { left: 5px; top: 0; width: 1px; height: 100%; }
.corner::after  { top: 5px; left: 0; width: 100%; height: 1px; }
.corner.tl { top: -6px; left: -6px; }
.corner.tr { top: -6px; right: -6px; }
.corner.bl { bottom: -6px; left: -6px; }
.corner.br { bottom: -6px; right: -6px; }

/* — type — */
.industry h1, .industry h2, .industry h3, .industry h4, .industry h5, .industry h6 {
  font-family: var(--font-heading); font-weight: var(--font-heading-weight);
  line-height: 1.12; letter-spacing: -0.015em; margin: 0 0 var(--space-2);
  color: var(--color-text);
}
.industry h1 { font-size: 42px; }
.industry h3 { font-size: 25px; }
.industry h4 { font-size: 20px; }
.industry h6 {
  font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase;
}
.industry p { margin: 0 0 var(--space-3); }
.text-muted { color: color-mix(in srgb, var(--color-text) 55%, transparent); }

/* — cards — */
.card {
  display: flex; flex-direction: column; gap: var(--space-2);
  padding: var(--space-3); border-radius: 0;
  background: transparent; border: 1px solid var(--color-divider);
}
.card-kicker {
  font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--color-accent);
}
.card-title {
  font-family: var(--font-heading); font-weight: var(--font-heading-weight);
  font-size: 17px; line-height: 1.2; margin: 0;
}
.card-meta {
  display: flex; align-items: center; gap: 6px; font-size: 11px;
  color: color-mix(in srgb, var(--color-text) 50%, transparent);
}
.elev-sm { box-shadow: var(--shadow-sm); }

/* — tags — */
.tag {
  display: inline-flex; align-items: center; font-size: 11px;
  letter-spacing: 0.02em; padding: 3px 10px; border-radius: 0;
}
.tag-accent { background: var(--color-accent-100); color: var(--color-accent-800); }

/* — navigation — */
.industry-nav {
  display: flex; align-items: center; gap: var(--space-4);
  padding: var(--space-3) var(--space-6);
  border-bottom: 1px solid var(--color-divider);
  background: var(--color-bg);
}
.industry-nav .nav-brand {
  font-family: var(--font-heading); font-weight: var(--font-heading-weight);
  font-size: 18px; margin-right: auto; color: var(--color-text);
}

/* — tables — */
.industry table.table { width: 100%; border-collapse: collapse; font-size: 14px; }
/* Rows are separated by hairlines only — no column rules. */
.industry table.table th, .industry table.table td { border: 0; }
.industry table.table th {
  text-align: left; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase;
  color: color-mix(in srgb, var(--color-text) 60%, transparent);
  padding: var(--space-2); border-bottom: 1px solid var(--color-divider);
  white-space: nowrap;
}
.industry table.table td {
  padding: var(--space-2);
  border-bottom: 1px solid color-mix(in srgb, var(--color-text) 8%, transparent);
  white-space: nowrap;
}
.industry table.table tbody tr:hover {
  background: color-mix(in srgb, var(--color-text) 4%, transparent);
}
.industry table.table a { color: var(--color-accent); text-decoration: none; font-size: 13px; }
.industry table.table a:hover { text-decoration: underline; }

/* — ranked bar list: label / track + fill / value — */
.rank-list { display: flex; flex-direction: column; gap: var(--space-2); }
.rank-row {
  display: grid; align-items: center; gap: var(--space-3);
  grid-template-columns: var(--rank-label-width, 120px) 1fr var(--rank-value-width, 40px);
}
.rank-name {
  font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.rank-track { height: 10px; background: var(--color-surface); }
.rank-fill { height: 100%; }
.rank-value {
  font-size: 12px; text-align: right; color: var(--color-neutral-700);
}

/* — KPI cards — */
.kpi-value {
  font-size: 22px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.kpi-momentum { font-size: 28px; }
.spark { display: flex; align-items: flex-end; gap: 2px; height: 20px; margin-top: 2px; }
.spark > span { width: 6px; display: block; }

/* — the sidebar's hero count — */
.total-count {
  font-family: var(--font-heading); font-weight: var(--font-heading-weight);
  font-size: 48px; line-height: 1; color: var(--color-text);
}

/* — trend chart's own axis labels, drawn outside Plotly — */
.trend-scale { position: relative; }
.trend-max, .trend-zero { position: absolute; left: 0; font-size: 11px; }
.trend-max { top: 0; }
.trend-zero { bottom: 0; }
.trend-months {
  display: flex; justify-content: space-between;
  font-size: 11px; color: var(--color-neutral-600); margin-top: var(--space-2);
}
"""

_STREAMLIT_MAPPING_CSS = """
/* Streamlit's own chrome is replaced by the design's nav. */
[data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

[data-testid="stAppViewContainer"] { background: var(--color-bg); }
[data-testid="stMain"] .block-container {
  max-width: 1600px;
  padding: calc(52px + var(--space-6)) var(--space-8) var(--space-8);
}

/* The nav spans the whole viewport, above the sidebar as well — Streamlit's
   sidebar sits at a high z-index, so the bar has to clear it. */
.industry-nav-wrap {
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000000;
}
[data-testid="stAppViewContainer"] > section { padding-top: 52px; }

/* Sidebar: a plain 280px rail; the blueprint cards inside supply the framing. */
[data-testid="stSidebar"] {
  width: 280px !important; min-width: 280px !important;
  background: var(--color-bg); border-right: none;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding: calc(52px + var(--space-8)) var(--space-4) var(--space-8);
  gap: var(--space-4);
}
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarHeader"] { display: none; }

/* Selects and text inputs wear .input. */
[data-baseweb="select"] > div, [data-testid="stTextInput"] input {
  background: var(--color-surface) !important;
  border: 1px solid var(--color-divider) !important;
  border-radius: 0 !important;
  font-family: var(--font-body) !important;
  font-size: 14px !important;
  color: var(--color-text) !important;
  min-height: 36px;
}
[data-baseweb="select"] > div:hover, [data-testid="stTextInput"] input:hover {
  border-color: color-mix(in srgb, var(--color-text) 45%, transparent) !important;
}
[data-baseweb="popover"] li { font-family: var(--font-body); font-size: 14px; }
[data-testid="stTextInput"] { max-width: 320px; }
[data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] p {
  font-family: var(--font-body) !important;
  font-size: 12px !important;
  color: color-mix(in srgb, var(--color-text) 70%, transparent) !important;
}

/* Containers keyed bp-* are blueprint cards holding real widgets. Their corner
   marks are written inside as absolutely positioned children. */
div[class*="st-key-bp-"] {
  position: relative;
  border: 1px solid var(--color-divider);
  border-radius: 0;
  background: transparent;
  box-shadow: var(--shadow-sm);
  padding: var(--space-3);
}
/* Streamlit positions every element container, which would anchor the corner
   marks to the little block holding them instead of to the card. */
div[class*="st-key-bp-"] .stElementContainer:has(.corner) {
  position: static !important;
}

/* Buttons: square, hairline, condensed — .btn and .btn-ghost. */
[data-testid="stButton"] button {
  border-radius: 0; border: 1px solid var(--color-divider);
  background: transparent; color: var(--color-text);
  font-family: var(--font-heading); font-weight: var(--font-heading-weight);
  font-size: 14px; padding: var(--space-2) calc(var(--space-3) * 1.2);
}
[data-testid="stButton"] button:hover {
  background: color-mix(in srgb, var(--color-text) 7%, transparent);
  color: var(--color-text); border-color: var(--color-divider);
}
[data-testid="stButton"] button:disabled { opacity: 0.45; }
div[class*="st-key-page-current"] button {
  border-color: var(--color-accent) !important; color: var(--color-accent) !important;
}
div[class*="st-key-ghost-"] button {
  border-color: transparent !important; color: var(--color-accent) !important;
  font-size: 12px; padding-inline: 0;
}
div[class*="st-key-ghost-"] button:hover {
  background: color-mix(in srgb, var(--color-accent) 10%, transparent) !important;
}

/* The Analysis / Latest jobs switcher wears .seg. */
[data-testid="stButtonGroup"] { gap: 0; border: 1px solid var(--color-divider); }
[data-testid="stButtonGroup"] button {
  border-radius: 0 !important; border: none !important;
  font-family: var(--font-heading); font-weight: var(--font-heading-weight);
  font-size: 14px; background: transparent; color: var(--color-text);
}
[data-testid="stButtonGroup"] button + button { border-left: 1px solid var(--color-divider) !important; }
[data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stButtonGroup"] button[kind="segmented_controlActive"] {
  background: var(--color-accent) !important; color: var(--color-bg) !important;
}

:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
::selection { background: color-mix(in srgb, var(--color-accent) 30%, transparent); }
"""


def apply_page_style():
    """Inject the Industry sheet. Call once, before anything else is rendered."""
    st.markdown(
        f"<style>{_DESIGN_SYSTEM_CSS}{_STREAMLIT_MAPPING_CSS}</style>",
        unsafe_allow_html=True,
    )
