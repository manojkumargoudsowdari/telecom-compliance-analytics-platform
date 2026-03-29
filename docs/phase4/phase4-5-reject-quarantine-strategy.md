# Phase 4-5: Reject and Quarantine Strategy (Silver Layer)

## 1. Overview

This document defines the reject and quarantine strategy for the Silver
layer of the Telecom Compliance Analytics Platform (TCAP).

It builds on:

- `docs/phase4/phase4-1-silver-functional-spec.md`
- `docs/phase4/phase4-2-silver-schema-contract.md`
- `docs/phase4/phase4-3-raw-to-silver-transformation-rulebook.md`
- `docs/phase4/phase4-4-data-quality-rulebook.md`

This document defines data-handling strategy only. It does not define
implementation design, physical storage design, or execution mechanics.

## 2. Purpose of the Reject / Quarantine Layer

The reject and quarantine layer exists to ensure that records which fail
Silver entry requirements are not silently dropped.

Its purpose is to:

- preserve traceability for records that do not enter final Silver
- rejected records are not deleted; they are preserved in a traceable
  reject/quarantine dataset
- provide a controlled destination for invalid records
- support auditability, diagnosis, and remediation
- separate valid Silver output from records that failed required field,
  schema, or validation expectations
- reject handling must be idempotent; the same raw inputs must produce
  the same reject/quarantine outcomes

## 3. Types of Rejected Records

Records are candidates for reject or quarantine handling when they fail
conditions such as:

- missing required fields
- invalid type casts on required fields
- schema violations

Representative categories include:

- missing or invalid `complaint_id`
- missing or invalid `date_created`
- missing `source_run_id`
- missing `silver_processed_at_utc`
- missing `source_system`
- records that cannot conform to the Phase 4-2 Silver schema contract
- records that fail Critical rules defined in Phase 4-4

## 4. Deduplication vs Rejection Boundary

- records excluded due to deduplication are not considered rejected
- only records that fail required-field, schema, or Critical quality
  rules are routed to reject/quarantine
- deduplicated records represent valid but non-selected candidates, not
  invalid records

## 5. Reject Dataset Definition

The reject/quarantine output is a conceptual companion dataset for
Silver, not part of the final validated Silver table itself.

Conceptual structure should include:

- raw record payload or a canonical rejected-record representation
- `source_run_id`
- reject or quarantine timestamp
- reject reason code
- reject reason description
- enough source context to trace the record back to its raw origin

The reject dataset must remain linkable to the originating raw run and
must distinguish why a record was rejected without duplicating the full
Silver schema contract.

## 6. Reject Reason Taxonomy

Reject reasons should be standardized through a controlled taxonomy.

Suggested conceptual reason groups:

- `MISSING_REQUIRED_FIELD`
- `INVALID_REQUIRED_FIELD`
- `INVALID_TYPE_CAST`
- `SCHEMA_CONTRACT_VIOLATION`
- `CRITICAL_QUALITY_RULE_FAILURE`
- `UNRESOLVABLE_TRANSFORMATION_INPUT`

Reason codes should be stable enough to support:

- operational reporting
- repeated run comparison
- issue triage
- audit review

## 7. Traceability Requirements

Every rejected or quarantined record must remain traceable to:

- the originating `source_run_id`
- the raw source record or raw-record representation
- the reject reason that prevented entry into final Silver
- the validation or rule context under which the rejection occurred

The strategy must support reconstruction of why a specific raw record
did not become part of the final Silver dataset.

## 8. Retention Expectations

Retention behavior is conceptual at this stage.

The reject/quarantine dataset should be retained long enough to support:

- auditability
- troubleshooting
- run reconciliation
- rule refinement and recurring issue analysis

Retention should not be shorter than the useful review horizon for
Silver validation and remediation. Exact retention periods belong to
later operational design work.

## 9. Reporting Expectations

Reject and quarantine handling should support conceptual reporting such
as:

- reject counts by `source_run_id`
- reject counts by reason code
- proportion of rejected records relative to candidate Silver input
- representative samples of rejected records for diagnosis
- trend view of recurring reject categories over time

This reporting expectation supports observability, but does not define
execution format or reporting implementation.

## 10. Out of Scope

This strategy does not define:

- transformation logic
- data quality rule definitions
- reject table physical schema or storage implementation
- execution or orchestration design
- Gold-layer modeling or dashboard behavior

The purpose of this document is only to define how invalid records are
treated conceptually once they are determined to be ineligible for final
Silver output.
