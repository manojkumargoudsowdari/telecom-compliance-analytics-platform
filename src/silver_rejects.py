from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _canonical_raw_record_hash(raw_record: dict[str, Any]) -> str:
    canonical_payload = json.dumps(
        raw_record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()


def _primary_reason_code(reject_reasons: list[str]) -> str:
    if not reject_reasons:
        return "UNKNOWN_REJECT_REASON"
    return reject_reasons[0].split(":", maxsplit=1)[0]


def _primary_reason_description(reject_reasons: list[str]) -> str:
    if not reject_reasons:
        return "Reject reason was not provided."

    primary = _primary_reason_code(reject_reasons)
    if primary == "MISSING_REQUIRED_FIELD":
        fields = [
            reason.split(":", maxsplit=1)[1]
            for reason in reject_reasons
            if reason.startswith("MISSING_REQUIRED_FIELD:")
        ]
        if fields:
            return "Missing required field(s): " + ", ".join(sorted(fields))
        return "Missing required field."

    return "; ".join(sorted(reject_reasons))


def _persisted_reject_sort_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        str(record["source_page_file"]),
        int(record["source_record_index"]),
        str(record["reject_reason_code"]),
        str(record["raw_record_hash"]),
    )


def _build_persisted_reject_record(
    *,
    source_run_id: str,
    reject_timestamp_utc: str,
    reject_record: dict[str, Any],
) -> dict[str, Any]:
    reject_reasons = list(reject_record.get("reject_reasons", []))
    raw_record = dict(reject_record.get("raw_record", {}))

    return {
        "source_run_id": source_run_id,
        "reject_timestamp_utc": reject_timestamp_utc,
        "reject_reason_code": _primary_reason_code(reject_reasons),
        "reject_reason_description": _primary_reason_description(reject_reasons),
        "reject_reasons": sorted(reject_reasons),
        "source_page_file": str(reject_record["source_page_file"]),
        "source_record_index": int(reject_record["source_record_index"]),
        "raw_record_hash": _canonical_raw_record_hash(raw_record),
        "raw_record": raw_record,
    }


def build_silver_reject_plan(
    *,
    config: dict[str, Any],
    source_run_id: str,
    paths: dict[str, str],
    candidate_reject_records: list[dict[str, Any]] | None = None,
    reject_timestamp_utc: str | None = None,
) -> dict[str, Any]:
    """Persist reject/quarantine records for the FCC Silver transformation.

    This implementation writes a deterministic reject artifact aligned to the
    Phase 4 reject/quarantine strategy. It persists only candidate rejects and
    does not write dedup-excluded valid records.
    """

    if candidate_reject_records is None or reject_timestamp_utc is None:
        return {
            "module": "src.silver_rejects",
            "status": "not_implemented",
            "source_run_id": source_run_id,
            "reject_output_directory": paths["reject_output_directory"],
            "config_sections": sorted(config.keys()),
        }

    reject_output_directory = Path(paths["reject_output_directory"])
    reject_output_directory.mkdir(parents=True, exist_ok=True)
    reject_output_file = reject_output_directory / "candidate_reject_records.json"

    persisted_records = [
        _build_persisted_reject_record(
            source_run_id=source_run_id,
            reject_timestamp_utc=reject_timestamp_utc,
            reject_record=reject_record,
        )
        for reject_record in candidate_reject_records
    ]
    persisted_records.sort(key=_persisted_reject_sort_key)

    with reject_output_file.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(persisted_records, handle, indent=2)
        handle.write("\n")

    return {
        "module": "src.silver_rejects",
        "status": "reject_persistence_complete",
        "source_run_id": source_run_id,
        "reject_output_directory": reject_output_directory.as_posix(),
        "reject_output_file": reject_output_file.as_posix(),
        "config_sections": sorted(config.keys()),
        "summary": {
            "persisted_reject_record_count": len(persisted_records),
            "reject_output_path": reject_output_file.as_posix(),
        },
    }
