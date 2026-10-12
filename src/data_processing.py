"""Data contracts and transformations for the published ModelVerdict results."""

from __future__ import annotations

import json
import math
from typing import Any

import pandas as pd

SOURCE_URL = "https://modelverdict.ai"
DATA_URL = "https://modelverdict.ai/data/leaderboards.json"
REQUIRED_LICENSE = "CC BY 4.0"

COLUMNS = [
    "model_id",
    "model_name",
    "provider",
    "task",
    "language_code",
    "level",
    "field_accuracy",
    "document_accuracy",
    "cost_usd_per_1000_documents",
    "latency_p50_ms",
    "latency_p90_ms",
    "invalid_json_rate",
    "case_count",
    "passes_threshold",
    "accuracy_threshold",
    "top_error",
    "by_field_json",
    "errors_json",
    "run_id",
    "run_date",
    "source_url",
]

NUMERIC_COLUMNS = [
    "field_accuracy",
    "document_accuracy",
    "cost_usd_per_1000_documents",
    "latency_p50_ms",
    "latency_p90_ms",
    "invalid_json_rate",
    "case_count",
    "accuracy_threshold",
]


def _safe_json(value: Any) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False, sort_keys=True)


def empty_models() -> pd.DataFrame:
    """Return an empty DataFrame with the normalized project schema."""
    return pd.DataFrame({column: pd.Series(dtype="object") for column in COLUMNS})


def normalize_leaderboards(payload: dict[str, Any]) -> pd.DataFrame:
    """Flatten a licensed ModelVerdict leaderboard JSON document into model/cohort rows."""
    if not isinstance(payload, dict):
        raise ValueError("The source response must be a JSON object.")
    if payload.get("license") != REQUIRED_LICENSE:
        raise ValueError("The source license is missing or changed; refusing to publish the data.")

    boards = payload.get("leaderboards")
    if not isinstance(boards, list) or not boards:
        raise ValueError("The source response contains no leaderboard cohorts.")

    run_id = str(payload.get("run_id") or "").strip()
    run_date = str(payload.get("run_date") or "").strip()
    if not run_id or not run_date:
        raise ValueError("The source response is missing run metadata.")

    rows: list[dict[str, Any]] = []
    for board in boards:
        if not isinstance(board, dict):
            continue
        task = str(board.get("task") or "").strip()
        language_code = str(board.get("lang") or "").strip()
        level = str(board.get("level") or "").strip()
        source_rows = board.get("rows")
        if not task or not language_code or not level or not isinstance(source_rows, list):
            continue

        for item in source_rows:
            if not isinstance(item, dict):
                continue
            model_id = str(item.get("model_id") or "").strip()
            model_name = str(item.get("model_name") or "").strip()
            if not model_id or not model_name:
                continue
            rows.append(
                {
                    "model_id": model_id,
                    "model_name": model_name,
                    "provider": str(item.get("vendor") or "Unknown").strip() or "Unknown",
                    "task": task,
                    "language_code": language_code,
                    "level": level,
                    "field_accuracy": item.get("field_accuracy"),
                    "document_accuracy": item.get("doc_accuracy"),
                    "cost_usd_per_1000_documents": item.get("usd_per_1000"),
                    "latency_p50_ms": item.get("latency_ms_p50"),
                    "latency_p90_ms": item.get("latency_ms_p90"),
                    "invalid_json_rate": item.get("invalid_json_rate"),
                    "case_count": item.get("n_cases"),
                    "passes_threshold": item.get("passes_bar"),
                    "accuracy_threshold": board.get("bar"),
                    "top_error": item.get("top_error"),
                    "by_field_json": _safe_json(item.get("by_field")),
                    "errors_json": _safe_json(item.get("errors")),
                    "run_id": run_id,
                    "run_date": run_date,
                    "source_url": SOURCE_URL,
                }
            )

    if not rows:
        raise ValueError("No usable model rows were found; the prior snapshot was preserved.")

    frame = pd.DataFrame(rows, columns=COLUMNS)
    for column in NUMERIC_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame[column] = frame[column].where(frame[column].map(lambda value: pd.isna(value) or math.isfinite(value)))

    for column in ("field_accuracy", "document_accuracy", "invalid_json_rate", "accuracy_threshold"):
        frame[column] = frame[column].where(frame[column].between(0, 1))
    for column in ("cost_usd_per_1000_documents", "latency_p50_ms", "latency_p90_ms", "case_count"):
        frame[column] = frame[column].where(frame[column] >= 0)

    frame["passes_threshold"] = frame["passes_threshold"].astype("boolean")
    frame["top_error"] = frame["top_error"].fillna("").astype(str).str.strip()
    frame = frame.drop_duplicates(["task", "language_code", "level", "model_id"], keep="last")
    return frame.reset_index(drop=True)
