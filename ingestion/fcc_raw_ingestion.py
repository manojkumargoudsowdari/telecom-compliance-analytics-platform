from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from src.config_loader import (
    ConfigError,
    get_required,
    load_yaml_config,
    validate_ingestion_config,
)
from src.http_client import DownloadError, download_json_page_with_retries
from src.metadata_writer import write_run_metadata
from src.raw_landing import create_run_directory, write_json_page
from src.run_id import generate_run_id, utc_now_iso


def build_success_summary(
    run_id: str,
    source_endpoint: str,
    landing_directory: Path,
    total_pages_fetched: int,
    total_records_fetched: int,
    total_bytes_landed: int,
    fetched_at_utc: str,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "source_endpoint": source_endpoint,
        "landing_directory": str(landing_directory.as_posix()),
        "total_pages_fetched": total_pages_fetched,
        "total_records_fetched": total_records_fetched,
        "total_bytes_landed": total_bytes_landed,
        "fetched_at_utc": fetched_at_utc,
        "status": "success",
    }


def build_run_metadata(
    *,
    run_id: str,
    status: str,
    source_endpoint: str,
    landing_directory: str,
    run_start_utc: str,
    run_end_utc: str,
    total_pages_fetched: int,
    total_records_fetched: int,
    total_bytes_landed: int,
    failure_message: str | None,
    exception_type: str | None,
    current_page_number: int | None,
    current_offset: int | None,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "status": status,
        "source_endpoint": source_endpoint,
        "landing_directory": landing_directory,
        "run_start_utc": run_start_utc,
        "run_end_utc": run_end_utc,
        "total_pages_fetched": total_pages_fetched,
        "total_records_fetched": total_records_fetched,
        "total_bytes_landed": total_bytes_landed,
        "failure_message": failure_message,
        "exception_type": exception_type,
        "current_page_number": current_page_number,
        "current_offset": current_offset,
    }


def run_ingestion(
    config: dict[str, Any],
    *,
    run_id: str,
    progress_state: dict[str, Any],
) -> dict[str, Any]:
    source_endpoint = str(get_required(config, "source.endpoint")).strip()
    raw_output_path = str(get_required(config, "output.raw_path")).strip()
    raw_file_prefix = str(get_required(config, "output.raw_file_prefix")).strip()
    page_size = int(get_required(config, "source.pagination.page_size"))
    timeout_seconds = int(get_required(config, "http.request_timeout_seconds"))
    max_retries = int(get_required(config, "http.max_retries"))
    retry_backoff_seconds = int(get_required(config, "http.retry_backoff_seconds"))

    run_directory = create_run_directory(raw_output_path, run_id)
    offset = 0
    page_number = 1
    total_pages_fetched = 0
    total_records_fetched = 0
    total_bytes_landed = 0
    fetched_at_utc = ""

    while True:
        progress_state["current_page_number"] = page_number
        progress_state["current_offset"] = offset
        page = download_json_page_with_retries(
            source_endpoint=source_endpoint,
            limit=page_size,
            offset=offset,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            retry_backoff_seconds=retry_backoff_seconds,
        )
        fetched_at_utc = page.fetched_at_utc
        landed_file = write_json_page(
            run_directory=run_directory,
            raw_file_prefix=raw_file_prefix,
            page_number=page_number,
            records=page.records,
        )

        total_pages_fetched += 1
        total_records_fetched += len(page.records)
        total_bytes_landed += landed_file.stat().st_size
        progress_state["total_pages_fetched"] = total_pages_fetched
        progress_state["total_records_fetched"] = total_records_fetched
        progress_state["total_bytes_landed"] = total_bytes_landed
        print(
            (
                f"[page {page_number:06d}] "
                f"offset={offset} "
                f"records={len(page.records)} "
                f"cumulative_records={total_records_fetched} "
                f"landed={landed_file.as_posix()}"
            ),
            flush=True,
        )

        if len(page.records) < page_size:
            break

        offset += page_size
        page_number += 1

    return build_success_summary(
        run_id=run_id,
        source_endpoint=source_endpoint,
        landing_directory=run_directory,
        total_pages_fetched=total_pages_fetched,
        total_records_fetched=total_records_fetched,
        total_bytes_landed=total_bytes_landed,
        fetched_at_utc=fetched_at_utc,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch and land the FCC Consumer Complaints raw payload."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the ingestion YAML configuration file.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    run_id: str | None = None
    metadata_root: str | None = None
    progress_state: dict[str, Any] | None = None
    try:
        config = load_yaml_config(args.config)
        validate_ingestion_config(config)
        source_endpoint = str(get_required(config, "source.endpoint")).strip()
        raw_output_path = str(get_required(config, "output.raw_path")).strip()
        metadata_root = str(get_required(config, "output.metadata_path")).strip()
        run_id = generate_run_id()
        landing_directory = str((Path(raw_output_path) / run_id).as_posix())
        run_start_utc = utc_now_iso()
        progress_state = {
            "source_endpoint": source_endpoint,
            "landing_directory": landing_directory,
            "run_start_utc": run_start_utc,
            "total_pages_fetched": 0,
            "total_records_fetched": 0,
            "total_bytes_landed": 0,
            "current_page_number": None,
            "current_offset": None,
        }
        summary = run_ingestion(config, run_id=run_id, progress_state=progress_state)
        metadata = build_run_metadata(
            run_id=run_id,
            status="success",
            source_endpoint=source_endpoint,
            landing_directory=landing_directory,
            run_start_utc=run_start_utc,
            run_end_utc=utc_now_iso(),
            total_pages_fetched=progress_state["total_pages_fetched"],
            total_records_fetched=progress_state["total_records_fetched"],
            total_bytes_landed=progress_state["total_bytes_landed"],
            failure_message=None,
            exception_type=None,
            current_page_number=progress_state["current_page_number"],
            current_offset=progress_state["current_offset"],
        )
        write_run_metadata(metadata_root, run_id, metadata)
    except (ConfigError, DownloadError, OSError, ValueError) as exc:
        if run_id and metadata_root and progress_state:
            metadata = build_run_metadata(
                run_id=run_id,
                status="failed",
                source_endpoint=progress_state["source_endpoint"],
                landing_directory=progress_state["landing_directory"],
                run_start_utc=progress_state["run_start_utc"],
                run_end_utc=utc_now_iso(),
                total_pages_fetched=progress_state["total_pages_fetched"],
                total_records_fetched=progress_state["total_records_fetched"],
                total_bytes_landed=progress_state["total_bytes_landed"],
                failure_message=str(exc),
                exception_type=type(exc).__name__,
                current_page_number=progress_state["current_page_number"],
                current_offset=progress_state["current_offset"],
            )
            write_run_metadata(metadata_root, run_id, metadata)
            print(
                (
                    f"Raw ingestion failed for run_id={run_id}: {exc}. "
                    f"Partial raw files may already exist under "
                    f"{progress_state['landing_directory']}."
                ),
                file=sys.stderr,
            )
        else:
            print(f"Raw ingestion failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
