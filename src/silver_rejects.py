from __future__ import annotations

from typing import Any


def build_silver_reject_plan(
    *,
    config: dict[str, Any],
    source_run_id: str,
    paths: dict[str, str],
) -> dict[str, Any]:
    """Return a scaffold-only reject/quarantine plan for the FCC Silver layer.

    This stub marks the integration point for reject and quarantine handling
    defined in Phase 4. It does not classify, write, or route invalid records.
    """

    return {
        "module": "src.silver_rejects",
        "status": "not_implemented",
        "source_run_id": source_run_id,
        "reject_output_directory": paths["reject_output_directory"],
        "config_sections": sorted(config.keys()),
    }
