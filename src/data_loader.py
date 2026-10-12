"""Read the last validated project snapshot from disk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.data_processing import COLUMNS, empty_models


def load_snapshot(csv_path: Path, metadata_path: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load a normalized CSV snapshot and its metadata, returning a friendly empty state on failure."""
    metadata: dict[str, Any] = {"status": "snapshot_missing", "row_count": 0}
    if metadata_path.exists():
        try:
            parsed = json.loads(metadata_path.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                metadata = parsed
        except (OSError, json.JSONDecodeError):
            metadata = {"status": "metadata_unavailable", "row_count": 0}

    if not csv_path.exists():
        return empty_models(), metadata
    try:
        frame = pd.read_csv(csv_path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError):
        return empty_models(), {**metadata, "status": "snapshot_unreadable"}

    for column in COLUMNS:
        if column not in frame:
            frame[column] = pd.NA
    return frame[COLUMNS], metadata
