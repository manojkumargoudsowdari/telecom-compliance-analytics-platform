from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DATASET_FILE_NAME = "silver_fcc_consumer_complaints.json"


def write_silver_dataset(
    output_directory: str | Path,
    records: list[dict[str, Any]],
) -> Path:
    """Write the final Silver dataset using deterministic file naming and order."""

    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    output_path = directory / DATASET_FILE_NAME

    ordered_records = sorted(records, key=lambda record: str(record["complaint_id"]))
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(ordered_records, handle, indent=2)
        handle.write("\n")

    return output_path


def write_silver_metadata(
    metadata_file_path: str | Path,
    metadata: dict[str, Any],
) -> Path:
    """Persist Silver run metadata to a deterministic metadata file path."""

    metadata_path = Path(metadata_file_path)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with metadata_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(metadata, handle, indent=2)
        handle.write("\n")
    return metadata_path


def build_silver_metadata_plan(
    *,
    config: dict[str, Any],
    source_run_id: str,
    paths: dict[str, str],
    transformation_summary: dict[str, Any] | None = None,
    validation_summary: dict[str, Any] | None = None,
    reject_summary: dict[str, Any] | None = None,
    silver_output_path: str | None = None,
    run_start_utc: str | None = None,
    run_end_utc: str | None = None,
) -> dict[str, Any]:
    """Build and optionally persist metadata for an FCC Silver run."""

    if (
        transformation_summary is None
        or validation_summary is None
        or reject_summary is None
        or run_start_utc is None
        or run_end_utc is None
    ):
        return {
            "module": "src.silver_metadata_writer",
            "status": "not_implemented",
            "source_run_id": source_run_id,
            "silver_metadata_file": paths["silver_metadata_file"],
            "config_sections": sorted(config.keys()),
        }

    metadata = {
        "source_run_id": source_run_id,
        "raw_records_read": transformation_summary["raw_records_read"],
        "candidate_valid_records_before_dedup": transformation_summary[
            "candidate_valid_records_before_dedup"
        ],
        "final_silver_record_count": transformation_summary[
            "final_deduplicated_candidate_records"
        ],
        "dedup_excluded_valid_records": transformation_summary[
            "dedup_excluded_valid_records"
        ],
        "reject_record_count": reject_summary["persisted_reject_record_count"],
        "validation_summary": validation_summary,
        "paths": {
            "raw_input_directory": paths["raw_input_directory"],
            "raw_metadata_file": paths["raw_metadata_file"],
            "silver_output_directory": paths["silver_output_directory"],
            "silver_output_file": silver_output_path,
            "silver_metadata_file": paths["silver_metadata_file"],
            "reject_output_directory": paths["reject_output_directory"],
            "reject_output_file": reject_summary["reject_output_path"],
            "quality_output_directory": paths["quality_output_directory"],
        },
        "processing_timestamps": {
            "run_start_utc": run_start_utc,
            "run_end_utc": run_end_utc,
        },
        "status": "success" if validation_summary["validation_passed"] else "failed",
    }

    metadata_path = write_silver_metadata(paths["silver_metadata_file"], metadata)

    return {
        "module": "src.silver_metadata_writer",
        "status": "metadata_written",
        "source_run_id": source_run_id,
        "silver_metadata_file": metadata_path.as_posix(),
        "config_sections": sorted(config.keys()),
        "summary": {
            "metadata_path": metadata_path.as_posix(),
            "silver_output_path": silver_output_path,
        },
    }
