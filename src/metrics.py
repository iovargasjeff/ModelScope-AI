"""Metrics used by the dashboard."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

SCORE_LABELS = {
    "field_accuracy": "Correct fields",
    "document_accuracy": "Error-free documents",
}


def pareto_frontier(
    frame: pd.DataFrame,
    score_column: str = "field_accuracy",
    cost_column: str = "cost_usd_per_1000_documents",
) -> pd.DataFrame:
    """Mark rows not dominated by another row on accuracy (higher) and cost (lower).

    The calculation is O(n log n), and is intended to run within one task/language/level cohort.
    Exact score-cost ties remain efficient because neither strictly dominates the other.
    """
    result = frame.copy()
    result["is_pareto_efficient"] = False
    if score_column not in result or cost_column not in result or result.empty:
        return result

    score = pd.to_numeric(result[score_column], errors="coerce")
    cost = pd.to_numeric(result[cost_column], errors="coerce")
    valid = score.notna() & cost.notna() & score.map(math.isfinite) & cost.map(math.isfinite)
    candidates = result.loc[valid, [score_column, cost_column]].copy()
    if candidates.empty:
        return result

    candidates = candidates.sort_values([cost_column, score_column], ascending=[True, False], kind="mergesort")
    best_at_lower_cost = -math.inf
    efficient_indices: list[Any] = []
    for _, same_cost in candidates.groupby(cost_column, sort=True):
        best_score_at_cost = float(same_cost[score_column].max())
        if best_score_at_cost > best_at_lower_cost:
            efficient_indices.extend(same_cost.index[same_cost[score_column].eq(best_score_at_cost)].tolist())
        best_at_lower_cost = max(best_at_lower_cost, best_score_at_cost)

    result.loc[efficient_indices, "is_pareto_efficient"] = True
    return result


def calculate_kpis(frame: pd.DataFrame, score_column: str = "field_accuracy") -> dict[str, float | int]:
    """Summarize a cohort after the dashboard filters have been applied."""
    return {
        "models": int(frame["model_id"].nunique()) if "model_id" in frame else 0,
        "providers": int(frame["provider"].nunique()) if "provider" in frame else 0,
        "median_cost": float(frame["cost_usd_per_1000_documents"].median())
        if "cost_usd_per_1000_documents" in frame and frame["cost_usd_per_1000_documents"].notna().any()
        else math.nan,
        "median_latency": float(frame["latency_p50_ms"].median())
        if "latency_p50_ms" in frame and frame["latency_p50_ms"].notna().any()
        else math.nan,
        "median_accuracy": float(frame[score_column].median())
        if score_column in frame and frame[score_column].notna().any()
        else math.nan,
    }


def provider_summary(frame: pd.DataFrame, score_column: str = "field_accuracy") -> pd.DataFrame:
    """Aggregate providers with medians to limit the effect of outliers."""
    if frame.empty or "provider" not in frame:
        return pd.DataFrame(columns=["Provider", "Models", "Median accuracy", "Median cost / 1k docs", "Median p50 latency"])
    grouped = frame.groupby("provider", dropna=False).agg(
        models=("model_id", "nunique"),
        accuracy=(score_column, "median"),
        cost=("cost_usd_per_1000_documents", "median"),
        latency=("latency_p50_ms", "median"),
    )
    return (
        grouped.rename_axis("Provider")
        .rename(columns={
            "models": "Models",
            "accuracy": "Median accuracy",
            "cost": "Median cost / 1k docs",
            "latency": "Median p50 latency (ms)",
        })
        .sort_values("Median accuracy", ascending=False)
        .reset_index()
    )
