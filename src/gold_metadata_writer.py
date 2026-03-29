from __future__ import annotations

import json
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any


DAILY_DATASET_FILE_NAME = "fact_complaints_daily.json"
MONTHLY_DATASET_FILE_NAME = "fact_complaints_monthly.json"


def _reset_output_root(output_root: str | Path) -> Path:
    root = Path(output_root)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    return root


def _write_partitioned_dataset(
    output_root: str | Path,
    records: list[dict[str, Any]],
    *,
    grain: str,
    dataset_name: str,
    period_key: str,
) -> list[str]:
    root = _reset_output_root(output_root)
    partitions: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        period_value = str(record[period_key])
        year = period_value[:4]
        month = period_value[5:7]
        partitions[(year, month)].append(record)

    output_paths: list[str] = []
    for (year, month), partition_records in sorted(partitions.items()):
        partition_directory = root / f"grain={grain}" / f"year={year}" / f"month={month}"
        partition_directory.mkdir(parents=True, exist_ok=True)
        output_path = partition_directory / dataset_name
        with output_path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(partition_records, handle, indent=2)
            handle.write("\n")
        output_paths.append(output_path.as_posix())

    return output_paths


def write_gold_datasets(
    *,
    daily_output_root: str | Path,
    monthly_output_root: str | Path,
    daily_records: list[dict[str, Any]],
    monthly_records: list[dict[str, Any]],
) -> dict[str, list[str]]:
    """Persist the approved Gold fact datasets using deterministic partition paths."""

    daily_paths = _write_partitioned_dataset(
        daily_output_root,
        daily_records,
        grain="daily",
        dataset_name=DAILY_DATASET_FILE_NAME,
        period_key="date_key",
    )
    monthly_paths = _write_partitioned_dataset(
        monthly_output_root,
        monthly_records,
        grain="monthly",
        dataset_name=MONTHLY_DATASET_FILE_NAME,
        period_key="month_key",
    )
    return {
        "daily_output_files": daily_paths,
        "monthly_output_files": monthly_paths,
    }


def _write_gold_metadata(metadata_file_path: str | Path, metadata: dict[str, Any]) -> Path:
    metadata_path = Path(metadata_file_path)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with metadata_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(metadata, handle, indent=2)
        handle.write("\n")
    return metadata_path


def build_gold_metadata_plan(
    *,
    config: dict[str, Any],
    source_run_id: str,
    paths: dict[str, str],
    transformation_summary: dict[str, Any],
    validation_summary: dict[str, Any],
    output_summary: dict[str, list[str]],
    run_start_utc: str,
    run_end_utc: str,
) -> dict[str, Any]:
    """Build and persist metadata for one Gold build."""

    metadata = {
        "source_run_id": source_run_id,
        "status": "success" if validation_summary["validation_passed"] else "failed",
        "record_counts": {
            "silver_source_record_count": transformation_summary["silver_records_read"],
            "daily_fact_row_count": transformation_summary["daily_fact_rows"],
            "monthly_fact_row_count": transformation_summary["monthly_fact_rows"],
            "daily_total_complaints": transformation_summary["daily_total_complaints"],
            "monthly_total_complaints": transformation_summary["monthly_total_complaints"],
        },
        "rolling_window_months": transformation_summary["rolling_window_months"],
        "unknown_member_rows": transformation_summary["unknown_member_rows"],
        "paths": {
            "silver_input_file": paths["silver_input_file"],
            "daily_output_root": paths["daily_output_root"],
            "monthly_output_root": paths["monthly_output_root"],
            "daily_output_files": output_summary["daily_output_files"],
            "monthly_output_files": output_summary["monthly_output_files"],
            "quality_output_directory": paths["quality_output_directory"],
            "quality_output_file": validation_summary["quality_output_path"],
            "metadata_file": paths["gold_metadata_file"],
        },
        "processing_timestamps": {
            "run_start_utc": run_start_utc,
            "run_end_utc": run_end_utc,
        },
        "validation_summary": validation_summary,
        "deferred_kpis": ["category_share"],
    }
    metadata_path = _write_gold_metadata(paths["gold_metadata_file"], metadata)
    return {
        "module": "src.gold_metadata_writer",
        "status": "gold_metadata_written",
        "source_run_id": source_run_id,
        "gold_metadata_file": metadata_path.as_posix(),
        "config_sections": sorted(config.keys()),
        "summary": {
            "metadata_path": metadata_path.as_posix(),
            "daily_output_files": len(output_summary["daily_output_files"]),
            "monthly_output_files": len(output_summary["monthly_output_files"]),
        },
    }
