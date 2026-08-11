# theme.py
"""Industry design-system tokens, and the Plotly template derived from them.

These values mirror the ``:root`` token block of the Industry design system
(`design/prototype.html` consumes the same variables). Streamlit's own chrome
reads them from ``.streamlit/config.toml`` and the injected sheet in
:mod:`styles`; all three must be changed together.

Importing this module registers the ``industry`` Plotly template and makes it
the default, so every figure built afterwards inherits the theme.
"""

import plotly.graph_objects as go
import plotly.io as pio

TEMPLATE_NAME = "industry"

BACKGROUND = "#f2f2f3"
SURFACE = "#e9e9ea"
TEXT = "#1d1f20"
ACCENT = "#5980a6"
DIVIDER = "#d0d0d1"
# --color-text at 55% opacity, flattened over BACKGROUND.
MUTED_TEXT = "#7d7e7f"

FONT_BODY = "Barlow, system-ui, sans-serif"
FONT_HEADING = "Barlow Condensed, system-ui, sans-serif"

# Tonal ramps, generated in OKLCH on a shared perceptual lightness scale, so the
# same step of either ramp carries the same visual weight.
ACCENT_RAMP = {
    100: "#eef6ff",
    200: "#d6ebff",
    300: "#b5d9fd",
    400: "#94bce3",
    500: "#749dc4",
    600: "#597ea3",
    700: "#416180",
    800: "#2c455d",
    900: "#1d2d3d",
}

NEUTRAL_RAMP = {
    100: "#f5f5f8",
    200: "#e7e7ea",
    300: "#d4d4d7",
    400: "#b7b7ba",
    500: "#98989b",
    600: "#7a7a7d",
    700: "#5d5d60",
    800: "#424244",
    900: "#2b2b2d",
}

TREND_FILL = ACCENT_RAMP[100]

# The seniority mix draws each row from a different ramp step — deliberate
# variety inside the mono palette. The step is bound to the level itself, never
# to its rank, so changing a filter never repaints a level a different color.
SENIORITY_RAMP_STEPS = {
    "Mid-Senior level": 900,
    "Entry level": 500,
    "Associate": 700,
    "Director": 400,
    "Internship": 300,
    "Executive": 800,
}

# Sentinel options that switch a filter off. They are prepended to the resource
# lists rather than stored in them, so the resource files stay a description of
# the data rather than of the UI.
ALL_REGIONS = "All regions"
ALL_FIELDS = "All fields"
ALL_LEVELS = "All levels"


def seniority_color(seniority_level):
    """
    Returns the accent-ramp color a seniority level is drawn in.

    Args:
    seniority_level (str): The seniority level, e.g. "Mid-Senior level".

    Returns:
    str: A hex color. Levels outside the design's six fall back to the base
         accent so an unexpected value still renders.
    """
    step = SENIORITY_RAMP_STEPS.get(seniority_level)
    return ACCENT_RAMP[step] if step else ACCENT


def _build_industry_template():
    """Build the Plotly template that carries the Industry tokens.

    Only the trend chart is drawn in Plotly, and the design strips it of grid,
    legend and axis furniture, so this template is deliberately bare.
    """
    return go.layout.Template(
        layout=go.Layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            colorway=[ACCENT],
            font={"family": FONT_BODY, "size": 12, "color": TEXT},
            showlegend=False,
            hoverlabel={
                "bgcolor": BACKGROUND,
                "bordercolor": DIVIDER,
                "font": {"family": FONT_BODY, "size": 12, "color": TEXT},
            },
            margin={"l": 0, "r": 0, "t": 8, "b": 0},
            xaxis={
                "showgrid": False,
                "zeroline": False,
                "showline": False,
                "ticks": "",
                "automargin": True,
                "tickfont": {
                    "family": FONT_BODY,
                    "size": 11,
                    "color": NEUTRAL_RAMP[600],
                },
            },
            yaxis={
                "showgrid": False,
                "zeroline": False,
                "showline": False,
                "ticks": "",
                "automargin": True,
                "tickfont": {"family": FONT_BODY, "size": 11, "color": MUTED_TEXT},
            },
        )
    )


pio.templates[TEMPLATE_NAME] = _build_industry_template()
pio.templates.default = TEMPLATE_NAME
