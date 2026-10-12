"""Plotly charts for ModelScope AI."""

from __future__ import annotations

import hashlib

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.theme import theme_tokens

PROVIDERS = ("Anthropic", "DeepSeek", "Google", "Mistral", "OpenAI", "Qwen", "Z.ai")


def _provider_color_map(frame: pd.DataFrame, theme: str, column: str = "provider") -> dict[str, str]:
    palette = theme_tokens(theme)["chart_colors"]
    providers = sorted(frame[column].dropna().astype(str).unique())
    return {
        provider: palette[
            (PROVIDERS.index(provider) if provider in PROVIDERS else int.from_bytes(
                hashlib.sha256(provider.encode()).digest()[:4], "big"
            )) % len(palette)
        ] for provider in providers
    }


def _style(fig: go.Figure, height: int = 380, theme: str = "Dark") -> go.Figure:
    colors = theme_tokens(theme)
    fig.update_layout(
        template=colors["plot_template"],
        height=height,
        margin=dict(l=14, r=18, t=18, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color=colors["text"], size=12),
        modebar=dict(bgcolor=colors["panel"], color=colors["muted"], activecolor=colors["accent"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=colors["muted"]),
            title=dict(font=dict(color=colors["text"])),
        ),
        hoverlabel=dict(
            bgcolor=colors["panel"],
            bordercolor=colors["border"],
            font_color=colors["text"],
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=colors["grid"],
        zeroline=False,
        linecolor=colors["border"],
        tickfont=dict(color=colors["muted"]),
        title_font=dict(color=colors["text"]),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=colors["grid"],
        zeroline=False,
        linecolor=colors["border"],
        tickfont=dict(color=colors["muted"]),
        title_font=dict(color=colors["text"]),
    )
    return fig


def accuracy_cost_chart(
    frame: pd.DataFrame, score_column: str, score_label: str, theme: str = "Dark"
) -> go.Figure:
    plot = frame.dropna(subset=[score_column, "cost_usd_per_1000_documents"]).copy()
    if "is_pareto_efficient" not in plot:
        plot["is_pareto_efficient"] = False
    plot["Frontier status"] = plot["is_pareto_efficient"].map(
        {True: "Pareto-efficient", False: "Other models"}
    )
    provider_colors = _provider_color_map(plot, theme)
    fig = px.scatter(
        plot,
        x="cost_usd_per_1000_documents",
        y=score_column,
        color="provider",
        hover_name="model_name",
        hover_data={
            "provider": True,
            score_column: ":.1%",
            "cost_usd_per_1000_documents": ":$.2f",
            "latency_p50_ms": ":,.0f",
            "latency_p90_ms": ":,.0f",
            "case_count": True,
            "top_error": True,
            "Frontier status": True,
        },
        color_discrete_map=provider_colors,
        labels={
            "cost_usd_per_1000_documents": "Cost per 1,000 documents (USD)",
            score_column: score_label,
            "provider": "Provider",
        },
    )
    fig.update_traces(
        marker=dict(size=13, opacity=0.88, line=dict(width=1, color=theme_tokens(theme)["panel"]))
    )

    frontier = plot[plot["is_pareto_efficient"]]
    if not frontier.empty:
        fig.add_trace(
            go.Scatter(
                x=frontier["cost_usd_per_1000_documents"],
                y=frontier[score_column],
                mode="markers",
                name="Pareto-efficient",
                marker=dict(
                    symbol="star",
                    size=19,
                    color=[provider_colors[str(provider)] for provider in frontier["provider"]],
                    line=dict(width=1.5, color=theme_tokens(theme)["panel"]),
                ),
                hoverinfo="skip",
            )
        )
    fig.update_yaxes(tickformat=".0%", range=[0, 1.03])
    return _style(fig, 440, theme)


def accuracy_latency_chart(
    frame: pd.DataFrame, score_column: str, score_label: str, theme: str = "Dark"
) -> go.Figure:
    plot = frame.dropna(subset=[score_column, "latency_p50_ms"]).copy()
    fig = px.scatter(
        plot,
        x="latency_p50_ms",
        y=score_column,
        color="provider",
        hover_name="model_name",
        hover_data={
            "provider": True,
            score_column: ":.1%",
            "latency_p50_ms": ":,.0f",
            "latency_p90_ms": ":,.0f",
            "cost_usd_per_1000_documents": ":$.2f",
            "case_count": True,
        },
        color_discrete_map=_provider_color_map(plot, theme),
        labels={
            "latency_p50_ms": "Median response time (ms; lower is faster)",
            score_column: score_label,
            "provider": "Provider",
        },
    )
    fig.update_traces(
        marker=dict(size=12, opacity=0.88, line=dict(width=1, color=theme_tokens(theme)["panel"]))
    )
    fig.update_yaxes(tickformat=".0%", range=[0, 1.03])
    return _style(fig, theme=theme)


def latency_distribution_chart(frame: pd.DataFrame, theme: str = "Dark") -> go.Figure:
    plot = frame.dropna(subset=["latency_p50_ms", "latency_p90_ms"]).copy()
    fig = px.scatter(
        plot,
        x="latency_p50_ms",
        y="latency_p90_ms",
        color="provider",
        hover_name="model_name",
        hover_data={"provider": True, "latency_p50_ms": ":,.0f", "latency_p90_ms": ":,.0f"},
        color_discrete_map=_provider_color_map(plot, theme),
        labels={
            "latency_p50_ms": "Median response time p50 (ms)",
            "latency_p90_ms": "Response time p90 (ms)",
            "provider": "Provider",
        },
    )
    fig.update_traces(
        marker=dict(size=11, opacity=0.85, line=dict(width=1, color=theme_tokens(theme)["panel"]))
    )
    return _style(fig, theme=theme)


def provider_cost_chart(summary: pd.DataFrame, theme: str = "Dark") -> go.Figure:
    plot = summary.dropna(subset=["Median cost / 1k docs"]).sort_values("Median cost / 1k docs")
    fig = px.bar(
        plot,
        x="Median cost / 1k docs",
        y="Provider",
        orientation="h",
        text="Median cost / 1k docs",
        color="Provider",
        color_discrete_map=_provider_color_map(plot, theme, column="Provider"),
        labels={"Median cost / 1k docs": "Median cost per 1,000 documents (USD)"},
    )
    fig.update_traces(texttemplate="$%{x:.2f}", textposition="outside", cliponaxis=False, showlegend=False)
    fig.update_yaxes(categoryorder="total ascending")
    return _style(fig, max(250, 54 * len(plot) + 80), theme)


def cost_rank_chart(frame: pd.DataFrame, top_n: int, order: str, theme: str = "Dark") -> go.Figure:
    ascending = order == "Lowest cost"
    plot = frame.dropna(subset=["cost_usd_per_1000_documents"]).sort_values(
        "cost_usd_per_1000_documents", ascending=ascending
    ).head(top_n)
    plot = plot.sort_values("cost_usd_per_1000_documents", ascending=True)
    fig = px.bar(
        plot,
        x="cost_usd_per_1000_documents",
        y="model_name",
        orientation="h",
        color="provider",
        text="cost_usd_per_1000_documents",
        color_discrete_map=_provider_color_map(plot, theme),
        hover_data={"provider": True, "field_accuracy": ":.1%", "latency_p50_ms": ":,.0f"},
        labels={
            "model_name": "Model",
            "cost_usd_per_1000_documents": "Cost per 1,000 documents (USD)",
            "provider": "Provider",
        },
    )
    fig.update_traces(texttemplate="$%{x:.2f}", textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="array", categoryarray=plot["model_name"].tolist())
    return _style(fig, max(280, 42 * len(plot) + 90), theme)
