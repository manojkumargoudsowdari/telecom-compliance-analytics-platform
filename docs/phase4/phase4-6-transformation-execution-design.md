# Phase 4-6: Transformation Execution Design

## 1. Execution Overview

This document defines how the FCC Silver transformation should be
executed in the `telecom-compliance-analytics-platform` repository.

The goal is to establish a controlled, production-grade execution
structure for Phase 4 without implementing the pipeline yet.

This design builds on:

- `docs/phase4/phase4-1-silver-functional-spec.md`
- `docs/phase4/phase4-2-silver-schema-contract.md`
- `docs/phase4/phase4-3-raw-to-silver-transformation-rulebook.md`
- `docs/phase4/phase4-4-data-quality-rulebook.md`
- `docs/phase4/phase4-5-reject-quarantine-strategy.md`

## 2. Entry Point

The Silver transformation should follow the same repository pattern used
by Phase 3 raw ingestion.

Recommended entry point:

- `ingestion/fcc_silver_transformation.py`

Recommended role:

- parse runtime arguments
- load Silver configuration
- resolve input raw run scope
- orchestrate transform, validation, reject handling, and metadata
  writing
- emit a deterministic run summary

## 3. File Structure

To remain consistent with the current repository layout, the Silver
execution code should be split between `ingestion/` and `src/`.

Recommended structure:

- `ingestion/fcc_silver_transformation.py`
  - execution entry point
- `src/silver_transformer.py`
  - raw-to-Silver structural transformation orchestration
- `src/silver_validator.py`
  - Silver validation orchestration aligned to Phase 4-4
- `src/silver_rejects.py`
  - reject/quarantine preparation aligned to Phase 4-5
- `src/silver_metadata_writer.py`
  - Silver run metadata persistence

This keeps the same separation-of-concerns pattern already used by the
raw layer.

## 4. Inputs

Primary inputs should be:

- raw page files under:
  - `data/raw/fcc/consumer_complaints/{source_run_id}/`
- raw run metadata under:
  - `data/raw/fcc/_metadata/{source_run_id}.json`

Input selection should be explicit rather than inferred silently.

Recommended execution scope:

- process one selected raw run at a time
- require the chosen `source_run_id` to be available before the Silver
  run begins

This keeps lineage and reconciliation clearer than scanning all raw runs
implicitly.

## 5. Outputs

The Silver design should use its own physical area under `data/silver/`.

Recommended output structure:

- final Silver dataset:
  - `data/silver/fcc/consumer_complaints/{source_run_id}/`
- Silver run metadata:
  - `data/silver/fcc/_metadata/{source_run_id}.json`
- reject/quarantine output:
  - `data/silver/fcc/_rejects/{source_run_id}/`
- validation/reporting artifacts:
  - `data/silver/fcc/_quality/{source_run_id}/`

This keeps:

- valid Silver output
- reject/quarantine output
- metadata
- quality reporting

physically separated but traceable through the same `source_run_id`.

## 6. Configuration Usage

The current repository already uses YAML configuration for raw
ingestion. Silver should follow that same pattern rather than
introducing `config.ini`.

Recommended configuration approach:

- add a Silver YAML template under `configs/`
- pass the config path through a CLI argument such as `--config`
- pass the selected raw run through a CLI parameter such as
  `--source-run-id` if not fully specified in config

Recommended configuration responsibilities:

- input raw root path
- Silver output root path
- reject output root path
- metadata output path
- quality output path
- runtime mode and overwrite policy

This keeps Silver configuration aligned with the Phase 3 operational
pattern.

## 7. Transformation Flow

High-level execution flow:

1. parse runtime arguments
2. load and validate Silver configuration
3. resolve the selected `source_run_id`
4. verify raw input directory and raw metadata availability
5. read raw page files for the selected run
6. apply Phase 4-3 transformation rules
7. separate valid candidate records from reject/quarantine records
8. apply deduplication to valid candidate records
9. apply dataset-level validation on the deduplicated Silver dataset
   according to Phase 4-4 rules
10. write final Silver output
11. write reject/quarantine output
12. write quality/reporting summary
13. write Silver run metadata
14. emit final run summary

This is an execution design only, not an implementation algorithm.

## 8. Validation Integration Points

Validation should occur at two explicit points:

- pre-output validation:
  - confirm candidate Silver records conform to schema expectations
- final-output validation:
  - confirm the persisted Silver dataset satisfies dataset-level quality
    expectations

Validation outputs should remain traceable to the same
`source_run_id`.

## 9. Reject Handling Integration Points

Reject handling should occur before final Silver persistence.

Expected integration points:

- during required-field enforcement
- during required type validation
- during schema-contract validation
- during Critical quality-rule enforcement

Reject handling should remain separate from deduplication handling:

- invalid records go to reject/quarantine
- valid but non-selected dedup candidates do not
- reject/quarantine routing must occur before deduplication for invalid
  records and must not include records excluded solely due to
  deduplication

## 10. Idempotency and Rerun Behavior

The execution design should be idempotent for the same raw input run and
the same approved rule set.

Expected behavior:

- the same `source_run_id` and the same transformation rules should
  yield the same Silver dataset, reject set, and validation outcomes
- rerunning should not create logically different results for identical
  inputs
- overwrite or replace behavior should be explicit and configuration
  controlled
- ordering of records during transformation must not affect final
  deterministic output

The recommended operational model is:

- one Silver output set per `source_run_id`
- deterministic replacement when rerun is intentionally executed for the
  same raw run

## 11. Logging Expectations

The Silver execution path should provide CLI-visible progress logging
similar in clarity to Phase 3.

Expected logging coverage:

- selected `source_run_id`
- raw files discovered
- records read
- candidate valid records
- reject counts
- final Silver row counts
- validation pass/fail summary
- output paths written
- metadata path written

Logs should support operational diagnosis without becoming a substitute
for formal metadata or quality reporting.

## 12. Out of Scope

This execution design does not define:

- transformation implementation code
- validation implementation code
- reject dataset physical schema details
- orchestration tooling beyond the repository execution structure
- scheduling, deployment, or CI/CD
- Gold-layer modeling or dashboard outputs
