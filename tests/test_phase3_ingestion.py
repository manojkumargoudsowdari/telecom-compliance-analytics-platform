from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ingestion import fcc_raw_ingestion
from src.config_loader import ConfigError, validate_ingestion_config
from src.http_client import DownloadError, JsonPageResult, download_json_page_with_retries
from src import run_id as run_id_module


def make_config(tmp_path):
    return {
        "source": {
            "endpoint": "https://example.test/fcc.json",
            "file_format": "json",
            "pagination": {
                "enabled": True,
                "method": "limit_offset",
                "page_size": 2,
            },
        },
        "output": {
            "raw_path": str(tmp_path / "raw"),
            "raw_file_prefix": "consumer_complaints_page",
            "metadata_path": str(tmp_path / "metadata"),
        },
        "http": {
            "request_timeout_seconds": 10,
            "max_retries": 2,
            "retry_backoff_seconds": 0,
        },
        "run": {
            "id_strategy": "timestamp_utc_compact",
        },
    }


def test_run_ingestion_skips_terminal_empty_page(tmp_path, monkeypatch):
    config = make_config(tmp_path)
    offsets = []

    def fake_download_json_page_with_retries(**kwargs):
        offsets.append(kwargs["offset"])
        if kwargs["offset"] == 0:
            return JsonPageResult(
                records=[{"ticket": 1}, {"ticket": 2}],
                fetched_at_utc="2026-03-28T00:00:00Z",
                content_type="application/json",
                status_code=200,
            )
        return JsonPageResult(
            records=[],
            fetched_at_utc="2026-03-28T00:00:01Z",
            content_type="application/json",
            status_code=200,
        )

    monkeypatch.setattr(
        fcc_raw_ingestion,
        "download_json_page_with_retries",
        fake_download_json_page_with_retries,
    )

    progress_state = {}
    summary = fcc_raw_ingestion.run_ingestion(
        config,
        run_id="20260328T000000000000Z",
        progress_state=progress_state,
    )

    landed_files = list((tmp_path / "raw" / "20260328T000000000000Z").glob("*.json"))
    assert offsets == [0, 2]
    assert [path.name for path in landed_files] == ["consumer_complaints_page_000001.json"]
    assert summary["total_pages_fetched"] == 1
    assert summary["total_records_fetched"] == 2
    assert progress_state["total_pages_fetched"] == 1


def test_main_returns_clean_failure_when_metadata_write_fails(monkeypatch, capsys):
    config = {
        "source": {
            "endpoint": "https://example.test/fcc.json",
            "file_format": "json",
            "pagination": {
                "enabled": True,
                "method": "limit_offset",
                "page_size": 1,
            },
        },
        "output": {
            "raw_path": "raw",
            "raw_file_prefix": "consumer_complaints_page",
            "metadata_path": "metadata",
        },
        "http": {
            "request_timeout_seconds": 10,
            "max_retries": 1,
            "retry_backoff_seconds": 0,
        },
        "run": {
            "id_strategy": "timestamp_utc_compact",
        },
    }

    class Args:
        config = "ignored.yaml"

    monkeypatch.setattr(fcc_raw_ingestion, "parse_args", lambda argv: Args())
    monkeypatch.setattr(fcc_raw_ingestion, "load_yaml_config", lambda path: config)
    monkeypatch.setattr(fcc_raw_ingestion, "validate_ingestion_config", lambda loaded: None)
    monkeypatch.setattr(fcc_raw_ingestion, "generate_run_id", lambda: "20260328T000000000000Z")
    monkeypatch.setattr(
        fcc_raw_ingestion,
        "run_ingestion",
        lambda loaded, *, run_id, progress_state: {
            "run_id": run_id,
            "status": "success",
        },
    )
    monkeypatch.setattr(
        fcc_raw_ingestion,
        "write_run_metadata",
        lambda metadata_root, run_id, metadata: (_ for _ in ()).throw(
            OSError("metadata path unavailable")
        ),
    )

    exit_code = fcc_raw_ingestion.main([])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Failed to write run metadata" in captured.err
    assert "metadata write failed" in captured.err


def test_main_returns_clean_failure_when_error_metadata_write_fails(monkeypatch, capsys):
    config = {
        "source": {
            "endpoint": "https://example.test/fcc.json",
            "file_format": "json",
            "pagination": {
                "enabled": True,
                "method": "limit_offset",
                "page_size": 1,
            },
        },
        "output": {
            "raw_path": "raw",
            "raw_file_prefix": "consumer_complaints_page",
            "metadata_path": "metadata",
        },
        "http": {
            "request_timeout_seconds": 10,
            "max_retries": 1,
            "retry_backoff_seconds": 0,
        },
        "run": {
            "id_strategy": "timestamp_utc_compact",
        },
    }

    class Args:
        config = "ignored.yaml"

    monkeypatch.setattr(fcc_raw_ingestion, "parse_args", lambda argv: Args())
    monkeypatch.setattr(fcc_raw_ingestion, "load_yaml_config", lambda path: config)
    monkeypatch.setattr(fcc_raw_ingestion, "validate_ingestion_config", lambda loaded: None)
    monkeypatch.setattr(fcc_raw_ingestion, "generate_run_id", lambda: "20260328T000000000000Z")
    monkeypatch.setattr(
        fcc_raw_ingestion,
        "run_ingestion",
        lambda loaded, *, run_id, progress_state: (_ for _ in ()).throw(OSError("disk full")),
    )
    monkeypatch.setattr(
        fcc_raw_ingestion,
        "write_run_metadata",
        lambda metadata_root, run_id, metadata: (_ for _ in ()).throw(
            OSError("metadata path unavailable")
        ),
    )

    exit_code = fcc_raw_ingestion.main([])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Failed to write run metadata" in captured.err
    assert "Raw ingestion failed for run_id=20260328T000000000000Z: disk full." in captured.err


def test_validate_ingestion_config_requires_metadata_path(tmp_path):
    config = make_config(tmp_path)
    del config["output"]["metadata_path"]

    with pytest.raises(ConfigError, match="output.metadata_path"):
        validate_ingestion_config(config)


def test_generate_run_id_is_unique_when_clock_does_not_advance(monkeypatch):
    class FrozenDatetime:
        @staticmethod
        def now(tz):
            return datetime(2026, 3, 28, 0, 0, 0, 123456, tzinfo=UTC)

    monkeypatch.setattr(run_id_module, "datetime", FrozenDatetime)
    monkeypatch.setattr(run_id_module, "_last_run_id_timestamp", "")
    monkeypatch.setattr(run_id_module, "_last_run_id_sequence", 0)

    first_run_id = run_id_module.generate_run_id()
    second_run_id = run_id_module.generate_run_id()

    assert first_run_id == "20260328T000000123456Z"
    assert second_run_id == "20260328T000000123456Z_01"


def test_download_json_page_rejects_non_object_records(monkeypatch):
    class Response:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        @staticmethod
        def raise_for_status():
            return None

        @staticmethod
        def json():
            return ["not-an-object"]

    monkeypatch.setattr("src.http_client.requests.get", lambda *args, **kwargs: Response())

    with pytest.raises(
        DownloadError,
        match="Expected each JSON array item to be an object",
    ):
        download_json_page_with_retries(
            source_endpoint="https://example.test/fcc.json",
            limit=10,
            offset=0,
            timeout_seconds=5,
            max_retries=1,
            retry_backoff_seconds=0,
        )
