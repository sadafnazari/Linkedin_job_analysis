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
