# Phase 3 FCC Raw Ingestion Documentation

## Purpose

This document records the implemented Phase 3 raw-layer ingestion for the
FCC Consumer Complaints dataset in the
`telecom-compliance-analytics-platform` repository.

It is based strictly on the committed implementation, committed tests,
and committed evidence under `docs/evidence/phase3/`.

## Traceability

- Jira Ticket ID: `TCAP-4`
- Phase: `Phase 3 - Data Ingestion (Raw Layer Implementation)`
- Status: `Implemented and validated`
- Primary entrypoint: `ingestion/fcc_raw_ingestion.py`
- Evidence root: `docs/evidence/phase3/outputs/`

## 1. Source Understanding

### FCC Dataset

The Phase 3 ingestion pulls the FCC Consumer Complaints dataset from the
public FCC open data platform. The source contract is documented in
`docs/source_contracts/fcc_consumer_complaints_source.md`.

Observed production endpoint:

- `https://opendata.fcc.gov/resource/3xyp-aqkj.json`

Observed characteristics from the implementation:

- provider: `Federal Communications Commission (FCC)`
- access pattern: `public HTTPS API`
- authentication: `none`
- format consumed by the pipeline: `JSON`

### API Type

The implementation uses the Socrata JSON API:

- config template points to a Socrata resource endpoint
- `src/http_client.py` issues `requests.get(..., params={"$limit": ..., "$offset": ...})`
- `download_json_page_with_retries()` expects a JSON array response

### Pagination Method

Phase 3 uses `$limit + $offset` paging:

- `$limit` is the configured page size
- `$offset` is incremented by page size after every full page
- the pipeline stops when a page returns fewer rows than the configured
  page size, or when the next page is empty

### Dataset Size Observed During Execution

The committed execution evidence in
`docs/evidence/phase3/outputs/03-fcc-ingestion-run.txt` and
`docs/evidence/phase3/outputs/04-metadata-verification.txt` shows the
observed full-snapshot result:

- `total_records_fetched = 3,459,080`
- `total_pages_fetched = 70`
- `page_size = 50,000`
- final page record count = `9,080`
- `total_bytes_landed = 2,355,265,931`

The observed run ID for the validation execution was:

- `20260328T214636092984Z`

## 2. Ingestion Configuration

### YAML Config Structure

The checked-in template is `configs/fcc_ingestion.template.yaml`.

It contains these top-level sections:

- `environment`
- `source`
- `output`
- `run`
- `http`
- `overrides`

Observed values in the committed template:

```yaml
environment:
  name: local

source:
  endpoint: https://opendata.fcc.gov/resource/3xyp-aqkj.json
  file_format: json
  pagination:
    enabled: true
    method: limit_offset
    page_size: 50000

output:
  raw_path: data/raw/fcc/consumer_complaints
  raw_file_prefix: consumer_complaints_page
  metadata_path: data/raw/fcc/_metadata

run:
  mode: full
  id_strategy: timestamp_utc_compact
  timestamp_format: iso_8601_utc

http:
  request_timeout_seconds: 120
  max_retries: 3
  retry_backoff_seconds: 5

overrides:
  enabled: true
```

### How Config Drives Execution

The pipeline reads configuration through `src/config_loader.py`:

- `load_yaml_config()` reads and parses YAML
- `get_required()` resolves dotted keys
- `validate_ingestion_config()` enforces required keys and value rules

The runtime in `ingestion/fcc_raw_ingestion.py` pulls these values from
config at execution time:

- source endpoint
- raw output path
- raw file prefix
- metadata output path
- page size
- request timeout
- retry count
- retry backoff

This means the ingestion path is config-driven rather than hard-coded.

## 3. Raw Layer Architecture

### Directory Structure

The raw-layer landing paths implemented in Phase 3 are:

- raw payload root: `data/raw/fcc/consumer_complaints/`
- metadata root: `data/raw/fcc/_metadata/`

Per run, the runtime layout is:

```text
data/
  raw/
    fcc/
      consumer_complaints/
        {run_id}/
          consumer_complaints_page_000001.json
          consumer_complaints_page_000002.json
          ...
      _metadata/
        {run_id}.json
```

### Naming Conventions

Implemented naming rules:

- run directory: `{run_id}`
- metadata file: `{run_id}.json`
- raw page file:
  `consumer_complaints_page_{page_number:06d}.json`

Observed example from validation evidence:

- run directory:
  `data/raw/fcc/consumer_complaints/20260328T214636092984Z/`
- metadata file:
  `data/raw/fcc/_metadata/20260328T214636092984Z.json`
- first page:
  `consumer_complaints_page_000001.json`
- last page:
  `consumer_complaints_page_000070.json`

### Design Decisions

Phase 3 implements these raw-layer design decisions:

- `run_id` is generated per execution in UTC
- each run lands into a distinct directory
- metadata is physically separated from raw files
- raw landing is append-only by run
- reruns create new run directories instead of overwriting older runs

`src/run_id.py` uses a compact UTC timestamp with microseconds and a
same-instant collision suffix when needed.

## 4. Ingestion Pipeline Design

### Modules Involved

The implemented Phase 3 pipeline is split across these modules:

- `ingestion/fcc_raw_ingestion.py`
  Main entrypoint, ingestion loop, summary construction, failure
  handling, and metadata orchestration
- `src/config_loader.py`
  YAML loading and validation
- `src/http_client.py`
  HTTP retrieval and retry logic
- `src/raw_landing.py`
  Run directory creation and raw page writes
- `src/metadata_writer.py`
  Metadata persistence
- `src/run_id.py`
  Run ID generation and UTC timestamp helpers

### Flow of Execution

The actual execution flow is:

1. Parse `--config`
2. Load YAML configuration
3. Validate required keys and allowed values
4. Generate a unique `run_id`
5. Initialize progress state
6. Create the raw run directory
7. Repeatedly download one page with retries
8. Write one raw JSON file for each non-empty page
9. Track cumulative page, record, and byte counts
10. Print per-page progress logs
11. Stop at the final page
12. Build a success summary
13. Write run metadata
14. Return success JSON to stdout

If an exception occurs, the pipeline attempts to write failure metadata
and returns exit code `1`.

### Pagination Loop Logic

The pagination loop is implemented in `run_ingestion()`:

- initialize `offset = 0`
- initialize `page_number = 1`
- request the current page
- stop immediately if the page is empty
- land the page if it contains records
- update cumulative counters
- stop if `len(page.records) < page_size`
- otherwise increment:
  - `offset += page_size`
  - `page_number += 1`

This is the hardened behavior that prevents landing a terminal empty page
file.

## 5. Pagination Strategy

### How `limit/offset` Works

The HTTP client sends:

- `$limit = page_size`
- `$offset = current offset`

With the committed config, the observed request sequence was:

- page 1: offset `0`, limit `50000`
- page 2: offset `50000`, limit `50000`
- ...
- page 70: offset `3450000`, limit `50000`

### Stop Condition

The pipeline uses two stop conditions:

- if a page returns `0` records, break before landing a file
- if a page returns fewer than `page_size` records, land it and then
  stop

### Final-Page Behavior

Observed final-page behavior from committed evidence:

- last landed page:
  `consumer_complaints_page_000070.json`
- records in final page: `9,080`
- expected next page file:
  `consumer_complaints_page_000071.json`
- presence of next page file: `False`
- empty page files: `NONE`

This is confirmed in
`docs/evidence/phase3/outputs/05-raw-page-verification.txt`.

## 6. Metadata System

### Metadata Schema

The metadata object is constructed in
`ingestion/fcc_raw_ingestion.py::build_run_metadata()`.

Committed fields:

- `run_id`
- `status`
- `source_endpoint`
- `landing_directory`
- `run_start_utc`
- `run_end_utc`
- `total_pages_fetched`
- `total_records_fetched`
- `total_bytes_landed`
- `failure_message`
- `exception_type`
- `current_page_number`
- `current_offset`

### Fields Captured

The metadata captures:

- execution identity
- source lineage
- output lineage
- execution timing
- volume metrics
- partial progress position
- failure details when applicable

### Purpose

The metadata system supports:

- lineage
- auditability
- run reconciliation
- failure diagnosis
- downstream run selection

The committed metadata verification evidence confirms a successful run
record with `status = success` and null failure fields.

## 7. Observability

### Logging Format

The ingestion loop prints one progress line per landed page:

```text
[page 000001] offset=0 records=50000 cumulative_records=50000 landed=data/raw/fcc/consumer_complaints/{run_id}/consumer_complaints_page_000001.json
```

This format is visible in
`docs/evidence/phase3/outputs/03-fcc-ingestion-run.txt`.

### What Is Tracked

Observed per-page tracking:

- page number
- offset
- records landed in the page
- cumulative record count
- raw file path

Observed run-level tracking:

- total pages fetched
- total records fetched
- total bytes landed
- run start and end timestamps
- current page number and offset
- success or failure status

## 8. Repo Hygiene Fix

### Problem Encountered

Before Phase 3 closeout, raw FCC payload files had been tracked in Git.

The pre-closeout evidence in
`docs/evidence/phase3/outputs/01-git-status-before.txt` shows:

- `.gitignore` and `.gitattributes` cleanup in progress
- tracked deletions under
  `data/raw/fcc/consumer_complaints/20260306T140358Z/`
- tracked deletions under
  `data/raw/fcc/consumer_complaints/20260306T140620Z/`

This means historical raw payload runs had entered version control.

### Solution Applied

The Phase 3 closeout applied these repo hygiene corrections:

- `.gitignore` excludes:
  - `data/raw/fcc/consumer_complaints/**`
  - `data/raw/fcc/_metadata/**`
- `.gitattributes` normalizes line endings
- previously tracked raw payload files were removed from Git
- `.gitkeep` placeholders preserve the raw directory structure

### Why It Matters In Production

Tracking raw landed payloads in Git is operationally unsafe because it:

- inflates repository size
- slows Git operations
- mixes runtime artifacts with source control
- makes review noisy
- undermines reproducible engineering workflows

The raw layer is designed for append-only runtime landing, not for source
control storage.

## 9. Hardening Enhancements

Phase 3 closed with several implementation hardening changes that are now
visible in the committed code and tests.

### Pagination Fix

The pipeline now checks for an empty page before writing a raw file.

Result:

- terminal empty pages are not landed
- `total_pages_fetched` reflects only landed non-empty pages

### Run ID Uniqueness

`src/run_id.py` now generates:

- microsecond-resolution UTC run IDs
- optional `_{sequence}` suffix for same-instant collisions

Result:

- rapid reruns do not share the same raw output directory or metadata
  file

### Validation Improvements

`src/config_loader.py` now requires:

- `output.metadata_path`

`src/http_client.py` now rejects:

- JSON payloads that are not arrays
- JSON arrays containing non-object items

### Failure Handling

`ingestion/fcc_raw_ingestion.py` now wraps metadata writes through
`try_write_run_metadata()`.

Result:

- metadata-write failures log a clean error
- the pipeline exits with code `1`
- secondary metadata-write failures do not crash the process with an
  unhandled traceback

## 10. Testing

### Test File

Phase 3 regression coverage is implemented in:

- `tests/test_phase3_ingestion.py`

### What Is Covered

Committed test coverage includes:

- terminal empty page is not landed
- success-path metadata write failures return a clean exit
- failure-path metadata write failures return a clean exit
- missing `output.metadata_path` fails validation
- `run_id` uniqueness when the clock does not advance
- JSON page download rejects non-object array items

### Test Results

Committed evidence in `docs/evidence/phase3/outputs/02-pytest.txt`
records:

- command: `python -m pytest -q`
- result: `6 passed`
- exit code: `0`

## 11. Execution Evidence

### Dataset Size

Observed from the committed successful validation run:

- records: `3,459,080`
- pages: `70`
- landed bytes: `2,355,265,931`

### Runtime Behavior

Observed from metadata:

- run start: `2026-03-28T21:46:36Z`
- run end: `2026-03-28T22:15:15Z`
- observed wall-clock duration: approximately `28 minutes 39 seconds`

Observed page behavior:

- 69 full pages of `50,000` records
- 1 final partial page of `9,080` records

### Evidence Files

Phase 3 execution evidence is committed under
`docs/evidence/phase3/outputs/`:

- `01-git-status-before.txt`
- `02-pytest.txt`
- `03-fcc-ingestion-run.txt`
- `04-metadata-verification.txt`
- `05-raw-page-verification.txt`
- `06-failure-path-validation.txt`
- `07-git-status-after.txt`

## 12. Validation Performed

### Metadata Validation

Committed metadata validation confirmed:

- metadata file exists
- metadata `status = success`
- `failure_message = null`
- `exception_type = null`
- landed page count reconciles with metadata page count

### Raw Data Validation

Committed raw-page validation confirmed:

- all landed files are JSON arrays
- all array items are objects
- no empty page files were landed
- the final expected next page file does not exist
- record counts from raw files reconcile with metadata totals

### Failure Path Validation

Committed failure-path validation used an invalid config with the
`metadata_path` key removed.

Observed result:

- stderr message:
  `Missing required configuration key: output.metadata_path`
- exit code: `1`
- traceback present: `False`

This is recorded in
`docs/evidence/phase3/outputs/06-failure-path-validation.txt`.

## 13. Final Outcome

### What Phase 3 Delivers

Phase 3 delivers a fully implemented FCC raw-layer ingestion pipeline
that is:

- config-driven
- paginated
- retry-aware
- append-only by run
- metadata-backed
- observable from the CLI
- hardened against the specific edge cases captured in the regression
  suite

### Production Readiness

Within the Phase 3 raw-layer scope, the implementation is production-grade
because the repository now contains:

- source and configuration contracts
- implemented ingestion modules
- hardened pagination and failure behavior
- run-level metadata
- raw-layer repo hygiene controls
- regression tests
- committed execution and validation evidence

This production readiness statement applies to the Phase 3 raw ingestion
scope only. It does not imply that downstream silver, gold, analytics,
or platform automation phases are implemented in this document.
