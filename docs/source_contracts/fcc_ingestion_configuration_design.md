# FCC Ingestion Configuration Design

## Purpose

This document defines the ingestion configuration design for the Phase 3
FCC Consumer Complaints pipeline.

Together with the FCC source contract, this configuration design completes
Task 1 for Phase 3 by establishing the externalized settings the pipeline
will consume before ingestion code is implemented.

## Traceability

- Jira Ticket ID: `TCAP-4`
- Version: `0.1-draft`
- Date: `2026-03-06`
- Phase: `Phase 3 - Production Data Ingestion Pipeline`
- Status: `Task 1 configuration design`

## Design Goals

- Keep source and output paths externalized.
- Support repeatable batch ingestion runs.
- Separate local development defaults from future deployed overrides.
- Standardize batch IDs, timestamps, and metadata paths.
- Make retry and timeout behavior configurable without code changes.

## Configuration Scope

The FCC ingestion pipeline should read configuration from an external
configuration file and, in deployed environments, allow environment
variables or platform settings to override selected values.

Recommended precedence order:

1. Environment-specific overrides
2. Configuration file values
3. Code defaults for non-critical local development only

## Required Configuration Keys

### Source Endpoint

- Key: `source.endpoint`
- Purpose: Fully qualified machine-readable FCC extraction endpoint
- Example:
  `https://opendata.fcc.gov/resource/<candidate-endpoint-pending-validation>.csv`
- Rule: Must remain aligned with the validated source contract
- Status: `Candidate endpoint pending validation`

### Raw Output Path

- Key: `output.raw_path`
- Purpose: Root landing path for unmodified FCC source files
- Example: `data/raw/fcc/consumer_complaints`
- Rule: Raw payloads must be written without business transformation

### Run Mode

- Key: `run.mode`
- Allowed Values: `full`, `incremental`, `backfill`
- Recommended Initial Value: `full`
- Purpose: Controls batch behavior as the pipeline evolves

### File Format

- Key: `source.file_format`
- Allowed Values: `csv`, `json`
- Recommended Initial Value: `csv`
- Purpose: Declares the expected source serialization format

### Batch / Run ID Strategy

- Key: `run.id_strategy`
- Recommended Value: `timestamp_utc_compact`
- Example Generated Value: `20260306T221530Z`
- Purpose: Produces a deterministic batch identifier for every ingestion
  run
- Rule: Each pipeline execution must emit exactly one run ID

### Timestamp Convention

- Key: `run.timestamp_format`
- Recommended Value: `iso_8601_utc`
- Example: `2026-03-06T22:15:30Z`
- Purpose: Standardizes timestamps across logs, metadata, and landed paths

### Metadata Output Path

- Key: `output.metadata_path`
- Purpose: Root path for ingestion metadata records and audit artifacts
- Example: `data/raw/fcc/_metadata`
- Rule: Metadata must be stored separately from landed source payloads

### Retry and Timeout Controls

- Key: `http.request_timeout_seconds`
- Recommended Initial Value: `120`
- Purpose: Upper bound for source retrieval calls

- Key: `http.max_retries`
- Recommended Initial Value: `3`
- Purpose: Maximum retry attempts for transient failures

- Key: `http.retry_backoff_seconds`
- Recommended Initial Value: `5`
- Purpose: Base backoff interval between retry attempts

### Environment Overrides

- Key: `environment.name`
- Allowed Values: `local`, `dev`, `test`, `prod`
- Recommended Initial Value: `local`
- Purpose: Distinguishes runtime context for pathing and override
  behavior

- Key: `overrides.enabled`
- Recommended Initial Value: `true`
- Purpose: Allows environment variables or deployment settings to replace
  local file values

## Recommended Path Conventions

### Raw Data Landing Root

Recommended root:

- `data/raw/fcc/consumer_complaints`

Recommended per-run layout:

- `data/raw/fcc/consumer_complaints/{run_id}/source_file.csv`

This keeps each ingestion batch isolated, traceable, and safe for reruns
without overwriting prior raw payloads.

### Metadata Root

Recommended root:

- `data/raw/fcc/_metadata`

Recommended per-run layout:

- `data/raw/fcc/_metadata/{run_id}.json`

## Environment Strategy

### Local Development

Use repository-relative defaults for fast iteration:

- `output.raw_path = data/raw/fcc/consumer_complaints`
- `output.metadata_path = data/raw/fcc/_metadata`
- `environment.name = local`

### Future Deployed Environment

In deployed environments, the same logical keys should be overridden using
environment-specific settings rather than changing code.

Expected override targets:

- `source.endpoint`
- `output.raw_path`
- `output.metadata_path`
- `run.mode`
- `http.request_timeout_seconds`
- `http.max_retries`
- `http.retry_backoff_seconds`

## Example Configuration Structure

```yaml
environment:
  name: local

source:
  endpoint: https://opendata.fcc.gov/resource/<candidate-endpoint-pending-validation>.csv
  file_format: csv

output:
  raw_path: data/raw/fcc/consumer_complaints
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

## Implementation Rules

- The ingestion pipeline must not hard-code source endpoints or output
  paths.
- No business-critical values should rely on code defaults in deployed
  environments.
- Batch IDs and timestamps must be generated in UTC.
- Local defaults must work without deployed infrastructure.
- Deployed environments must be able to override configuration without
  modifying source code.
- Metadata output must remain separate from raw landed files.

## Task 1 Completion Statement

With the FCC source contract draft and this ingestion configuration
design, Task 1 is complete at the documentation and design level. Code
implementation begins in the next Phase 3 tasks.
