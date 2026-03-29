from __future__ import annotations

from datetime import date, datetime
from typing import Any

REQUIRED_FIELDS = (
    "complaint_id",
    "date_created",
    "source_run_id",
    "silver_processed_at_utc",
    "source_system",
)

EXPECTED_COLUMNS = (
    "source_run_id",
    "silver_processed_at_utc",
    "source_system",
    "complaint_id",
    "ticket_created_utc",
    "date_created",
    "issue_date",
    "issue_time_raw",
    "issue_type",
    "issue",
    "type_of_property_goods_or_services",
    "type_of_call_or_message",
    "method",
    "city",
    "state",
    "zip_code",
    "caller_id_number",
    "advertiser_business_phone_number",
)


def _parse_date_value(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _parse_timestamp_value(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _record_structurally_valid(record: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []

    record_columns = tuple(record.keys())
    if record_columns != EXPECTED_COLUMNS:
        failures.append("STRUCTURAL_SCHEMA_MISMATCH")

    for field_name in REQUIRED_FIELDS:
        if not _is_non_empty_string(record.get(field_name)):
            failures.append(f"MISSING_REQUIRED_FIELD:{field_name}")

    date_created = record.get("date_created")
    if date_created is None or not _is_non_empty_string(date_created) or not _parse_date_value(date_created):
        failures.append("INVALID_REQUIRED_DATE:date_created")

    silver_processed_at_utc = record.get("silver_processed_at_utc")
    if (
        silver_processed_at_utc is None
        or not _is_non_empty_string(silver_processed_at_utc)
        or not _parse_timestamp_value(silver_processed_at_utc)
    ):
        failures.append("INVALID_REQUIRED_TIMESTAMP:silver_processed_at_utc")

    ticket_created_utc = record.get("ticket_created_utc")
    if ticket_created_utc is not None and (
        not _is_non_empty_string(ticket_created_utc)
        or not _parse_timestamp_value(ticket_created_utc)
    ):
        failures.append("INVALID_OPTIONAL_TIMESTAMP:ticket_created_utc")

    issue_date = record.get("issue_date")
    if issue_date is not None and (
        not _is_non_empty_string(issue_date) or not _parse_date_value(issue_date)
    ):
        failures.append("INVALID_OPTIONAL_DATE:issue_date")

    return not failures, failures


def build_silver_validation_plan(
    *,
    config: dict[str, Any],
    source_run_id: str,
    paths: dict[str, str],
    final_candidate_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Validate deduplicated FCC Silver candidates against critical contract rules.

    This integration performs field-level and dataset-level validation aligned
    to the Phase 4 data quality rulebook. It does not persist reports or route
    records to reject storage.
    """

    critical_failures: list[str] = []
    warning_findings: list[str] = []
    informational_findings: list[str] = []

    if final_candidate_records is None:
        return {
            "module": "src.silver_validator",
            "status": "not_implemented",
            "source_run_id": source_run_id,
            "quality_output_directory": paths["quality_output_directory"],
            "config_sections": sorted(config.keys()),
        }

    if not final_candidate_records:
        critical_failures.append("DATASET_EMPTY")

    seen_complaint_ids: set[str] = set()
    duplicate_complaint_ids = 0
    invalid_record_count = 0

    for record in final_candidate_records:
        structurally_valid, record_failures = _record_structurally_valid(record)
        if not structurally_valid:
            invalid_record_count += 1
            critical_failures.extend(record_failures)

        complaint_id = record.get("complaint_id")
        if isinstance(complaint_id, str):
            if complaint_id in seen_complaint_ids:
                duplicate_complaint_ids += 1
            else:
                seen_complaint_ids.add(complaint_id)

    if duplicate_complaint_ids > 0:
        critical_failures.append("DUPLICATE_COMPLAINT_ID_IN_FINAL_DATASET")

    validation_passed = len(critical_failures) == 0

    return {
        "module": "src.silver_validator",
        "status": "validation_complete",
        "source_run_id": source_run_id,
        "quality_output_directory": paths["quality_output_directory"],
        "config_sections": sorted(config.keys()),
        "validation_passed": validation_passed,
        "summary": {
            "validation_passed": validation_passed,
            "critical_rule_failures": len(critical_failures),
            "warning_findings": len(warning_findings),
            "informational_findings": len(informational_findings),
            "invalid_final_records": invalid_record_count,
            "duplicate_complaint_ids": duplicate_complaint_ids,
            "final_candidate_records_checked": len(final_candidate_records),
            "failed_critical_checks": sorted(set(critical_failures)),
        },
    }
