# FCC Raw Landing Zone Design

## Purpose

This document defines the raw landing zone structure and naming
conventions for the Phase 3 FCC Consumer Complaints ingestion pipeline.

The goal is to establish a production-oriented raw data layout that is
simple, auditable, and safe for repeatable ingestion runs.

## Traceability

- Jira Ticket ID: `TCAP-4`
- Version: `0.1-draft`
- Date: `2026-03-06`
- Phase: `Phase 3 - Production Data Ingestion Pipeline`
- Status: `Task 2 raw landing zone design`

## Raw Landing Root

The FCC raw landing root is:

- `data/raw/fcc/consumer_complaints`

This directory stores unmodified source payloads only.

## Metadata Root

The FCC ingestion metadata root is:

- `data/raw/fcc/_metadata`

This directory stores run-level ingestion metadata and audit records only.

Metadata must never be mixed into the raw payload directory.

## Directory Structure

The repository-managed raw layer structure for FCC complaint ingestion is:

```text
data/
  raw/
    fcc/
      consumer_complaints/
        .gitkeep
      _metadata/
        .gitkeep
```

At runtime, each ingestion run must land into an isolated run-specific
directory under the raw payload root.

Recommended runtime pattern:

- `data/raw/fcc/consumer_complaints/{run_id}/`

Recommended metadata pattern:

- `data/raw/fcc/_metadata/{run_id}.json`

## Naming Conventions

### Run Directory Naming

- Pattern: `{run_id}`
- Source: generated from the ingestion pipeline run ID strategy
- Recommended Format: `YYYYMMDDTHHMMSSffffffZ`
- Example: `20260306T221530123456Z`
- Collision Rule: the implementation may append `_{sequence}` if more
  than one run ID is generated within the same timestamp instant

Each run directory represents a single pipeline execution boundary.

### Raw Payload File Naming

- Pattern: `{raw_file_prefix}_{page_number:06d}.json`
- Example: `consumer_complaints_page_000001.json`
- Rule: one UTF-8 JSON file must be landed per fetched FCC page that
  contains records
- Rule: the terminal empty page used to detect end-of-data must not be
  landed

Each landed file represents one API page from the FCC source.

### Metadata File Naming

- Pattern: `{run_id}.json`
- Example: `20260306T221530123456Z.json`

Each metadata file corresponds to exactly one ingestion run.

## Run ID Usage

The raw landing zone depends on the same run ID convention defined in the
FCC ingestion configuration design:

- UTC-based
- compact timestamp format
- unique per ingestion execution

The run ID is used in both:

- the raw run directory path
- the metadata file name

This creates direct traceability between landed payloads and ingestion
metadata.

## Metadata Separation

Raw source payloads and ingestion metadata must remain physically
separated:

- payloads under `data/raw/fcc/consumer_complaints/{run_id}/`
- metadata under `data/raw/fcc/_metadata/{run_id}.json`

This prevents audit artifacts from being confused with source data and
keeps the raw landing area clean for downstream processing.

## Immutability Rules

The raw landing zone is append-only.

Rules:

- raw payload files must never be overwritten in place
- raw metadata files must never be overwritten in place
- each ingestion run must create a new run-specific landing location
- reruns must create a new run ID rather than reuse an older directory

If a source extraction needs to be repeated, the pipeline must produce a
new isolated run directory and matching metadata record.

## Rerun Behavior

Reruns are expected in production due to retries, source issues, or
operational recovery.

Required behavior:

- reruns must not overwrite previous raw payloads
- reruns must remain traceable as separate ingestion attempts
- downstream layers can decide later which run is authoritative

This keeps the raw layer safe for audit and operational troubleshooting.

## Example Landed Paths

Paged JSON example:

- `data/raw/fcc/consumer_complaints/20260306T221530123456Z/consumer_complaints_page_000001.json`
- `data/raw/fcc/consumer_complaints/20260306T221530123456Z/consumer_complaints_page_000002.json`
- `data/raw/fcc/_metadata/20260306T221530123456Z.json`

Repeated same-instant run example:

- `data/raw/fcc/consumer_complaints/20260306T221530123456Z_01/consumer_complaints_page_000001.json`
- `data/raw/fcc/_metadata/20260306T221530123456Z_01.json`

## Notes for Future Bronze Processing

Bronze processing is not implemented in this task.

The raw landing structure is designed so future bronze ingestion can:

- read one isolated run at a time
- correlate raw files with one metadata record per run
- preserve raw-layer immutability while promoting selected runs downstream

No bronze, silver, or gold logic should modify the raw landed payloads.

## Alignment With Existing Phase 3 Design

This raw landing zone design aligns with:

- the FCC source contract draft
- the FCC ingestion configuration design

In particular, it preserves the previously defined root paths:

- `output.raw_path = data/raw/fcc/consumer_complaints`
- `output.metadata_path = data/raw/fcc/_metadata`
