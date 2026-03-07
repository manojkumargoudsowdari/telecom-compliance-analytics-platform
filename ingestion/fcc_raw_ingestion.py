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
from src.raw_landing import create_run_directory, write_json_page
from src.run_id import generate_run_id


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


def run_ingestion(
    config: dict[str, Any],
    *,
    run_id: str,
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
    run_directory: str | None = None
    try:
        config = load_yaml_config(args.config)
        validate_ingestion_config(config)
        raw_output_path = str(get_required(config, "output.raw_path")).strip()
        run_id = generate_run_id()
        run_directory = str((Path(raw_output_path) / run_id).as_posix())
        summary = run_ingestion(config, run_id=run_id)
    except (ConfigError, DownloadError, OSError, ValueError) as exc:
        if run_id and run_directory:
            print(
                (
                    f"Raw ingestion failed for run_id={run_id}: {exc}. "
                    f"Partial raw files may already exist under {run_directory}."
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
