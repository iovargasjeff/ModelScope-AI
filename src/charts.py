"""Plotly charts for ModelScope AI."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PALETTE = ["#75A7FF", "#56D6B1", "#F5C451", "#AA8BFF", "#53C5D9", "#F28E6B", "#E879B9", "#96C36B"]


def _style(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=14, r=18, t=18, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#CDD6E5", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#141C2A", bordercolor="#2D3A50", font_color="#F1F5F9"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.10)", zeroline=False, linecolor="rgba(148,163,184,0.16)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.10)", zeroline=False, linecolor="rgba(148,163,184,0.16)")
    return fig


def accuracy_cost_chart(frame: pd.DataFrame, score_column: str, score_label: str) -> go.Figure:
    plot = frame.dropna(subset=[score_column, "cost_usd_per_1000_documents"]).copy()
    if "is_pareto_efficient" not in plot:
        plot["is_pareto_efficient"] = False
    plot["Frontier status"] = plot["is_pareto_efficient"].map(
        {True: "Pareto-efficient", False: "Other models"}
    )
    providers = sorted(plot["provider"].fillna("Unknown").astype(str).unique())
    provider_colors = {provider: PALETTE[index % len(PALETTE)] for index, provider in enumerate(providers)}
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
    fig.update_traces(marker=dict(size=13, opacity=0.88, line=dict(width=1, color="rgba(255,255,255,0.55)")))

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
                    line=dict(width=1.5, color="#F8FAFC"),
                ),
                hoverinfo="skip",
            )
        )
    fig.update_yaxes(tickformat=".0%", range=[0, 1.03])
    return _style(fig, 440)

def accuracy_latency_chart(frame: pd.DataFrame, score_column: str, score_label: str) -> go.Figure:
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
        color_discrete_sequence=PALETTE,
        labels={
            "latency_p50_ms": "Median response time (ms; lower is faster)",
            score_column: score_label,
            "provider": "Provider",
        },
    )
    fig.update_traces(marker=dict(size=12, opacity=0.88, line=dict(width=1, color="rgba(255,255,255,0.55)")))
    fig.update_yaxes(tickformat=".0%", range=[0, 1.03])
    return _style(fig)


def latency_distribution_chart(frame: pd.DataFrame) -> go.Figure:
    plot = frame.dropna(subset=["latency_p50_ms", "latency_p90_ms"]).copy()
    fig = px.scatter(
        plot,
        x="latency_p50_ms",
        y="latency_p90_ms",
        color="provider",
        hover_name="model_name",
        hover_data={"provider": True, "latency_p50_ms": ":,.0f", "latency_p90_ms": ":,.0f"},
        color_discrete_sequence=PALETTE,
        labels={
            "latency_p50_ms": "Median response time p50 (ms)",
            "latency_p90_ms": "Response time p90 (ms)",
            "provider": "Provider",
        },
    )
    fig.update_traces(marker=dict(size=11, opacity=0.85, line=dict(width=1, color="rgba(255,255,255,0.55)")))
    return _style(fig)


def provider_cost_chart(summary: pd.DataFrame) -> go.Figure:
    plot = summary.dropna(subset=["Median cost / 1k docs"]).sort_values("Median cost / 1k docs")
    fig = px.bar(
        plot,
        x="Median cost / 1k docs",
        y="Provider",
        orientation="h",
        text="Median cost / 1k docs",
        color="Provider",
        color_discrete_sequence=PALETTE,
        labels={"Median cost / 1k docs": "Median cost per 1,000 documents (USD)"},
    )
    fig.update_traces(texttemplate="$%{x:.2f}", textposition="outside", cliponaxis=False, showlegend=False)
    fig.update_yaxes(categoryorder="total ascending")
    return _style(fig, max(250, 54 * len(plot) + 80))


def cost_rank_chart(frame: pd.DataFrame, top_n: int, order: str) -> go.Figure:
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
        color_discrete_sequence=PALETTE,
        hover_data={"provider": True, "field_accuracy": ":.1%", "latency_p50_ms": ":,.0f"},
        labels={
            "model_name": "Model",
            "cost_usd_per_1000_documents": "Cost per 1,000 documents (USD)",
            "provider": "Provider",
        },
    )
    fig.update_traces(texttemplate="$%{x:.2f}", textposition="outside", cliponaxis=False)
    fig.update_yaxes(categoryorder="array", categoryarray=plot["model_name"].tolist())
    return _style(fig, max(280, 42 * len(plot) + 90))
