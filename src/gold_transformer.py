from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

import ijson

UNKNOWN_ISSUE_KEY = "__UNKNOWN_ISSUE__"
UNKNOWN_METHOD_KEY = "__UNKNOWN_METHOD__"
UNKNOWN_TEXT = "__UNKNOWN__"


def _require_silver_file(silver_input_file: str | Path) -> Path:
    path = Path(silver_input_file)
    if not path.exists():
        raise ValueError(f"Silver input file does not exist: {path.as_posix()}")
    if not path.is_file():
        raise ValueError(f"Silver input path is not a file: {path.as_posix()}")
    return path


def _stream_silver_records(silver_input_file: str | Path) -> Iterable[dict[str, Any]]:
    path = _require_silver_file(silver_input_file)
    with path.open("rb") as handle:
        for record in ijson.items(handle, "item"):
            if not isinstance(record, dict):
                raise ValueError(
                    f"Silver dataset contains a non-object item: {path.as_posix()}"
                )
            yield record


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Gold build requires non-empty string field: {field_name}")
    return value


def _previous_month_key(month_key: str) -> str | None:
    year_text, month_text = month_key.split("-", maxsplit=1)
    year = int(year_text)
    month = int(month_text)
    if month == 1:
        return f"{year - 1:04d}-12"
    return f"{year:04d}-{month - 1:02d}"


def _issue_key(record: dict[str, Any]) -> str:
    issue_type = record.get("issue_type")
    issue = record.get("issue")
    if not isinstance(issue_type, str) or not issue_type.strip():
        return UNKNOWN_ISSUE_KEY
    if not isinstance(issue, str) or not issue.strip():
        return UNKNOWN_ISSUE_KEY
    return f"issue_type={issue_type}|issue={issue}"


def _method_key(record: dict[str, Any]) -> str:
    method = record.get("method")
    if not isinstance(method, str) or not method.strip():
        return "__UNKNOWN_METHOD__"
    return f"method={method}"


def _geography_key(record: dict[str, Any]) -> str:
    state = record.get("state")
    city = record.get("city")
    zip_code = record.get("zip_code")

    state_part = state if isinstance(state, str) and state.strip() else UNKNOWN_TEXT
    city_part = city if isinstance(city, str) and city.strip() else UNKNOWN_TEXT
    zip_part = zip_code if isinstance(zip_code, str) and zip_code.strip() else UNKNOWN_TEXT
    return f"state={state_part}|city={city_part}|zip_code={zip_part}"


def _daily_sort_key(record: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(record["date_key"]),
        str(record["issue_key"]),
        str(record["method_key"]),
        str(record["geography_key"]),
    )


def _monthly_sort_key(record: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(record["month_key"]),
        str(record["issue_key"]),
        str(record["method_key"]),
        str(record["geography_key"]),
    )


def _build_monthly_records(
    daily_records: list[dict[str, Any]],
    rolling_window_months: int,
) -> list[dict[str, Any]]:
    monthly_counts: dict[tuple[str, str, str, str], int] = defaultdict(int)

    for record in daily_records:
        month_key = str(record["date_key"])[:7]
        key = (
            month_key,
            str(record["issue_key"]),
            str(record["method_key"]),
            str(record["geography_key"]),
        )
        monthly_counts[key] += int(record["complaint_count"])

    partition_rows: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for (month_key, issue_key, method_key, geography_key), complaint_count in monthly_counts.items():
        partition_key = (issue_key, method_key, geography_key)
        partition_rows[partition_key].append(
            {
                "month_key": month_key,
                "issue_key": issue_key,
                "method_key": method_key,
                "geography_key": geography_key,
                "complaint_count": complaint_count,
            }
        )

    monthly_records: list[dict[str, Any]] = []
    for partition_key in sorted(partition_rows):
        ordered_partition = sorted(
            partition_rows[partition_key],
            key=lambda record: str(record["month_key"]),
        )
        month_to_count = {
            str(record["month_key"]): int(record["complaint_count"])
            for record in ordered_partition
        }
        rolling_counts: deque[int] = deque(maxlen=rolling_window_months)

        for record in ordered_partition:
            month_key = str(record["month_key"])
            complaint_count = int(record["complaint_count"])
            previous_month_key = _previous_month_key(month_key)
            previous_month_count = (
                month_to_count.get(previous_month_key)
                if previous_month_key is not None
                else None
            )

            complaint_growth_rate = None
            if previous_month_count is not None and previous_month_count != 0:
                complaint_growth_rate = (
                    complaint_count - previous_month_count
                ) / previous_month_count

            rolling_counts.append(complaint_count)
            rolling_average = sum(rolling_counts) / len(rolling_counts) if rolling_counts else None

            monthly_records.append(
                {
                    "month_key": month_key,
                    "issue_key": str(record["issue_key"]),
                    "method_key": str(record["method_key"]),
                    "geography_key": str(record["geography_key"]),
                    "complaint_count": complaint_count,
                    "complaint_growth_rate": complaint_growth_rate,
                    "rolling_average_complaint_count": rolling_average,
                }
            )

    return sorted(monthly_records, key=_monthly_sort_key)


def build_gold_transformation_plan(
    *,
    config: dict[str, Any],
    source_run_id: str,
    paths: dict[str, str],
    rolling_window_months: int,
) -> dict[str, Any]:
    """Build daily and monthly Gold facts from the validated Silver dataset."""

    silver_records_read = 0
    daily_counts: dict[tuple[str, str, str, str], int] = defaultdict(int)
    silver_issue_totals: dict[str, int] = defaultdict(int)
    silver_method_totals: dict[str, int] = defaultdict(int)
    silver_geography_totals: dict[str, int] = defaultdict(int)
    silver_month_totals: dict[str, int] = defaultdict(int)

    for record in _stream_silver_records(paths["silver_input_file"]):
        silver_records_read += 1
        date_key = _require_string(record.get("date_created"), "date_created")
        issue_key = _issue_key(record)
        method_key = _method_key(record)
        geography_key = _geography_key(record)
        daily_counts[(date_key, issue_key, method_key, geography_key)] += 1
        silver_issue_totals[issue_key] += 1
        silver_method_totals[method_key] += 1
        silver_geography_totals[geography_key] += 1
        silver_month_totals[date_key[:7]] += 1

    daily_records = [
        {
            "date_key": date_key,
            "issue_key": issue_key,
            "method_key": method_key,
            "geography_key": geography_key,
            "complaint_count": complaint_count,
        }
        for (date_key, issue_key, method_key, geography_key), complaint_count in daily_counts.items()
    ]
    daily_records.sort(key=_daily_sort_key)

    monthly_records = _build_monthly_records(daily_records, rolling_window_months)

    daily_unknown_row_counts = {
        "issue_key_unknown_rows": sum(1 for row in daily_records if row["issue_key"] == UNKNOWN_ISSUE_KEY),
        "method_key_unknown_rows": sum(
            1 for row in daily_records if row["method_key"] == UNKNOWN_METHOD_KEY
        ),
        "geography_key_unknown_rows": sum(
            1 for row in daily_records if UNKNOWN_TEXT in row["geography_key"]
        ),
    }

    return {
        "module": "src.gold_transformer",
        "status": "gold_fact_aggregation_complete",
        "source_run_id": source_run_id,
        "config_sections": sorted(config.keys()),
        "daily_records": daily_records,
        "monthly_records": monthly_records,
        "reconciliation_inputs": {
            "silver_total_count": silver_records_read,
            "silver_issue_totals": dict(sorted(silver_issue_totals.items())),
            "silver_method_totals": dict(sorted(silver_method_totals.items())),
            "silver_geography_totals": dict(sorted(silver_geography_totals.items())),
            "silver_month_totals": dict(sorted(silver_month_totals.items())),
        },
        "summary": {
            "silver_records_read": silver_records_read,
            "daily_fact_rows": len(daily_records),
            "monthly_fact_rows": len(monthly_records),
            "daily_total_complaints": sum(
                int(record["complaint_count"]) for record in daily_records
            ),
            "monthly_total_complaints": sum(
                int(record["complaint_count"]) for record in monthly_records
            ),
            "rolling_window_months": rolling_window_months,
            "unknown_member_rows": daily_unknown_row_counts,
        },
    }
