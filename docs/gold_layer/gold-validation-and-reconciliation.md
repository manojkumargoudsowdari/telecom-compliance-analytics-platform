# Gold Validation and Reconciliation Framework

## 1. Purpose

This document defines the validation and reconciliation framework for
the Gold layer of the Telecom Compliance Analytics Platform (TCAP).

It establishes the deterministic quality controls required to verify
that Gold outputs are complete, internally consistent, and reconcilable
to upstream Silver inputs before dashboard consumption.

This framework applies only to the approved Gold facts:

- `fact_complaints_daily`
- `fact_complaints_monthly`

It is limited to validation and reconciliation design. It does not
define code, SQL, orchestration, or runtime execution behavior.

## 2. Validation Objectives

- validate that each Gold fact conforms to its approved grain
- validate that required keys and required measures are present
- validate that Gold counts and KPI values are sane and internally
  consistent
- reconcile daily Gold to the validated Silver complaint population
- reconcile monthly Gold to daily Gold
- ensure unknown-member rows are handled explicitly and auditable
- define deterministic failure conditions and expected validation
  artifacts

## 3. Validation Principles

- Deterministic:
  - identical inputs must produce identical validation outcomes
- Explicit:
  - every blocking and warning rule must be named and documented
- Reconciled:
  - Gold totals must tie back to approved upstream totals
- No silent data loss:
  - dropped or excluded records must be explainable through approved
    aggregation and unknown-member rules
- Grain-first:
  - validation must confirm the declared grain before KPI sanity checks
- Separation of concerns:
  - this document defines validation behavior, not transformation or
    pipeline mechanics

## 4. Daily Fact Validation Rules

### 4.1 Grain Uniqueness

The declared grain for `fact_complaints_daily` is:

- one row per `date_key`, `issue_key`, `method_key`, and `geography_key`

Required validation:

- no duplicate rows may exist for the same daily grain combination
- duplicate daily grain combinations are a blocking failure

### 4.2 Required-Key Presence

Required daily fact keys:

- `date_key`
- `issue_key`
- `method_key`
- `geography_key`

Required daily fact measure:

- `complaint_count`

Required validation:

- required keys must be present on every row
- `complaint_count` must be present on every row
- null required keys are a blocking failure
- null `complaint_count` is a blocking failure

### 4.3 `complaint_count` Sanity

Required validation:

- `complaint_count` must be non-negative
- `complaint_count` must be an integer-compatible count measure
- zero-count rows are not valid persisted Gold fact rows unless
  explicitly approved in a future design revision

Blocking failures:

- negative `complaint_count`
- non-integer count representation

### 4.4 Unknown-Member Handling

Unknown-member rows are valid daily Gold rows when they result from
approved dimension mapping behavior.

Required validation:

- unknown members must use deterministic approved dimension keys
- unknown-member rows must remain included in fact totals unless
  explicitly excluded by the same reconciliation filter context
- unknown-member rows must not be silently dropped

Blocking failures:

- null dimension key where an unknown-member key should exist
- unmapped missing dimension values that do not resolve to an approved
  unknown-member key

## 5. Monthly Fact Validation Rules

### 5.1 Grain Uniqueness

The declared grain for `fact_complaints_monthly` is:

- one row per `month_key`, `issue_key`, `method_key`, and
  `geography_key`

Required validation:

- no duplicate rows may exist for the same monthly grain combination
- duplicate monthly grain combinations are a blocking failure

### 5.2 Required-Key Presence

Required monthly fact keys:

- `month_key`
- `issue_key`
- `method_key`
- `geography_key`

Required monthly fact base measure:

- `complaint_count`

Required validation:

- required keys must be present on every row
- `complaint_count` must be present on every row
- null required keys are a blocking failure
- null `complaint_count` is a blocking failure

### 5.3 `complaint_count` Sanity

Required validation:

- `complaint_count` must be non-negative
- `complaint_count` must be an integer-compatible count measure
- zero-count rows are not valid persisted Gold fact rows unless
  explicitly approved in a future design revision

Blocking failures:

- negative `complaint_count`
- non-integer count representation

### 5.4 Non-Additive KPI Sanity Checks

Required validation applies to:

- `complaint_growth_rate`
- `category_share`
- `rolling_average_complaint_count`

Required validation:

- non-additive KPIs must be consistent with the approved monthly
  complaint totals
- non-additive KPIs must not be validated by summing lower-level derived
  KPI values
- null behavior must match the approved KPI catalog and aggregation
  rules

### 5.5 Rolling-Window Metadata Presence

Because `rolling_average_complaint_count` uses a parameterized but fixed
rolling window per dataset, monthly Gold validation must confirm that:

- the rolling-window definition is declared in metadata
- the window is fixed for the dataset being validated

Blocking failure:

- `rolling_average_complaint_count` is present but the rolling-window
  definition is missing from required metadata

## 6. Reconciliation Rules

## 6.1 Silver to Daily Gold Reconciliation

The daily Gold fact must reconcile to the validated Silver dataset for
the same business context.

Required reconciliation:

- daily `complaint_count` totals must reconcile to Silver complaint
  totals grouped by:
  - `date_created`
  - issue context
  - method context
  - geography context
- reconciliation must include unknown-member rows unless the exact same
  reporting filter context excludes them

Blocking failure:

- daily Gold totals do not reconcile to the Silver complaint population
  for the same filter and time context

## 6.2 Daily to Monthly Gold Reconciliation

The monthly Gold fact must reconcile to daily Gold and must not be
validated against a direct Silver-to-monthly shortcut path.

Required reconciliation:

- monthly `complaint_count` must equal the sum of daily
  `complaint_count` for the same:
  - month
  - issue context
  - method context
  - geography context

Blocking failure:

- monthly totals do not equal the corresponding aggregated daily totals

## 6.3 Filtered-Context Reconciliation

Reconciliation must hold not only for global totals but also for the
same filtered context used in reporting.

Required rule:

- when a time, issue, method, or geography filter is applied, Gold
  totals must reconcile to the corresponding upstream total under that
  same filtered context

This is required because approved KPIs, especially `category_share`,
depend on filtered-context correctness rather than only whole-dataset
totals.

## 6.4 Unknown-Member Inclusion in Reconciliation

Unknown-member rows are part of valid Gold totals.

Required rule:

- reconciliation summaries must include unknown-member rows by default
- if a reconciliation view excludes unknown members, that exclusion must
  be explicit and applied consistently on both sides of the comparison

## 7. KPI Sanity Rules

### 7.1 `complaint_count`

- must be non-negative
- must reconcile to the approved source fact totals

Blocking failures:

- negative values
- reconciliation mismatch

### 7.2 `category_share`

- must be between `0` and `1` inclusive when non-null
- must return null when denominator is `0`
- must be computed using the approved denominator rule:
  - same filtered context
  - preserve time filters
  - preserve non-category dimensions
  - remove only the active category dimension

Blocking failures:

- value outside `[0, 1]`
- non-null value when denominator is `0`
- denominator behavior inconsistent with the approved active-axis rule

### 7.3 `complaint_growth_rate`

- must return null when the previous comparable period is unavailable
- must return null when the previous comparable period count is `0`
- when non-null, it must reconcile to:
  - `(current_period_complaints - previous_period_complaints) / previous_period_complaints`

Blocking failures:

- non-null value in a zero-denominator context
- value inconsistent with approved formula

### 7.4 `period_over_period_change`

- must equal:
  - `current_period_count - previous_period_count`
- must return null when no previous comparable period exists
- must return null when either comparison-period count is unavailable

Blocking failures:

- value inconsistent with approved absolute-change formula
- non-null value when the prior comparable period does not exist

### 7.5 `rolling_average_complaint_count`

- must be computed only from approved monthly complaint totals
- must use the dataset's declared fixed rolling window
- early periods may use the available window only, consistent with the
  KPI catalog
- if no periods exist in the window, return null

Blocking failures:

- value inconsistent with the declared rolling window
- non-null value when no window periods exist

## 8. Failure Conditions

### Blocking Failures

The following conditions invalidate Gold output:

- grain duplication in daily or monthly facts
- missing required keys
- null required measures
- negative `complaint_count`
- unresolved missing dimension values where unknown-member mapping is
  required
- Silver-to-daily reconciliation failure
- daily-to-monthly reconciliation failure
- non-additive KPI values that violate approved formulas or null rules
- missing rolling-window metadata when rolling averages are present

### Warning-Only Conditions

The following conditions should be reported but do not automatically
invalidate output unless thresholds are later elevated by approved
design:

- unusually high unknown-member row share
- unusual distribution shifts across issue, method, or geography
- unusually sparse category participation in a monthly slice

### Informational Conditions

The following support observability only:

- count of unknown-member rows by dimension
- count of null-to-unknown mappings by dimension
- period coverage summary for rolling windows

## 9. Required Validation Outputs and Evidence Artifacts

Gold validation must produce deterministic evidence-ready outputs.

Required conceptual artifacts:

- counts summary
  - Silver source complaint count
  - daily Gold row count
  - monthly Gold row count
  - unknown-member row counts
- reconciliation summary
  - Silver to daily reconciliation status
  - daily to monthly reconciliation status
  - filtered-context reconciliation outcomes where applicable
- failed-check summary
  - blocking failures
  - warnings
  - informational findings
- metadata summary
  - validation timestamp
  - validated dataset names
  - applicable reporting periods
  - rolling-window definition, when applicable

These outputs must be suitable for inclusion in a later evidence pack
and audit trail.

## 10. Design Trade-Offs and Constraints

- strict reconciliation improves trust, but it requires disciplined
  handling of unknown-member rows across all Gold facts
- validating monthly facts through daily Gold improves auditability, but
  it intentionally forbids a simpler direct Silver-to-monthly shortcut
- non-additive KPI validation is more rigorous than count validation
  because it must confirm formula behavior, null behavior, and filtered
  context semantics

## 11. Acceptance Criteria

This task is complete only when:

- daily fact validation rules are explicit and deterministic
- monthly fact validation rules are explicit and deterministic
- both Gold facts have grain-level validation defined
- Silver to daily reconciliation rules are explicit
- daily to monthly reconciliation rules are explicit
- unknown-member handling is explicitly covered in both validation and
  reconciliation
- KPI sanity checks are defined for all approved non-additive KPIs
- blocking versus warning-only failures are defined
- required validation outputs and evidence expectations are documented
- no code, SQL, pipeline logic, or orchestration details are introduced
