# Phase 3 FCC Raw Ingestion Runbook

## Purpose

This runbook defines how to execute, validate, and capture evidence for
the Phase 3 FCC raw ingestion implementation in this repository.

It is specific to the FCC Consumer Complaints raw layer implemented by
`ingestion/fcc_raw_ingestion.py` using
`configs/fcc_ingestion.template.yaml`.

## Scope

This runbook covers only Phase 3 raw-layer closeout:

- repository state inspection
- test execution
- one clean FCC raw ingestion run
- metadata and raw-page verification
- one deterministic failed-path validation
- evidence capture under `docs/evidence/phase3/outputs/`

This runbook does not cover bronze, silver, gold, dashboard, or Phase 4
work.

## Prerequisites

- Run from the repository root:
  `D:\Work\Code\telecom-compliance-analytics-platform`
- Python is available on the shell path.
- Required Python packages from `requirements.txt` are installed.
- Network access to `https://opendata.fcc.gov/resource/3xyp-aqkj.json`
  is available.
- The checked-in config file exists at
  `configs/fcc_ingestion.template.yaml`.
- Raw landing roots exist or can be created:
  `data/raw/fcc/consumer_complaints/` and `data/raw/fcc/_metadata/`.

## Exact Commands

### 1. Inspect Repository State

```powershell
git status --short --branch
git diff --cached --name-status
git diff --name-status
```

### 2. Run Phase 3 Regression Tests

```powershell
python -m pytest -q
```

Expected result:

- pytest completes successfully
- the current hardened Phase 3 suite reports all tests passing

### 3. Run a Clean FCC Ingestion

```powershell
$runLogPath = "docs/evidence/phase3/outputs/ingestion-run.log"
$summaryPath = "docs/evidence/phase3/outputs/ingestion-summary.json"
$ingestionOutput = python -m ingestion.fcc_raw_ingestion --config configs/fcc_ingestion.template.yaml 2>&1
$ingestionOutput | Tee-Object -FilePath $runLogPath
$jsonStart = ($ingestionOutput | Select-String '^\{' | Select-Object -Last 1).LineNumber
$ingestionOutput[($jsonStart - 1)..($ingestionOutput.Count - 1)] | Set-Content $summaryPath
```

Expected stdout behavior:

- per-page progress logs are emitted during the run
- the final stdout payload is a JSON summary

Expected summary fields:

- `run_id`
- `source_endpoint`
- `landing_directory`
- `total_pages_fetched`
- `total_records_fetched`
- `total_bytes_landed`
- `fetched_at_utc`
- `status`

### 4. Verify Metadata for the Run

```powershell
$summary = Get-Content "docs/evidence/phase3/outputs/ingestion-summary.json" -Raw | ConvertFrom-Json
$runId = $summary.run_id
$metadataPath = "data/raw/fcc/_metadata/$runId.json"
Get-Content $metadataPath -Raw | ConvertFrom-Json | ConvertTo-Json -Depth 5
```

Expected metadata checks:

- `status` is `success`
- `run_id` matches the summary output
- `landing_directory` ends with the same `run_id`
- `total_pages_fetched`, `total_records_fetched`, and
  `total_bytes_landed` are populated
- `failure_message` is null
- `exception_type` is null

### 5. Verify Raw Page Landing

```powershell
$runDirectory = "data/raw/fcc/consumer_complaints/$runId"
Get-ChildItem $runDirectory -Filter "*.json" | Sort-Object Name | Select-Object Name, Length
(Get-ChildItem $runDirectory -Filter "*.json").Count
Get-Content (Join-Path $runDirectory "consumer_complaints_page_000001.json") -TotalCount 20
```

Expected raw-page checks:

- at least one landed JSON page exists
- file names follow `consumer_complaints_page_000001.json`
- there is no trailing empty terminal page file
- the first page is a JSON array of objects

## Acceptance Criteria

Phase 3 raw ingestion is ready to close only when all of the following
are true:

- repository state has been inspected and is understood before evidence
  capture
- `python -m pytest -q` passes
- the FCC ingestion command exits successfully
- run metadata is written to `data/raw/fcc/_metadata/{run_id}.json`
- raw files are written to
  `data/raw/fcc/consumer_complaints/{run_id}/`
- raw page files are page-based JSON and do not include a terminal empty
  page
- the run ID is unique for the ingestion execution
- a deterministic failure path returns exit code `1` without an
  unhandled traceback
- evidence artifacts are stored under
  `docs/evidence/phase3/outputs/`

## Failure Validation Procedure

Use a temporary invalid config to verify the pipeline fails cleanly on a
required Phase 3 config error without modifying checked-in source files.

```powershell
$invalidConfig = "docs/evidence/phase3/outputs/fcc_ingestion.invalid.yaml"
Copy-Item "configs/fcc_ingestion.template.yaml" $invalidConfig
(Get-Content $invalidConfig) | Where-Object { $_ -notmatch "metadata_path:" } | Set-Content $invalidConfig
python -m ingestion.fcc_raw_ingestion --config $invalidConfig
$LASTEXITCODE
Remove-Item $invalidConfig
```

Expected failure validation result:

- command exits with code `1`
- stderr reports a clean config validation failure
- no Python traceback is emitted

Metadata-write failure handling is covered by the automated regression
tests in `tests/test_phase3_ingestion.py`.

## Expected Outputs

The evidence directory should contain only real execution artifacts
created by the operator during validation. Do not pre-populate runtime
results in source control.

Expected operator-generated evidence after a successful closeout run:

- `docs/evidence/phase3/outputs/ingestion-run.log`
- `docs/evidence/phase3/outputs/ingestion-summary.json`
- optional captured terminal transcript or screenshots
- optional copied metadata sample for review if needed

The repository should keep only placeholders and templates until a real
validation run is performed.

## Evidence Checklist

- repo state inspected and captured
- pytest output captured
- ingestion summary captured
- run metadata verified
- raw page landing verified
- failed-path validation executed
- no fabricated runtime output checked into Git
