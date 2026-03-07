from __future__ import annotations

import json
from pathlib import Path


def create_run_directory(raw_output_root: str | Path, run_id: str) -> Path:
    run_directory = Path(raw_output_root) / run_id
    run_directory.mkdir(parents=True, exist_ok=True)
    return run_directory


def write_raw_payload(run_directory: str | Path, filename: str, payload: bytes) -> Path:
    target_path = Path(run_directory) / filename
    target_path.write_bytes(payload)
    return target_path


def build_page_filename(raw_file_prefix: str, page_number: int) -> str:
    return f"{raw_file_prefix}_{page_number:06d}.json"


def write_json_page(
    run_directory: str | Path,
    raw_file_prefix: str,
    page_number: int,
    records: list[dict],
) -> Path:
    filename = build_page_filename(raw_file_prefix, page_number)
    payload = json.dumps(records, ensure_ascii=False, indent=2).encode("utf-8")
    return write_raw_payload(run_directory, filename, payload)
