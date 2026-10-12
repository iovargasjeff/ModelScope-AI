"""Regression coverage for provider identity and chart appearance."""

import pandas as pd
import plotly.graph_objects as go
import pytest

from src.charts import _provider_color_map, _style
from src.theme import theme_tokens


@pytest.mark.parametrize("mode", ["Light", "Dark"])
def test_provider_colors_do_not_change_when_other_providers_are_filtered_out(mode):
    full = pd.DataFrame({"provider": ["Anthropic", "Google", "OpenAI", "Other"]})
    subset = full[full["provider"].isin(["OpenAI", "Other"])]
    all_colors = _provider_color_map(full, mode)
    selected_colors = _provider_color_map(subset, mode)
    assert selected_colors == {name: all_colors[name] for name in selected_colors}


@pytest.mark.parametrize("mode", ["Light", "Dark"])
def test_legend_and_plot_toolbar_use_the_selected_appearance(mode):
    figure = _style(go.Figure(), theme=mode)
    colors = theme_tokens(mode)
    assert figure.layout.legend.title.font.color == colors["text"]
    assert figure.layout.modebar.color == colors["muted"]
    assert figure.layout.hoverlabel.bgcolor == colors["panel"]
