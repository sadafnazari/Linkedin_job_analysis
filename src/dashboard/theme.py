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

# Every stacked segment on the page — seniority bands, job field bands — is drawn
# from these six steps, so one legend vocabulary covers the whole dashboard.
# The steps are deliberately spread across the ramp: neighbouring steps (900 next
# to 800) are indistinguishable once they sit side by side in a bar, and step 100
# all but disappears against the page background.
STACK_RAMP_STEPS = (900, 400, 700, 200, 500, 300)
STACK_PALETTE = [ACCENT_RAMP[step] for step in STACK_RAMP_STEPS]

# A hairline on every swatch and segment boundary, so the light steps still read
# as a shape rather than dissolving into the background.
SEGMENT_OUTLINE = "rgba(29, 31, 32, 0.55)"

# Seniority levels take their step from the shared palette by level, never by
# rank, so changing a filter never repaints a level a different color. Job field
# segments are bound to rank instead — which five fields are on screen depends on
# the filters — and the legend above the bars is what names them.
SENIORITY_RAMP_STEPS = dict(
    zip(
        (
            "Mid-Senior level",
            "Entry level",
            "Associate",
            "Director",
            "Internship",
            "Executive",
        ),
        STACK_RAMP_STEPS,
    )
)

# The order seniority bands stack in, bottom first, wherever they are drawn.
SENIORITY_ORDER = tuple(SENIORITY_RAMP_STEPS)

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


def stack_color(index):
    """
    Returns the color of the nth segment of a stacked bar.

    Used where segments are ranked rather than named — the job field bands, whose
    membership changes with the filters.

    Args:
    index (int): The segment's position in the stack, 0 first.

    Returns:
    str: A hex color from the shared stack palette, cycling if the stack is
         longer than the palette.
    """
    return STACK_PALETTE[index % len(STACK_PALETTE)]


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
