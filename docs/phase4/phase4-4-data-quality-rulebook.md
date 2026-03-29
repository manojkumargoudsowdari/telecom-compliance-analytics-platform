# Phase 4-4: Data Quality Rulebook (Silver Layer)

## 1. Overview

This document defines the data quality expectations for the Silver
dataset `silver_fcc_consumer_complaints`.

It builds on:

- `docs/phase4/phase4-1-silver-functional-spec.md`
- `docs/phase4/phase4-2-silver-schema-contract.md`
- `docs/phase4/phase4-3-raw-to-silver-transformation-rulebook.md`

This rulebook defines validation expectations only. It does not define
transformation logic, execution design, or implementation mechanics.

## 2. Data Quality Principles

- Deterministic validation: the same Silver inputs must produce the same
  validation outcomes when the same rule set is applied
- Explicit rule definitions: every quality check must have a clear
  intent and validation category
- No silent data loss: records or datasets that fail quality rules must
  not disappear without traceable handling
- Traceability of failures: validation outcomes must remain attributable
  to the relevant `source_run_id`
- Reproducibility: repeated validation over identical Silver data must
  produce identical results
- Separation from transformation logic: this rulebook defines what must
  be validated, not how records are transformed into Silver

## 3. Rule Categories

### Critical Rules

Critical rules must pass for the Silver dataset to be considered valid.
Violations block or invalidate the Silver output.

### Warning Rules

Warning rules do not block output, but they indicate elevated data risk
or potential drift that must be reported.

### Informational Rules

Informational rules support observability, monitoring, and drift
detection. They do not block output.

## 4. Field-Level Validation Rules

### Required Fields

Critical validations:

- `complaint_id` must be present, non-null, and non-empty
- `date_created` must be present and valid
- `source_run_id` must be present
- `silver_processed_at_utc` must be present
- `source_system` must be present

### Type Validation

Critical validations:

- `date_created` must conform to the approved `DATE` contract
- `ticket_created_utc`, when present, must conform to the approved
  `TIMESTAMP` contract
- `issue_date`, when present, must conform to the approved `DATE`
  contract
- `silver_processed_at_utc` must conform to the approved `TIMESTAMP`
  contract

Warning validations:

- string fields should not contain values that violate the expected
  schema type after transformation

### Domain Checks

Critical validations:

- `complaint_id` must not be blank or null-equivalent

Warning validations:

- `state`, when present, should satisfy basic format sanity expected for
  a state or territory code
- `zip_code`, when present, should satisfy basic ZIP/postal-code sanity
- identifier-like fields carried as optional strings should not be
  dominated by malformed blank-equivalent values

## 5. Dataset-Level Validation Rules

### Critical Rules

- `complaint_id` must be unique in the final Silver dataset
- final Silver row count must be greater than zero
- final Silver grain must remain `one row per complaint_id`
- all records must conform to the Phase 4-2 schema contract, including
  required column presence, approved data types, and nullability rules

### Warning Rules

- row-count results should remain within reasonable bounds relative to
  the corresponding raw ingestion run
- deduplication should behave as expected, with multiple raw records
  resolving to one final Silver record per `complaint_id`
- Silver row counts should reconcile to raw ingestion at a high level,
  acknowledging that exact equality is not expected when invalid records
  are rejected

### Informational Rules

- total row counts by `source_run_id`
- duplicate rates observed before final deduplication
- high-level raw-to-Silver reduction profile

## 6. Null and Completeness Checks

### Critical Rules

- required fields must have zero nulls in final Silver output

### Warning Rules

- optional fields should have monitored null rates
- sudden increases in null rates for key optional fields should be
  flagged
- large completeness changes between comparable runs should be flagged

### Informational Rules

- null counts by column
- null percentages by column
- trend view of completeness over time or by `source_run_id`

## 7. Drift Detection Rules

### Warning Rules

- new unexpected values in key categorical fields such as `issue_type`
  and `method` should be flagged
- notable distribution changes in key dimensions should be flagged
- sudden changes in complaint volume patterns should be flagged
- schema drift such as missing required columns or unexpected extra
  columns should be flagged

### Informational Rules

- new distinct values by categorical field
- distribution summaries for key dimensions
- run-over-run volume comparisons

## 8. Invalid Record Handling Expectations

- records failing critical rules must not enter final Silver
- records failing critical rules must be routed to the reject or
  quarantine path defined in Phase 4-5
- invalid records must not be silently dropped
- quality outcomes must preserve traceability to the originating
  `source_run_id`

## 9. Failure Behavior

- Critical rule failures block or invalidate Silver dataset production
- Warning rule failures allow output but require reporting
- Informational findings do not block output
- Validation outcomes must be deterministic and reproducible

## 10. Reporting Expectations

Validation reporting should conceptually provide:

- validation summary with rule counts and pass/fail outcomes
- list of failed rule categories
- counts of affected records by rule category
- sample invalid records or representative failures for diagnosis
- traceability of reported issues back to `source_run_id`

This section defines reporting expectations only. It does not prescribe
an execution format or implementation design.

## 11. Out of Scope

This rulebook does not define:

- transformation logic
- reject table schema
- execution or orchestration design
- implementation details
- Gold-layer metrics, KPI logic, or dashboards

## 12. Open Questions / Review Notes

- Basic format sanity is expected for `state` and `zip_code`, but the
  project should confirm in a later design step whether warning-level
  checks should remain lightweight or evolve into stronger approved
  domain reference validation.
- Raw-to-Silver reconciliation is intentionally defined at a high level.
  Phase 4-6 should confirm how reconciliation summaries are produced
  without changing the quality rule intent.
