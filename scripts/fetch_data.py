"""Fetch, validate, and atomically update the public ModelVerdict snapshot."""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_URL = "https://modelverdict.ai/data/leaderboards.json"
SOURCE_URL = "https://modelverdict.ai"
ATTRIBUTION = "Based on data from ModelVerdict (CC BY 4.0)"


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def fetch_payload(session: requests.Session | None = None) -> dict[str, Any]:
    client = session or requests.Session()
    response = client.get(DATA_URL, headers={"Accept": "application/json"}, timeout=45)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("The data source returned an unexpected JSON format.")
    return payload


def _existing_metadata() -> dict[str, Any]:
    path = DATA_DIR / "metadata.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def refresh_snapshot() -> dict[str, Any]:
    # Import after setting the project root so direct script invocation works from any directory.
    sys.path.insert(0, str(ROOT))
    from src.data_processing import REQUIRED_LICENSE, normalize_leaderboards

    payload = fetch_payload()
    frame = normalize_leaderboards(payload)
    if frame.empty:
        raise ValueError("The source returned no valid rows; the existing snapshot was preserved.")

    prior = _existing_metadata()
    if (
        prior.get("run_id") == payload.get("run_id")
        and (DATA_DIR / "leaderboards.json").is_file()
        and (DATA_DIR / "models.csv").is_file()
    ):
        return {**prior, "status": "unchanged"}

    metadata = {
        "source": SOURCE_URL,
        "data_url": DATA_URL,
        "license": REQUIRED_LICENSE,
        "attribution": ATTRIBUTION,
        "run_id": str(payload["run_id"]),
        "run_date": str(payload["run_date"]),
        "dataset_version": str(payload.get("dataset_version", "unknown")),
        "fetched_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "status": "healthy",
        "row_count": int(len(frame)),
        "model_count": int(frame["model_id"].nunique()),
        "provider_count": int(frame["provider"].nunique()),
        "cohort_count": int(frame[["task", "language_code", "level"]].drop_duplicates().shape[0]),
    }

    # All validation completes before any previous snapshot is replaced.
    raw_text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    csv_text = frame.to_csv(index=False, lineterminator="\n")
    metadata_text = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    _atomic_write(DATA_DIR / "leaderboards.json", raw_text)
    _atomic_write(DATA_DIR / "models.csv", csv_text)
    _atomic_write(DATA_DIR / "metadata.json", metadata_text)
    return metadata


def main() -> int:
    try:
        metadata = refresh_snapshot()
    except (requests.RequestException, ValueError, KeyError) as error:
        print(f"Data refresh failed: {error}. The last valid snapshot was left untouched.", file=sys.stderr)
        return 1
    if metadata["status"] == "unchanged":
        print(f"ModelVerdict snapshot is already current: run={metadata['run_id']}.")
    else:
        print(
            "Updated ModelVerdict snapshot: "
            f"run={metadata['run_id']} rows={metadata['row_count']} "
            f"models={metadata['model_count']} cohorts={metadata['cohort_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

