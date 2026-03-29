from __future__ import annotations

from typing import Any


def build_silver_validation_plan(
    *,
    config: dict[str, Any],
    source_run_id: str,
    paths: dict[str, str],
) -> dict[str, Any]:
    """Return a scaffold-only validation plan for the FCC Silver layer.

    This stub marks the integration point for Phase 4 Silver validation aligned
    to the data quality rulebook. It does not execute record-level or
    dataset-level validation.
    """

    return {
        "module": "src.silver_validator",
        "status": "not_implemented",
        "source_run_id": source_run_id,
        "quality_output_directory": paths["quality_output_directory"],
        "config_sections": sorted(config.keys()),
    }
