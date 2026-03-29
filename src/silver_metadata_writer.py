from __future__ import annotations

from typing import Any


def build_silver_metadata_plan(
    *,
    config: dict[str, Any],
    source_run_id: str,
    paths: dict[str, str],
) -> dict[str, Any]:
    """Return a scaffold-only metadata plan for the FCC Silver layer.

    This stub marks the metadata-writing boundary for Silver execution. It does
    not persist metadata and only exposes the expected integration point.
    """

    return {
        "module": "src.silver_metadata_writer",
        "status": "not_implemented",
        "source_run_id": source_run_id,
        "silver_metadata_file": paths["silver_metadata_file"],
        "config_sections": sorted(config.keys()),
    }
