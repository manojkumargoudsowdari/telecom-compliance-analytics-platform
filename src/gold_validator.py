from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.gold_transformer import UNKNOWN_ISSUE_KEY, UNKNOWN_METHOD_KEY, UNKNOWN_TEXT

DAILY_EXPECTED_COLUMNS = (
    "date_key",
    "issue_key",
    "method_key",
    "geography_key",
    "complaint_count",
)

MONTHLY_EXPECTED_COLUMNS = (
    "month_key",
    "issue_key",
    "method_key",
    "geography_key",
    "complaint_count",
    "complaint_growth_rate",
    "rolling_average_complaint_count",
)

VALIDATION_SUMMARY_FILE_NAME = "validation_summary.json"


def _write_validation_summary(
    quality_output_directory: str | Path,
    summary: dict[str, Any],
) -> Path:
    output_directory = Path(quality_output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / VALIDATION_SUMMARY_FILE_NAME
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    return output_path


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_daily_rows(daily_records: list[dict[str, Any]]) -> tuple[list[str], dict[str, int]]:
    failures: list[str] = []
    seen_grains: set[tuple[str, str, str, str]] = set()

    for record in daily_records:
        if tuple(record.keys()) != DAILY_EXPECTED_COLUMNS:
            failures.append("DAILY_STRUCTURAL_SCHEMA_MISMATCH")
            continue

        grain = (
            str(record["date_key"]),
            str(record["issue_key"]),
            str(record["method_key"]),
            str(record["geography_key"]),
        )
        if grain in seen_grains:
            failures.append("DAILY_GRAIN_DUPLICATE")
        else:
            seen_grains.add(grain)

        for field_name in ("date_key", "issue_key", "method_key", "geography_key"):
            if not _is_non_empty_string(record.get(field_name)):
                failures.append(f"DAILY_MISSING_REQUIRED_KEY:{field_name}")

        complaint_count = record.get("complaint_count")
        if not isinstance(complaint_count, int):
            failures.append("DAILY_INVALID_COMPLAINT_COUNT_TYPE")
        elif complaint_count <= 0:
            failures.append("DAILY_INVALID_COMPLAINT_COUNT_VALUE")

    unknown_counts = {
        "issue_key_unknown_rows": sum(
            1 for record in daily_records if record.get("issue_key") == UNKNOWN_ISSUE_KEY
        ),
        "method_key_unknown_rows": sum(
            1 for record in daily_records if record.get("method_key") == UNKNOWN_METHOD_KEY
        ),
        "geography_key_unknown_rows": sum(
            1
            for record in daily_records
            if isinstance(record.get("geography_key"), str)
            and UNKNOWN_TEXT in str(record["geography_key"])
        ),
    }
    return failures, unknown_counts


def _previous_month_key(month_key: str) -> str | None:
    year_text, month_text = month_key.split("-", maxsplit=1)
    year = int(year_text)
    month = int(month_text)
    if month == 1:
        return f"{year - 1:04d}-12"
    return f"{year:04d}-{month - 1:02d}"


def _validate_monthly_rows(
    monthly_records: list[dict[str, Any]],
    rolling_window_months: int,
) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    seen_grains: set[tuple[str, str, str, str]] = set()

    partition_rows: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for record in monthly_records:
        if tuple(record.keys()) != MONTHLY_EXPECTED_COLUMNS:
            failures.append("MONTHLY_STRUCTURAL_SCHEMA_MISMATCH")
            continue

        grain = (
            str(record["month_key"]),
            str(record["issue_key"]),
            str(record["method_key"]),
            str(record["geography_key"]),
        )
        if grain in seen_grains:
            failures.append("MONTHLY_GRAIN_DUPLICATE")
        else:
            seen_grains.add(grain)

        for field_name in ("month_key", "issue_key", "method_key", "geography_key"):
            if not _is_non_empty_string(record.get(field_name)):
                failures.append(f"MONTHLY_MISSING_REQUIRED_KEY:{field_name}")

        complaint_count = record.get("complaint_count")
        if not isinstance(complaint_count, int):
            failures.append("MONTHLY_INVALID_COMPLAINT_COUNT_TYPE")
        elif complaint_count <= 0:
            failures.append("MONTHLY_INVALID_COMPLAINT_COUNT_VALUE")

        partition_key = (
            str(record.get("issue_key")),
            str(record.get("method_key")),
            str(record.get("geography_key")),
        )
        partition_rows.setdefault(partition_key, []).append(record)

    for partition_key, rows in partition_rows.items():
        ordered_rows = sorted(rows, key=lambda row: str(row["month_key"]))
        month_to_count = {
            str(row["month_key"]): int(row["complaint_count"]) for row in ordered_rows
        }
        trailing_counts: list[int] = []
        for row in ordered_rows:
            month_key = str(row["month_key"])
            complaint_count = int(row["complaint_count"])
            previous_month_key = _previous_month_key(month_key)
            previous_month_count = (
                month_to_count.get(previous_month_key)
                if previous_month_key is not None
                else None
            )
            expected_growth = None
            if previous_month_count is not None and previous_month_count != 0:
                expected_growth = (
                    complaint_count - previous_month_count
                ) / previous_month_count

            actual_growth = row.get("complaint_growth_rate")
            if actual_growth != expected_growth:
                failures.append("MONTHLY_INVALID_COMPLAINT_GROWTH_RATE")

            trailing_counts.append(complaint_count)
            window_counts = trailing_counts[-rolling_window_months:]
            expected_rolling_average = sum(window_counts) / len(window_counts) if window_counts else None
            actual_rolling_average = row.get("rolling_average_complaint_count")
            if actual_rolling_average != expected_rolling_average:
                failures.append("MONTHLY_INVALID_ROLLING_AVERAGE")

            if previous_month_count is None and actual_growth is not None:
                failures.append("MONTHLY_GROWTH_RATE_SHOULD_BE_NULL_WITHOUT_PREVIOUS_PERIOD")
            if previous_month_count == 0 and actual_growth is not None:
                failures.append("MONTHLY_GROWTH_RATE_SHOULD_BE_NULL_FOR_ZERO_DENOMINATOR")

    return failures, warnings


def build_gold_validation_plan(
    *,
    config: dict[str, Any],
    source_run_id: str,
    paths: dict[str, str],
    daily_records: list[dict[str, Any]],
    monthly_records: list[dict[str, Any]],
    transformation_summary: dict[str, Any],
    reconciliation_inputs: dict[str, Any],
) -> dict[str, Any]:
    """Validate Gold facts and persist a deterministic validation summary."""

    critical_failures: list[str] = []
    warning_findings: list[str] = []
    informational_findings: list[str] = []

    daily_failures, unknown_counts = _validate_daily_rows(daily_records)
    critical_failures.extend(daily_failures)

    rolling_window_months = int(transformation_summary["rolling_window_months"])
    if rolling_window_months <= 0:
        critical_failures.append("MISSING_OR_INVALID_ROLLING_WINDOW_METADATA")

    monthly_failures, monthly_warnings = _validate_monthly_rows(
        monthly_records,
        rolling_window_months,
    )
    critical_failures.extend(monthly_failures)
    warning_findings.extend(monthly_warnings)

    daily_total = sum(int(record["complaint_count"]) for record in daily_records)
    monthly_total = sum(int(record["complaint_count"]) for record in monthly_records)
    silver_total = int(reconciliation_inputs["silver_total_count"])

    if daily_total != silver_total:
        critical_failures.append("SILVER_TO_DAILY_RECONCILIATION_FAILURE")
    if monthly_total != daily_total:
        critical_failures.append("DAILY_TO_MONTHLY_RECONCILIATION_FAILURE")

    silver_issue_totals = reconciliation_inputs["silver_issue_totals"]
    daily_issue_totals: dict[str, int] = {}
    for record in daily_records:
        issue_key = str(record["issue_key"])
        daily_issue_totals[issue_key] = daily_issue_totals.get(issue_key, 0) + int(
            record["complaint_count"]
        )
    if daily_issue_totals != silver_issue_totals:
        critical_failures.append("FILTERED_CONTEXT_RECONCILIATION_FAILURE:issue")

    silver_method_totals = reconciliation_inputs["silver_method_totals"]
    daily_method_totals: dict[str, int] = {}
    for record in daily_records:
        method_key = str(record["method_key"])
        daily_method_totals[method_key] = daily_method_totals.get(method_key, 0) + int(
            record["complaint_count"]
        )
    if daily_method_totals != silver_method_totals:
        critical_failures.append("FILTERED_CONTEXT_RECONCILIATION_FAILURE:method")

    silver_geography_totals = reconciliation_inputs["silver_geography_totals"]
    daily_geography_totals: dict[str, int] = {}
    for record in daily_records:
        geography_key = str(record["geography_key"])
        daily_geography_totals[geography_key] = daily_geography_totals.get(
            geography_key, 0
        ) + int(record["complaint_count"])
    if daily_geography_totals != silver_geography_totals:
        critical_failures.append("FILTERED_CONTEXT_RECONCILIATION_FAILURE:geography")

    daily_month_totals: dict[str, int] = {}
    for record in daily_records:
        month_key = str(record["date_key"])[:7]
        daily_month_totals[month_key] = daily_month_totals.get(month_key, 0) + int(
            record["complaint_count"]
        )
    monthly_month_totals: dict[str, int] = {}
    for record in monthly_records:
        month_key = str(record["month_key"])
        monthly_month_totals[month_key] = monthly_month_totals.get(month_key, 0) + int(
            record["complaint_count"]
        )
    if monthly_month_totals != daily_month_totals:
        critical_failures.append("FILTERED_CONTEXT_RECONCILIATION_FAILURE:month")

    if any(count > 0 for count in unknown_counts.values()):
        informational_findings.extend(
            [
                f"UNKNOWN_MEMBER_ROWS:{dimension}:{count}"
                for dimension, count in sorted(unknown_counts.items())
                if count > 0
            ]
        )

    validation_passed = len(critical_failures) == 0
    summary = {
        "validation_passed": validation_passed,
        "critical_rule_failures": len(critical_failures),
        "warning_findings": len(warning_findings),
        "informational_findings": len(informational_findings),
        "failed_critical_checks": sorted(set(critical_failures)),
        "record_counts": {
            "silver_source_record_count": silver_total,
            "daily_fact_row_count": len(daily_records),
            "monthly_fact_row_count": len(monthly_records),
            "daily_total_complaints": daily_total,
            "monthly_total_complaints": monthly_total,
        },
        "reconciliation_summary": {
            "silver_to_daily_reconciled": daily_total == silver_total,
            "daily_to_monthly_reconciled": monthly_total == daily_total,
            "filtered_context_reconciliation": {
                "issue": daily_issue_totals == silver_issue_totals,
                "method": daily_method_totals == silver_method_totals,
                "geography": daily_geography_totals == silver_geography_totals,
                "month": monthly_month_totals == daily_month_totals,
            },
        },
        "unknown_member_row_counts": unknown_counts,
        "rolling_window_months": rolling_window_months,
        "deferred_kpis": ["category_share"],
    }
    output_path = _write_validation_summary(paths["quality_output_directory"], summary)
    summary["quality_output_path"] = output_path.as_posix()

    return {
        "module": "src.gold_validator",
        "status": "gold_validation_complete",
        "source_run_id": source_run_id,
        "quality_output_file": output_path.as_posix(),
        "config_sections": sorted(config.keys()),
        "summary": summary,
    }
