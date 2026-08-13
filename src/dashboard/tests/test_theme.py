import plotly.io as pio

import theme


class TestIndustryTemplate:
    def test_template_is_registered_as_the_default(self):
        assert pio.templates.default == theme.TEMPLATE_NAME

    def test_chart_backgrounds_are_transparent(self):
        """The chart sits inside a blueprint card, so it must not paint its own
        panel over the card's ground."""
        layout = pio.templates[theme.TEMPLATE_NAME].layout
        assert layout.paper_bgcolor == "rgba(0,0,0,0)"
        assert layout.plot_bgcolor == "rgba(0,0,0,0)"

    def test_axis_furniture_is_stripped(self):
        layout = pio.templates[theme.TEMPLATE_NAME].layout
        assert layout.xaxis.showgrid is False
        assert layout.yaxis.showgrid is False
        assert layout.showlegend is False


class TestStackPalette:
    def test_bands_that_touch_are_far_apart_on_the_ramp(self):
        """Adjacent ramp steps sitting side by side in a bar cannot be told apart,
        so the palette's order spreads them out."""
        steps = theme.STACK_RAMP_STEPS
        gaps = [abs(later - earlier) for earlier, later in zip(steps, steps[1:])]
        assert min(gaps) >= 200

    def test_the_lightest_step_is_left_out(self):
        """Step 100 all but disappears against the page background."""
        assert 100 not in theme.STACK_RAMP_STEPS

    def test_ranked_bands_cycle_rather_than_running_out(self):
        longer_than_the_palette = len(theme.STACK_PALETTE) + 1
        colors = [theme.stack_color(index) for index in range(longer_than_the_palette)]
        assert colors[-1] == colors[0]


class TestSeniorityColor:
    def test_every_designed_level_has_its_own_step(self):
        colors = {theme.seniority_color(level) for level in theme.SENIORITY_RAMP_STEPS}
        assert len(colors) == len(theme.SENIORITY_RAMP_STEPS)

    def test_colors_come_from_the_accent_ramp(self):
        for level in theme.SENIORITY_RAMP_STEPS:
            assert theme.seniority_color(level) in theme.ACCENT_RAMP.values()

    def test_unknown_level_falls_back_to_the_accent(self):
        """An unexpected seniority value should still render, not crash."""
        assert theme.seniority_color("Fellow") == theme.ACCENT
