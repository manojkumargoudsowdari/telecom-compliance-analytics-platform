# Phase 6 Semantic Model Design

## 1. Purpose

This document defines the Phase 6 reporting semantic model for the
Power BI layer of the Telecom Compliance Analytics Platform (TCAP).

The purpose of the semantic model is to expose the approved Gold facts
and approved KPI logic in a reporting-safe structure that supports:

- trend analysis
- descriptive anomaly identification
- leadership-level reporting
- statistically correct KPI consumption

This document is architecture-focused only. It does not define Power BI
files, DAX, report pages, or implementation steps.

## 2. Architectural Role

The semantic model is the reporting layer above the completed Gold
layer.

Current layer responsibilities:

- Raw:
  - source capture
- Silver:
  - canonical validated complaint record
- Gold:
  - reporting-ready aggregated facts and Gold-owned KPI contracts
- Phase 6 semantic model:
  - expose Gold facts and approved reporting dimensions safely for
    Power BI consumption
  - enforce grain-aware metric usage
  - prevent incorrect aggregation of non-additive KPIs

The semantic model must consume Gold outputs as the final analytical
source. It must not bypass Gold by querying Silver directly for
reporting logic.

## 3. Confirmed Gold Inputs

Confirmed Gold facts available from the repository:

- `fact_complaints_daily`
  - grain:
    - one row per `date_key`, `issue_key`, `method_key`, and
      `geography_key`
  - persisted measure:
    - `complaint_count`

- `fact_complaints_monthly`
  - grain:
    - one row per `month_key`, `issue_key`, `method_key`, and
      `geography_key`
  - persisted measures:
    - `complaint_count`
    - `complaint_growth_rate`
    - `rolling_average_complaint_count`

Confirmed Gold KPI contract:

- `category_share` is Gold-defined
- `category_share` is not persisted as a physical Gold column in the
  first implementation
- `category_share` must be computed in the reporting layer from monthly
  fact counts while preserving the approved Gold denominator rules

## 4. Candidate Semantic Fact Tables

### 4.1 `FactComplaintsDaily`

- Semantic source:
  - `data/gold/fact_complaints_daily/`
- Reporting role:
  - daily trend analysis
  - daily exception review
  - base daily count context for anomaly-focused visuals
- Grain:
  - one row per `date_key`, `issue_key`, `method_key`, and
    `geography_key`
- Approved measure exposed directly:
  - `complaint_count`
- Reporting-layer derived metric support:
  - inputs for `period_over_period_change`

### 4.2 `FactComplaintsMonthly`

- Semantic source:
  - `data/gold/fact_complaints_monthly/`
- Reporting role:
  - executive monthly reporting
  - issue, method, and geography monthly comparisons
  - monthly trend smoothing
  - monthly KPI visuals
- Grain:
  - one row per `month_key`, `issue_key`, `method_key`, and
    `geography_key`
- Approved measures exposed directly:
  - `complaint_count`
  - `complaint_growth_rate`
  - `rolling_average_complaint_count`
- Reporting-layer derived metric support:
  - `category_share`

## 5. Candidate Dimension Tables

The approved Gold design defines conformed dimensions:

- `dim_date`
- `dim_issue`
- `dim_method`
- `dim_geography`

For the semantic model, the following dimension roles are required for
reporting support by the approved Phase 2 and Phase 5 documents.

Important boundary:

- these dimensions are required semantically for reporting
- this document does not assume they already exist as separate physical
  Gold outputs
- the implementation path remains subject to validation and may take
  one of the following forms:
  - separate imported dimension tables
  - derived semantic tables
  - future Gold dimension outputs

### 5.1 `DimDateDaily`

- Role:
  - filter and organize `FactComplaintsDaily`
- Key:
  - `date_key`
- Purpose:
  - day-level trend navigation and daily time filtering

### 5.2 `DimDateMonthly`

- Role:
  - filter and organize `FactComplaintsMonthly`
- Key:
  - `month_key`
- Purpose:
  - month-level trend navigation and monthly KPI filtering

### 5.3 `DimIssue`

- Role:
  - support issue-focused and issue-type reporting
- Confirmed semantic scope from repo docs:
  - `issue`
  - `issue_type`
- Join key:
  - `issue_key`

### 5.4 `DimMethod`

- Role:
  - support method analysis and method-based filtering
- Confirmed semantic scope from repo docs:
  - `method`
- Join key:
  - `method_key`

### 5.5 `DimGeography`

- Role:
  - support geography analysis with `state` as the primary level
- Confirmed semantic scope from repo docs:
  - `state`
  - `city`
  - `zip_code`
- Join key:
  - `geography_key`

## 6. Relationship Design and Filter Direction

Approved semantic-model relationship pattern:

- star-schema orientation
- dimensions filter facts
- no direct fact-to-fact relationship
- no bidirectional filtering by default

Recommended relationship pattern:

- `DimDateDaily` -> `FactComplaintsDaily`
  - key:
    - `date_key`
  - filter direction:
    - single direction from dimension to fact

- `DimDateMonthly` -> `FactComplaintsMonthly`
  - key:
    - `month_key`
  - filter direction:
    - single direction from dimension to fact

- `DimIssue` -> `FactComplaintsDaily`
  - key:
    - `issue_key`
  - filter direction:
    - single direction from dimension to fact

- `DimIssue` -> `FactComplaintsMonthly`
  - key:
    - `issue_key`
  - filter direction:
    - single direction from dimension to fact

- `DimMethod` -> `FactComplaintsDaily`
  - key:
    - `method_key`
  - filter direction:
    - single direction from dimension to fact

- `DimMethod` -> `FactComplaintsMonthly`
  - key:
    - `method_key`
  - filter direction:
    - single direction from dimension to fact

- `DimGeography` -> `FactComplaintsDaily`
  - key:
    - `geography_key`
  - filter direction:
    - single direction from dimension to fact

- `DimGeography` -> `FactComplaintsMonthly`
  - key:
    - `geography_key`
  - filter direction:
    - single direction from dimension to fact

This design prevents ambiguous cross-filter behavior and avoids mixing
daily and monthly facts through direct relationships.

## 7. Rationale for Separate Daily and Monthly Time Dimensions

Separate daily and monthly time dimensions are recommended for the
semantic model even though Gold defines a single logical `dim_date`
concept.

Rationale:

- `FactComplaintsDaily` and `FactComplaintsMonthly` have different time
  grains
- a single time table joined carelessly to both facts can encourage
  incorrect day-to-month comparisons and ambiguous filter behavior
- monthly-only KPIs such as `complaint_growth_rate` and
  `rolling_average_complaint_count` should be controlled by a monthly
  calendar context
- daily trend visuals should remain isolated from monthly KPI visuals
  unless explicitly designed together

This is a semantic-model safety rule, not a Gold redesign.

## 8. Metric Governance Rules

### Additive Metric

- `complaint_count`
  - additive within the approved fact grain and filter context

### Non-Additive Metrics

- `complaint_growth_rate`
- `rolling_average_complaint_count`
- `category_share`

Required semantic-model rule:

- non-additive metrics must not be aggregated by summing or averaging
  precomputed values across unrelated grouped outputs
- they must be recomputed from the correct fact-level
  `complaint_count` context at the reporting grain required by the KPI

Specific implications:

- `complaint_growth_rate` is monthly-only
- `rolling_average_complaint_count` is monthly-only and uses the fixed
  calendar-month window defined in Gold metadata
- `category_share` must be derived from monthly `complaint_count` within
  the approved filtered context and active category axis

### Conditional KPI Scope: `period_over_period_change`

`period_over_period_change` remains present in prior Phase 2 and Phase 5
design documents, but it is not part of the currently confirmed Gold
persisted metric set named for this Phase 6 implementation kickoff.

For semantic-model control, it should be treated as conditionally in
scope pending explicit KPI-contract confirmation in the next task.

Current rule:

- do not treat `period_over_period_change` as a locked committed
  semantic-model KPI yet
- if confirmed later, it should be derived from daily
  `complaint_count` only and must remain grain-safe

## 9. `category_share` Reporting-Layer Contract

`category_share` must remain a reporting-layer KPI in Phase 6.

Confirmed contract from repo docs:

- source:
  - `FactComplaintsMonthly`
- numerator:
  - `complaint_count` for the selected category value
- denominator:
  - sum of `complaint_count` over the same filtered context excluding
    only the active category dimension
- active category axes supported:
  - issue
  - method
  - geography
- time filters must be preserved
- all non-category filters must be preserved

The semantic model must not introduce separate persisted issue-share,
method-share, or geography-share columns.

## 10. Semantic Model Guardrails

The semantic model must enforce the following guardrails:

- do not join daily and monthly facts directly
- a single visual must never blend daily and monthly facts
- mixed-grain report pages are allowed only when each visual remains
  grain-pure
- do not expose monthly-only KPIs in daily-grain contexts
- do not allow non-additive KPIs to roll up from precomputed values
- do not treat all FCC raw attributes as semantic-model dimensions
- keep `state` as the primary geography analysis level
- use `city` with caution, consistent with Phase 2 and Phase 5 guidance
- leadership pages should default to state-level geography
- `city` and `zip_code` should be treated as secondary exploratory
  filters only when data completeness supports them
- keep weekly reporting out of scope in the first semantic-model build
- preserve unknown-member buckets so totals remain reconcilable to Gold
- keep reporting logic aligned to the approved Gold KPI contracts rather
  than redefining business formulas in visuals ad hoc

## 11. Open Validation Checks Before Implementation

The following items are not sufficiently defined in the repo for safe
semantic-model implementation and should be validated before build:

### 11.1 Physical Dimension Availability

Phase 5 documents define logical conformed dimensions, but the Gold
implementation persists fact outputs only.

Validation needed:

- confirm whether `DimIssue`, `DimMethod`, and `DimGeography` will be
  materialized from distinct keys in the semantic layer
- confirm whether future Gold dimension outputs will be provided, or
  whether the semantic model will derive display attributes from the
  persisted fact keys

### 11.2 Key Decomposition Rules

The persisted Gold facts currently expose:

- `issue_key`
- `method_key`
- `geography_key`

Validation needed:

- confirm that parsing these keys into reporting attributes is an
  approved implementation path
- confirm the stable parsing contract for:
  - `issue_type`
  - `issue`
  - `method`
  - `state`
  - `city`
  - `zip_code`

### 11.3 Daily Versus Monthly Visual Boundaries

Phase 2 Page 5 intentionally combines daily and monthly analytical
needs.

Validation needed:

- confirm which visuals will use `FactComplaintsDaily`
- confirm which visuals will use `FactComplaintsMonthly`
- confirm that report layout will prevent accidental grain mixing

### 11.4 `period_over_period_change` KPI Confirmation

Prior repo docs reference `period_over_period_change`, but the current
Phase 6 implementation kickoff is more tightly scoped around the
confirmed persisted Gold outputs plus reporting-layer `category_share`.

Validation needed:

- confirm whether `period_over_period_change` remains in the approved
  Phase 6 semantic-model KPI set
- if confirmed, lock it explicitly as a daily reporting-layer
  calculation derived from `FactComplaintsDaily`
- confirm that it is not introduced implicitly into monthly or
  mixed-grain visuals

## 12. Conclusion

The repo documentation is sufficient to define a safe semantic-model
architecture for Phase 6, provided the implementation respects the
approved Gold grains, approved KPI contracts, and reporting guardrails.

The semantic model should remain intentionally conservative:

- two fact tables
- separate daily and monthly time dimensions
- conformed issue, method, and geography filtering
- reporting-layer computation for `category_share`
- strict protection against misuse of non-additive KPIs

This design stays within the bounds of the completed Phase 2 and Phase 5
artifacts and does not assume unsupported reporting fields or new Gold
outputs.
