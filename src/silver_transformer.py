from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from src.run_id import utc_now_iso

SOURCE_SYSTEM = "fcc_consumer_complaints"
NULL_EQUIVALENT_STRINGS = {"", "none", "null"}
PLACEHOLDER_ABSENCE_STRINGS = {"none", "null"}


def _sorted_raw_page_files(raw_input_directory: str) -> list[Path]:
    directory = Path(raw_input_directory)
    if not directory.exists():
        raise ValueError(f"Raw input directory does not exist: {directory.as_posix()}")
    if not directory.is_dir():
        raise ValueError(f"Raw input path is not a directory: {directory.as_posix()}")

    page_files = sorted(directory.glob("*.json"))
    if not page_files:
        raise ValueError(f"No raw page files found under: {directory.as_posix()}")
    return page_files


def _read_page_records(page_file: Path) -> list[dict[str, Any]]:
    with page_file.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, list):
        raise ValueError(f"Raw page is not a JSON array: {page_file.as_posix()}")
    if any(not isinstance(item, dict) for item in payload):
        raise ValueError(
            f"Raw page contains non-object array items: {page_file.as_posix()}"
        )

    return payload


def _strip_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_optional_string(
    value: Any,
    *,
    uppercase: bool = False,
    allow_placeholder_absence: bool = False,
) -> str | None:
    text = _strip_string(value)
    if text is None:
        return None

    lowered = text.lower()
    if allow_placeholder_absence and lowered in PLACEHOLDER_ABSENCE_STRINGS:
        return None

    if uppercase:
        return text.upper()
    return text


def _normalize_required_string(value: Any) -> str | None:
    text = _strip_string(value)
    if text is None:
        return None
    if text.lower() in NULL_EQUIVALENT_STRINGS:
        return None
    return text


def _parse_timestamp(value: Any) -> str | None:
    text = _strip_string(value)
    if text is None or text.lower() in NULL_EQUIVALENT_STRINGS:
        return None

    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_date(value: Any) -> str | None:
    text = _strip_string(value)
    if text is None or text.lower() in NULL_EQUIVALENT_STRINGS:
        return None

    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed.date().isoformat()


def _build_candidate_record(
    *,
    raw_record: dict[str, Any],
    source_run_id: str,
    silver_processed_at_utc: str,
) -> dict[str, Any]:
    return {
        "source_run_id": source_run_id,
        "silver_processed_at_utc": silver_processed_at_utc,
        "source_system": SOURCE_SYSTEM,
        "complaint_id": _normalize_required_string(raw_record.get("id")),
        "ticket_created_utc": _parse_timestamp(raw_record.get("ticket_created")),
        "date_created": _parse_date(raw_record.get("date_created")),
        "issue_date": _parse_date(raw_record.get("issue_date")),
        "issue_time_raw": _normalize_optional_string(raw_record.get("issue_time")),
        "issue_type": _normalize_optional_string(raw_record.get("issue_type")),
        "issue": _normalize_optional_string(raw_record.get("issue")),
        "type_of_property_goods_or_services": _normalize_optional_string(
            raw_record.get("type_of_property_goods_or_services"),
            allow_placeholder_absence=True,
        ),
        "type_of_call_or_message": _normalize_optional_string(
            raw_record.get("type_of_call_or_messge"),
            allow_placeholder_absence=True,
        ),
        "method": _normalize_optional_string(raw_record.get("method")),
        "city": _normalize_optional_string(raw_record.get("city")),
        "state": _normalize_optional_string(raw_record.get("state"), uppercase=True),
        "zip_code": _normalize_optional_string(raw_record.get("zip")),
        "caller_id_number": _normalize_optional_string(
            raw_record.get("caller_id_number"),
            allow_placeholder_absence=True,
        ),
        "advertiser_business_phone_number": _normalize_optional_string(
            raw_record.get("advertiser_business_phone_number"),
            allow_placeholder_absence=True,
        ),
    }


def _required_field_failures(candidate_record: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for field_name in (
        "complaint_id",
        "date_created",
        "source_run_id",
        "silver_processed_at_utc",
        "source_system",
    ):
        if candidate_record.get(field_name) is None:
            failures.append(f"MISSING_REQUIRED_FIELD:{field_name}")
    return failures


def _build_reject_record(
    *,
    source_run_id: str,
    source_page_file: str,
    source_record_index: int,
    raw_record: dict[str, Any],
    reject_reasons: list[str],
) -> dict[str, Any]:
    return {
        "source_run_id": source_run_id,
        "source_page_file": source_page_file,
        "source_record_index": source_record_index,
        "reject_reasons": reject_reasons,
        "raw_record": raw_record,
    }


def build_silver_transformation_plan(
    *,
    config: dict[str, Any],
    source_run_id: str,
    paths: dict[str, str],
    include_records: bool = False,
) -> dict[str, Any]:
    """Map raw FCC records into candidate Silver records and reject candidates.

    This implementation performs only the structural mapping and required-field
    screening defined for the early Silver phase. It does not perform
    deduplication, dataset-level validation, or reject persistence.
    """

    page_files = _sorted_raw_page_files(paths["raw_input_directory"])
    silver_processed_at_utc = utc_now_iso()

    candidate_silver_records: list[dict[str, Any]] | None = [] if include_records else None
    candidate_reject_records: list[dict[str, Any]] | None = [] if include_records else None

    raw_records_read = 0
    candidate_valid_count = 0
    candidate_reject_count = 0

    for page_file in page_files:
        page_records = _read_page_records(page_file)
        for source_record_index, raw_record in enumerate(page_records, start=1):
            raw_records_read += 1
            candidate_record = _build_candidate_record(
                raw_record=raw_record,
                source_run_id=source_run_id,
                silver_processed_at_utc=silver_processed_at_utc,
            )
            reject_reasons = _required_field_failures(candidate_record)

            if reject_reasons:
                candidate_reject_count += 1
                if include_records and candidate_reject_records is not None:
                    candidate_reject_records.append(
                        _build_reject_record(
                            source_run_id=source_run_id,
                            source_page_file=page_file.name,
                            source_record_index=source_record_index,
                            raw_record=raw_record,
                            reject_reasons=reject_reasons,
                        )
                    )
                continue

            candidate_valid_count += 1
            if include_records and candidate_silver_records is not None:
                candidate_silver_records.append(candidate_record)

    return {
        "module": "src.silver_transformer",
        "status": "candidate_mapping_complete",
        "source_run_id": source_run_id,
        "raw_input_directory": paths["raw_input_directory"],
        "records_included_in_response": include_records,
        "candidate_silver_records": candidate_silver_records,
        "candidate_reject_records": candidate_reject_records,
        "summary": {
            "raw_page_files_read": len(page_files),
            "raw_records_read": raw_records_read,
            "candidate_valid_records": candidate_valid_count,
            "candidate_reject_records": candidate_reject_count,
            "silver_processed_at_utc": silver_processed_at_utc,
            "config_sections": sorted(config.keys()),
        },
    }
