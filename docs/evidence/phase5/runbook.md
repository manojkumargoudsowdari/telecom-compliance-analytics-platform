# Phase 5 Gold Pipeline Runbook

## Purpose

This runbook defines how to execute the Phase 5 FCC Gold pipeline,
validate the resulting Gold facts, and capture deterministic evidence
for repository review.

It is specific to the FCC Consumer Complaints Gold layer implemented by
`ingestion/fcc_gold_transformation.py` using
`configs/fcc_ingestion.template.yaml`.

## Scope

This runbook covers only the Phase 5 Gold pipeline:

- reading one selected Phase 4 Silver run
- streaming the large Silver JSON-array input using `ijson`
- building `fact_complaints_daily`
- building `fact_complaints_monthly` from daily Gold only
- persisting Gold metadata
- persisting Gold validation artifacts
- evidence capture under `docs/evidence/phase5/outputs/`

This runbook does not cover Power BI implementation, dashboard styling,
semantic-model optimization, or future Gold KPI extensions.

## Source Run

- `source_run_id`: `20260328T214636092984Z`
- Silver input:
  `data/silver/fcc/consumer_complaints/20260328T214636092984Z/silver_fcc_consumer_complaints.json`

## Exact Command

```powershell
python ingestion/fcc_gold_transformation.py --config configs/fcc_ingestion.template.yaml --source-run-id 20260328T214636092984Z
```

## Produced Outputs

After a successful run, the Gold pipeline writes:

- daily Gold fact root:
  `data/gold/fact_complaints_daily/`
- monthly Gold fact root:
  `data/gold/fact_complaints_monthly/`
- validation summary:
  `data/gold/_quality/20260328T214636092984Z/validation_summary.json`
- Gold metadata:
  `data/gold/_metadata/20260328T214636092984Z.json`

## Known Implementation Decisions

- `ijson` is the approved dependency for streaming the large Silver
  JSON-array input. Hand-rolled streaming parsers are not approved.
- `fact_complaints_monthly` is derived only from `fact_complaints_daily`.
  Direct Silver-to-monthly aggregation is not approved.
- Persisted Gold scope in this first implementation is limited to:
  - daily `complaint_count`
  - monthly `complaint_count`
  - monthly `complaint_growth_rate`
  - monthly `rolling_average_complaint_count`
- `rolling_average_complaint_count` is calendar-month based. Missing
  months inside the fixed window are treated as zero-complaint months.
- `category_share` remains a Gold-defined KPI, but it is not persisted as
  a physical column in the first Gold implementation.

## Evidence Pack Contents

The Phase 5 evidence pack stores:

- the exact command used
- one run summary compiled from persisted Gold metadata and validation
  artifacts
- one copied validation artifact
- one copied metadata artifact
- one count summary
- one reconciliation summary
- one unknown-member summary
- one known-constraints summary

## Evidence Notes

- The evidence pack uses only real outputs from the completed Gold run for
  `20260328T214636092984Z`.
- The CLI transcript itself was not persisted during the run, so
  `01-run-summary.txt` is compiled from the persisted Gold metadata and
  validation artifacts for that same run.
- The validation artifact truthfully stores
  `informational_findings = 3`, but it does not persist the named
  informational entries. The corresponding informational conditions are
  documented in the evidence notes using the persisted unknown-member row
  counts.
