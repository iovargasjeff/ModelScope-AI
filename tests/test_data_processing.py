"""Transformation tests using tiny synthetic records (never published as data)."""

import pytest

from src.data_processing import COLUMNS, normalize_leaderboards


def sample_payload(rows=None):
    return {
        "source": "https://modelverdict.ai",
        "license": "CC BY 4.0",
        "run_id": "test-run",
        "run_date": "2026-10-10",
        "dataset_version": "test",
        "leaderboards": [
            {
                "task": "invoices",
                "lang": "en",
                "level": "all",
                "bar": 0.95,
                "rows": rows
                or [
                    {
                        "model_id": "test/provider-model",
                        "model_name": "Provider Model",
                        "vendor": "Test Provider",
                        "field_accuracy": 0.97,
                        "doc_accuracy": 0.90,
                        "usd_per_1000": 2.5,
                        "latency_ms_p50": 1200,
                        "latency_ms_p90": 2400,
                        "invalid_json_rate": 0.02,
                        "n_cases": 100,
                        "passes_bar": True,
                        "top_error": "wrong_value",
                        "by_field": {"total": 0.99},
                        "errors": {"wrong_value": 3},
                    }
                ],
            }
        ],
    }


def test_normalize_flattens_cohort_and_preserves_metrics():
    frame = normalize_leaderboards(sample_payload())

    assert list(frame.columns) == COLUMNS
    assert len(frame) == 1
    row = frame.iloc[0]
    assert row["model_name"] == "Provider Model"
    assert row["provider"] == "Test Provider"
    assert row["language_code"] == "en"
    assert row["field_accuracy"] == pytest.approx(0.97)
    assert row["cost_usd_per_1000_documents"] == pytest.approx(2.5)
    assert row["passes_threshold"] is True or bool(row["passes_threshold"])
    assert '"total": 0.99' in row["by_field_json"]


def test_normalize_deduplicates_model_within_cohort_and_cleans_invalid_values():
    first = {
        "model_id": "test/repeated",
        "model_name": "Repeated Model",
        "vendor": "Provider",
        "field_accuracy": 1.4,
        "doc_accuracy": -0.1,
        "usd_per_1000": -3,
        "latency_ms_p50": 500,
        "latency_ms_p90": 900,
        "n_cases": 20,
    }
    second = {**first, "field_accuracy": 0.8, "usd_per_1000": 4.0}
    frame = normalize_leaderboards(sample_payload([first, second]))

    assert len(frame) == 1
    row = frame.iloc[0]
    assert row["field_accuracy"] == pytest.approx(0.8)
    assert row["document_accuracy"] != row["document_accuracy"]
    assert row["cost_usd_per_1000_documents"] == pytest.approx(4.0)


def test_normalize_rejects_data_without_reuse_license():
    payload = sample_payload()
    payload["license"] = "unknown"

    with pytest.raises(ValueError, match="license"):
        normalize_leaderboards(payload)


def test_normalize_rejects_empty_source_response():
    with pytest.raises(ValueError, match="no leaderboard cohorts"):
        normalize_leaderboards({"license": "CC BY 4.0", "leaderboards": []})
