from __future__ import annotations

from typing import Any


def build_silver_transformation_plan(
    *,
    config: dict[str, Any],
    source_run_id: str,
    paths: dict[str, str],
) -> dict[str, Any]:
    """Return a scaffold-only transformation plan for the FCC Silver layer.

    This stub represents the orchestration boundary for Phase 4 raw-to-Silver
    transformation work described in the Phase 4 execution design. It does not
    read raw data or apply any transformation rules.
    """

    return {
        "module": "src.silver_transformer",
        "status": "not_implemented",
        "source_run_id": source_run_id,
        "raw_input_directory": paths["raw_input_directory"],
        "config_sections": sorted(config.keys()),
    }
