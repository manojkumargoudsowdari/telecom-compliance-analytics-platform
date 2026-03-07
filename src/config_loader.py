from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised when ingestion configuration is missing or invalid."""


def load_yaml_config(config_path: str | Path) -> dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        raise ConfigError(f"Configuration file does not exist: {path}")

    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    if not isinstance(config, dict):
        raise ConfigError("Configuration root must be a mapping.")

    return config


def get_required(config: dict[str, Any], dotted_key: str) -> Any:
    value: Any = config
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            raise ConfigError(f"Missing required configuration key: {dotted_key}")
        value = value[part]

    if isinstance(value, str) and not value.strip():
        raise ConfigError(f"Configuration key cannot be blank: {dotted_key}")

    return value


def get_optional(config: dict[str, Any], dotted_key: str, default: Any = None) -> Any:
    value: Any = config
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def validate_ingestion_config(config: dict[str, Any]) -> None:
    get_required(config, "source.endpoint")
    file_format = str(get_required(config, "source.file_format")).lower()
    pagination_enabled = get_required(config, "source.pagination.enabled")
    pagination_method = str(get_required(config, "source.pagination.method")).lower()
    page_size = int(get_required(config, "source.pagination.page_size"))
    get_required(config, "output.raw_path")
    get_required(config, "output.raw_file_prefix")
    get_required(config, "http.request_timeout_seconds")
    get_required(config, "http.max_retries")
    get_required(config, "http.retry_backoff_seconds")
    get_required(config, "run.id_strategy")

    if file_format != "json":
        raise ConfigError("Unsupported source.file_format. Expected: json.")
    if pagination_enabled is not True:
        raise ConfigError("source.pagination.enabled must be true for this pipeline.")
    if pagination_method != "limit_offset":
        raise ConfigError(
            "Unsupported source.pagination.method. Expected: limit_offset."
        )
    if page_size <= 0:
        raise ConfigError("source.pagination.page_size must be greater than zero.")

    timeout_seconds = int(get_required(config, "http.request_timeout_seconds"))
    max_retries = int(get_required(config, "http.max_retries"))
    retry_backoff_seconds = int(get_required(config, "http.retry_backoff_seconds"))

    if timeout_seconds <= 0:
        raise ConfigError("http.request_timeout_seconds must be greater than zero.")
    if max_retries < 1:
        raise ConfigError("http.max_retries must be at least 1.")
    if retry_backoff_seconds < 0:
        raise ConfigError("http.retry_backoff_seconds must be zero or greater.")
