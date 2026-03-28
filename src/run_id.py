from __future__ import annotations

from datetime import UTC, datetime

_last_run_id_timestamp = ""
_last_run_id_sequence = 0


def generate_run_id() -> str:
    """Return a compact UTC run identifier for one ingestion execution."""
    global _last_run_id_sequence
    global _last_run_id_timestamp

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    if timestamp == _last_run_id_timestamp:
        _last_run_id_sequence += 1
    else:
        _last_run_id_timestamp = timestamp
        _last_run_id_sequence = 0

    if _last_run_id_sequence == 0:
        return timestamp
    return f"{timestamp}_{_last_run_id_sequence:02d}"


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
