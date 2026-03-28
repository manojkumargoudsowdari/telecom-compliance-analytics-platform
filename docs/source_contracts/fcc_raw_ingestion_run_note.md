# FCC Raw Ingestion Run Note

## Purpose

This note explains how to execute the FCC raw landing ingestion locally
for Phase 3 Task 3.

## Local Command

```bash
python -m ingestion.fcc_raw_ingestion --config configs/fcc_ingestion.template.yaml
```

## Source Configuration

The checked-in template configuration is aligned to the finalized Phase 3
source design:

- production source: `Socrata JSON API`
- base endpoint: `https://opendata.fcc.gov/resource/3xyp-aqkj.json`
- ingestion mode: `full snapshot`
- pagination method: `$limit + $offset`
- page size: `50000`
- raw landing pattern: `one JSON file per page under each run_id`

## Successful Output

On success, the command prints a concise JSON summary with:

- `run_id`
- `source_endpoint`
- `landing_directory`
- `total_pages_fetched`
- `total_records_fetched`
- `total_bytes_landed`
- `fetched_at_utc`
- `status`

## Raw Landing Behavior

Each execution creates one UTC run ID and lands paginated raw JSON payload
files into a run-specific directory under the configured raw landing
root.

Each landed file contains the raw page records serialized to UTF-8 JSON
without business transformation.

The terminal empty page used to detect end-of-data is not landed as a
raw file.
