"""Metric tests using deliberately small synthetic data."""

import math

import pandas as pd
import pytest

from src.metrics import calculate_kpis, pareto_frontier, provider_summary


def test_pareto_frontier_marks_undominated_accuracy_cost_points_and_keeps_ties():
    frame = pd.DataFrame(
        {
            "model_name": ["frontier-low", "frontier-mid", "frontier-tie", "dominated", "invalid"],
            "field_accuracy": [0.80, 0.85, 0.85, 0.82, None],
            "cost_usd_per_1000_documents": [4.0, 5.0, 5.0, 9.0, 1.0],
        }
    )

    result = pareto_frontier(frame)

    efficient = result.loc[result["is_pareto_efficient"], "model_name"].tolist()
    assert set(efficient) == {"frontier-low", "frontier-mid", "frontier-tie"}


def test_pareto_frontier_returns_false_when_required_columns_are_missing():
    result = pareto_frontier(pd.DataFrame({"model_name": ["only"]}))

    assert result["is_pareto_efficient"].tolist() == [False]


def test_kpis_use_medians_and_count_unique_models_and_providers():
    frame = pd.DataFrame(
        {
            "model_id": ["a", "b", "c", "c"],
            "provider": ["P1", "P1", "P2", "P2"],
            "field_accuracy": [0.8, 0.9, 1.0, 0.4],
            "cost_usd_per_1000_documents": [1.0, 3.0, 5.0, 7.0],
            "latency_p50_ms": [100, 300, 500, 700],
        }
    )

    result = calculate_kpis(frame)

    assert result["models"] == 3
    assert result["providers"] == 2
    assert result["median_cost"] == pytest.approx(4.0)
    assert result["median_latency"] == pytest.approx(400)
    assert result["median_accuracy"] == pytest.approx(0.85)


def test_kpis_handle_all_missing_metric_values():
    frame = pd.DataFrame(
        {
            "model_id": ["a"],
            "provider": ["P1"],
            "field_accuracy": [None],
            "cost_usd_per_1000_documents": [None],
            "latency_p50_ms": [None],
        }
    )

    result = calculate_kpis(frame)

    assert result["models"] == 1
    assert math.isnan(result["median_cost"])
    assert math.isnan(result["median_accuracy"])


def test_provider_summary_uses_medians_not_means():
    frame = pd.DataFrame(
        {
            "provider": ["P1", "P1", "P1"],
            "model_id": ["a", "b", "c"],
            "field_accuracy": [0.8, 0.9, 1.0],
            "cost_usd_per_1000_documents": [1.0, 2.0, 100.0],
            "latency_p50_ms": [100, 200, 5000],
        }
    )

    summary = provider_summary(frame).iloc[0]

    assert summary["Models"] == 3
    assert summary["Median accuracy"] == pytest.approx(0.9)
    assert summary["Median cost / 1k docs"] == pytest.approx(2.0)
    assert summary["Median p50 latency (ms)"] == pytest.approx(200)
