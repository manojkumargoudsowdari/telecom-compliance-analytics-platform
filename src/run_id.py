from __future__ import annotations

from datetime import UTC, datetime


def generate_run_id() -> str:
    """Return a compact UTC run identifier for one ingestion execution."""
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
