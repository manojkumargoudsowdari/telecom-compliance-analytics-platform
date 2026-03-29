# Phase 4 Silver Pipeline Runbook

## Purpose

This runbook defines how to execute the Phase 4 FCC Silver pipeline,
validate the resulting Silver dataset, and capture deterministic evidence
for repository review.

It is specific to the FCC Consumer Complaints Silver layer implemented by
`ingestion/fcc_silver_transformation.py` using
`configs/fcc_ingestion.template.yaml`.

## Scope

This runbook covers only the Phase 4 Silver pipeline:

- reading one selected Phase 3 raw run
- mapping raw records into Silver candidate records
- deterministic deduplication to one row per `complaint_id`
- dataset-level validation
- reject artifact persistence
- final Silver dataset persistence
- Silver metadata persistence
- evidence capture under `docs/evidence/phase4/outputs/`

This runbook does not cover Gold marts, dashboards, orchestration, or
Phase 5 work.

## Prerequisites

- Run from the repository root:
  `D:\Work\Code\telecom-compliance-analytics-platform`
- Python is available on the shell path.
- Required Python packages from `requirements.txt` are installed.
- The checked-in config file exists at
  `configs/fcc_ingestion.template.yaml`.
- The Phase 3 raw run exists for the selected source run:
  `data/raw/fcc/consumer_complaints/20260328T214636092984Z/`
- The matching Phase 3 raw metadata exists:
  `data/raw/fcc/_metadata/20260328T214636092984Z.json`

## Exact Command

```powershell
python ingestion/fcc_silver_transformation.py --config configs/fcc_ingestion.template.yaml --source-run-id 20260328T214636092984Z
```

## Expected Outputs

After a successful run, the Silver pipeline writes:

- Silver dataset:
  `data/silver/fcc/consumer_complaints/20260328T214636092984Z/silver_fcc_consumer_complaints.json`
- validation summary:
  `data/silver/fcc/_quality/20260328T214636092984Z/validation_summary.json`
- reject artifact:
  `data/silver/fcc/_rejects/20260328T214636092984Z/candidate_reject_records.json`
- Silver metadata:
  `data/silver/fcc/_metadata/20260328T214636092984Z.json`

## Validation Expectations

The run is considered successful only when all of the following are true:

- the CLI summary reports `status = silver_pipeline_complete`
- `validation_passed = true`
- `critical_rule_failures = 0`
- the final Silver dataset is written
- the validation summary artifact is written
- the reject artifact is written, even when empty
- the metadata file is written and reconciles with the run summary

## Evidence Pack Contents

The Phase 4 evidence pack stores:

- the exact command used
- one captured CLI run summary
- one copied validation artifact
- one copied metadata artifact
- one deterministic small Silver sample
- one deterministic reject sample
- one count reconciliation summary

## Evidence Checklist

- command captured
- run summary captured
- validation artifact copied
- metadata artifact copied
- sample Silver records copied
- sample reject records copied
- count reconciliation captured
