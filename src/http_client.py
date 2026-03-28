from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

from src.run_id import utc_now_iso


class DownloadError(RuntimeError):
    """Raised when a source payload cannot be retrieved."""


@dataclass(frozen=True)
class DownloadResult:
    payload: bytes
    fetched_at_utc: str
    content_type: str | None
    status_code: int


@dataclass(frozen=True)
class JsonPageResult:
    records: list[dict[str, Any]]
    fetched_at_utc: str
    content_type: str | None
    status_code: int


def download_with_retries(
    source_endpoint: str,
    timeout_seconds: int,
    max_retries: int,
    retry_backoff_seconds: int,
) -> DownloadResult:
    last_exception: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(source_endpoint, timeout=timeout_seconds)
            if response.status_code >= 500:
                raise DownloadError(
                    f"Server error from source endpoint: HTTP {response.status_code}"
                )
            response.raise_for_status()
            return DownloadResult(
                payload=response.content,
                fetched_at_utc=utc_now_iso(),
                content_type=response.headers.get("Content-Type"),
                status_code=response.status_code,
            )
        except (requests.RequestException, DownloadError) as exc:
            last_exception = exc
            if attempt >= max_retries:
                break
            if retry_backoff_seconds > 0:
                time.sleep(retry_backoff_seconds)

    raise DownloadError(f"Failed to download source payload: {last_exception}")


def download_json_page_with_retries(
    source_endpoint: str,
    limit: int,
    offset: int,
    timeout_seconds: int,
    max_retries: int,
    retry_backoff_seconds: int,
) -> JsonPageResult:
    last_exception: Exception | None = None
    params = {"$limit": limit, "$offset": offset}

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                source_endpoint,
                params=params,
                timeout=timeout_seconds,
            )
            if response.status_code >= 500:
                raise DownloadError(
                    f"Server error from source endpoint: HTTP {response.status_code}"
                )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise DownloadError("Expected JSON array payload from source endpoint.")
            if any(not isinstance(record, dict) for record in payload):
                raise DownloadError(
                    "Expected each JSON array item to be an object from the source endpoint."
                )
            return JsonPageResult(
                records=payload,
                fetched_at_utc=utc_now_iso(),
                content_type=response.headers.get("Content-Type"),
                status_code=response.status_code,
            )
        except (requests.RequestException, ValueError, DownloadError) as exc:
            last_exception = exc
            if attempt >= max_retries:
                break
            if retry_backoff_seconds > 0:
                time.sleep(retry_backoff_seconds)

    raise DownloadError(f"Failed to download source payload page: {last_exception}")
