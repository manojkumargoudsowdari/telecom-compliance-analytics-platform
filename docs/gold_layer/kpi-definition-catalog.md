# Gold Layer KPI Definition Catalog

## 1. Purpose

This document defines the approved KPI catalog for the Gold layer of
the Telecom Compliance Analytics Platform (TCAP).

It is derived strictly from the Phase 2 source-of-truth documents:

- `docs/phase2-analytics-requirements.md`
- `docs/phase2-kpi-definitions.md`
- `docs/phase2-dashboard-design.md`

It also aligns KPI field usage to the approved Phase 4 Silver schema
contract documented in:

- `docs/phase4/phase4-2-silver-schema-contract.md`

This catalog defines KPI behavior only. It does not define table
schemas, pipeline implementation, SQL, Power BI measures, or visual
formatting implementation.

## 2. KPI Categories

### Volume Metrics

- `complaint_count`

### Distribution Metrics

- `category_share`

### Trend Metrics

- `complaint_growth_rate`
- `period_over_period_change`
- `rolling_average_complaint_count`

## 3. KPI Hierarchy and Inventory

### Base KPI

- `complaint_count`

`complaint_count` is the base KPI used across all approved Gold
reporting cuts:

- time
- issue
- method
- geography

All other approved KPIs in this catalog are derived from
`complaint_count`.

### Derived KPIs

- `complaint_growth_rate`
- `category_share`
- `period_over_period_change`
- `rolling_average_complaint_count`

### Share KPI Distinction

The share logic is normalized into a single KPI:

- `category_share`

`category_share` is a parameterized share KPI where the reporting
category axis is explicitly declared by the dataset or consuming model.

Examples:

- `category = issue`
- `category = method`
- `category = geography`

This consolidation removes redundant share formulas while preserving the
Phase 2 reporting intent for:

- issue concentration
- method mix
- geography share comparisons

Implementation contract for the first Gold build:

- `category_share` is a Gold-defined KPI derived from
  `fact_complaints_monthly` `complaint_count` within the approved
  filtered context
- `category_share` is not persisted as a separate physical column in the
  first Gold implementation
- `category_share` is computed in reporting or query consumption from
  monthly fact counts while preserving Gold-owned business logic

## 4. KPI Definitions

### 3.1 `complaint_count`

- KPI Name:
  - `complaint_count`
- KPI Role:
  - base
- Business Definition:
  - total number of complaints in the active reporting context
- Source Fields:
  - `complaint_id`
  - `date_created`
  - applicable reporting dimensions from Silver:
    - `issue_type`
    - `method`
    - `issue`
    - `city`
    - `state`
    - `zip_code`
- Calculation Logic:
  1. start from the validated Silver complaint population
  2. apply the active date and dimension filters
  3. count complaints at the selected Gold reporting grain
  4. use `complaint_id` as the counting key
- Numerator:
  - `COUNT(complaint_id)` in the active reporting context
- Denominator:
  - not applicable
- Zero-Denominator Behavior:
  - not applicable
- Grain:
  - daily
  - monthly
- Applicable Dimensions:
  - `date_created`
  - `issue_type`
  - `method`
  - `issue`
  - `city`
  - `state`
  - `zip_code`
- Filter Behavior:
  - affected by all active report filters on the fields above
- Null Handling Rules:
  - records without `complaint_id` do not enter Silver and therefore do
    not enter the KPI population
  - records with null optional dimensions remain countable unless the
    filtered dimension specifically excludes nulls
- Aggregation Behavior:
  - additive across time and dimensions when no duplicate counting path
    is introduced
  - child groups should sum to the parent total within the same filter
    context
- Additivity:
  - additive
- Dimensional Applicability:
  - time:
    - valid
  - issue:
    - valid
  - method:
    - valid
  - geography:
    - valid
- Reconciliation Expectation:
  - must reconcile to Silver complaint totals for the same date window
    and dimension filters
- Phase 2 Requirement Mapping:
  - `AR-01`
  - `AR-02`
  - `AR-03`
  - `AR-04`
  - `AR-05`
  - `AR-06`
  - `AR-07`
- Dashboard Mapping:
  - Page 1: Compliance Overview
  - Page 2: Issue Type and Method Analysis
  - Page 3: Issue Category Analysis
  - Page 4: Geographic Analysis
  - Page 5: Trend and Anomaly Monitoring

### 3.2 `complaint_growth_rate`

- KPI Name:
  - `complaint_growth_rate`
- KPI Role:
  - derived
- Business Definition:
  - relative change in complaint count between the current reporting
    period and the previous comparable period
- Change Type:
  - percentage
- Source Fields:
  - `complaint_id`
  - `date_created`
  - applicable dimensions:
    - `issue_type`
    - `method`
    - `issue`
    - `state`
    - `city`
- Calculation Logic:
  1. determine the current reporting period at the active grain
  2. calculate `complaint_count` for the current period
  3. determine the immediately previous comparable period at the same
     grain
  4. calculate `complaint_count` for the previous period
  5. compute:
     - `(current_period_complaints - previous_period_complaints) / previous_period_complaints`
- Numerator:
  - `current_period_complaints - previous_period_complaints`
- Denominator:
  - `previous_period_complaints`
- Zero-Denominator Behavior:
  - if `previous_period_complaints = 0`, return null
- Grain:
  - monthly
- Applicable Dimensions:
  - `issue_type`
  - `method`
  - `issue`
  - `state`
  - `city`
- Filter Behavior:
  - affected by active filters on the applicable dimensions
  - date filter defines the comparison window and visible periods
  - current-period and previous-period totals must be calculated under
    identical non-time filters
- Null Handling Rules:
  - if `previous_period_complaints = 0`, return null rather than divide
    by zero
  - if either comparison period is not available, return null
  - null optional dimensions do not invalidate the KPI if the records
    remain in the selected filter context
- Aggregation Behavior:
  - not additive across periods
  - must be recomputed from period complaint totals at each visible
    reporting slice
- Additivity:
  - non-additive
- Dimensional Applicability:
  - time:
    - valid at monthly grain only
  - issue:
    - valid
  - method:
    - valid
  - geography:
    - valid
- Reconciliation Expectation:
  - numerator and denominator inputs must reconcile to the corresponding
    monthly Silver-based complaint totals for the same dimension filters
- Phase 2 Requirement Mapping:
  - `AR-01`
  - `AR-07`
- Dashboard Mapping:
  - Page 1: Compliance Overview
  - Page 5: Trend and Anomaly Monitoring

### 3.3 `category_share`

- KPI Name:
  - `category_share`
- KPI Role:
  - derived
- Business Definition:
  - percentage share of complaint volume for the selected reporting
    category relative to total complaints in the same reporting context
- Source Fields:
  - `complaint_id`
  - `date_created`
  - category dimensions:
    - `issue`
    - `issue_type`
    - `method`
    - `state`
    - `city`
    - `zip_code`
- Calculation Logic:
  1. calculate `complaint_count` for the selected category value within
     the current filter context
  2. calculate total complaint count for the same filter context
  3. remove only the category axis being compared from the denominator
  4. compute:
     - `category_complaint_count / total_complaint_count_in_filter_context`
- Numerator:
  - complaint count for the selected category value in the active
    reporting context
- Denominator:
  - total complaint count in the same reporting context after removing
    only the category axis being compared
- Zero-Denominator Behavior:
  - if denominator total is `0`, return null
- Grain:
  - daily
  - monthly
- Applicable Dimensions:
  - `issue`
  - `issue_type`
  - `method`
  - `state`
  - `city`
  - `zip_code`
- Filter Behavior:
  - affected by active filters on:
    - `date_created`
    - `issue`
    - `issue_type`
    - `method`
    - `state`
    - `city`
    - `zip_code`
  - denominator preserves report filters and removes only the category
    grouping being compared
  - denominator must not remove time filters, issue filters, method
    filters, or geography filters other than the single category axis
    being evaluated
- Null Handling Rules:
  - null category values are excluded from category-specific share rows
    unless a report explicitly includes a null bucket
  - if the denominator total is `0`, return null
- invalid comparison contexts return null rather than a forced numeric
  value
- Aggregation Behavior:
  - not additive across categories
  - category shares should sum to 100 percent only within the same
    defined filter context
- Additivity:
  - non-additive
- Dimensional Applicability:
  - time:
    - valid
  - issue:
    - valid when `category = issue`
  - method:
    - valid when `category = method`
  - geography:
    - valid when `category = state`, `city`, or `zip_code`
- Reconciliation Expectation:
  - category numerator and denominator totals must reconcile to Silver
    complaint totals for the same reporting context
- Phase 2 Requirement Mapping:
  - `AR-02`
  - `AR-03`
  - `AR-07`
- Dashboard Mapping:
  - Page 1: Compliance Overview when `category = issue`
  - Page 2: Issue Type and Method Analysis when `category = issue_type` or `method`
  - Page 3: Issue Category Analysis
  - Page 4: Geographic Analysis when `category = state`, `city`, or `zip_code`

### 3.4 `period_over_period_change`

- KPI Name:
  - `period_over_period_change`
- KPI Role:
  - derived
- Business Definition:
  - absolute change in complaint count between the current reporting
    period and the previous comparable period
- Change Type:
  - absolute
- Source Fields:
  - `complaint_id`
  - `date_created`
  - applicable dimensions:
    - `issue`
    - `issue_type`
    - `method`
    - `state`
    - `city`
- Calculation Logic:
  1. determine the current reporting period at the active grain
  2. calculate `complaint_count` for the current period
  3. determine the immediately previous comparable period at the same
     grain
  4. calculate `complaint_count` for the previous period
  5. compute:
     - `current_period_complaints - previous_period_complaints`
- Numerator:
  - `current_period_complaints - previous_period_complaints`
- Denominator:
  - not applicable
- Zero-Denominator Behavior:
  - not applicable
- Grain:
  - daily
  - monthly
- Applicable Dimensions:
  - `issue`
  - `issue_type`
  - `method`
  - `state`
  - `city`
- Filter Behavior:
  - affected by active filters on:
    - `issue`
    - `issue_type`
    - `method`
    - `state`
    - `city`
    - `zip_code`
  - date filter determines visible periods and comparison scope
  - current-period and previous-period totals must be calculated under
    identical non-time filters
- Null Handling Rules:
  - if the prior-period complaint count is absent because the prior
    period is not available, return null
  - optional dimension nulls do not invalidate the KPI unless filtered
    out
- Aggregation Behavior:
  - not additive across time periods
  - must be recalculated at each reporting slice from period totals
- Additivity:
  - non-additive
- Dimensional Applicability:
  - time:
    - valid
  - issue:
    - valid
  - method:
    - valid
  - geography:
    - valid
- Reconciliation Expectation:
  - both current-period and prior-period complaint totals must reconcile
    to Silver counts for the same filters and period definitions
- Phase 2 Requirement Mapping:
  - `AR-05`
  - `AR-06`
- Dashboard Mapping:
  - Page 3: Issue Category Analysis
  - Page 5: Trend and Anomaly Monitoring

### 3.5 `rolling_average_complaint_count`

- KPI Name:
  - `rolling_average_complaint_count`
- KPI Role:
  - derived
- Business Definition:
  - smoothed moving average of complaint count across recent reporting
    periods
- Source Fields:
  - `complaint_id`
  - `date_created`
  - applicable dimensions:
    - `issue`
    - `issue_type`
    - `method`
    - `state`
- Calculation Logic:
  1. choose the approved reporting grain
  2. identify the fixed trailing calendar-month window ending in the
     current month
  3. calculate `complaint_count` for each month in that window
  4. treat any missing month in the window as a zero-complaint month
  5. sum complaint counts across the full calendar-month window
  6. divide by the fixed number of months in that window
  5. compute:
     - `AVERAGE(complaint_count over trailing N periods)`
- Rolling Window Rule:
  - the rolling window is parameterized but fixed per dataset
  - the selected window definition must be declared in dataset metadata
  - the rolling window must not vary dynamically within the same
    persisted dataset
  - the window is calendar-month based, not based on the last `N`
    observed monthly rows
  - missing months inside the window count as zero complaint months
- Numerator:
  - sum of period complaint counts across the trailing window
- Denominator:
  - number of periods included in the trailing window
- Zero-Denominator Behavior:
  - if no periods exist in the window, return null
- Grain:
  - monthly
- Applicable Dimensions:
  - `issue`
  - `issue_type`
  - `method`
  - `state`
- Filter Behavior:
  - affected by active filters on:
    - `issue`
    - `issue_type`
    - `method`
    - `state`
    - `city`
    - `zip_code`
  - date filter determines the visible rolling window sequence
  - rolling window periods must be evaluated under identical non-time
    filters
- Null Handling Rules:
  - early periods with incomplete history remain valid and use the full
    fixed calendar-month window, with pre-history months treated as
    zero-complaint months
  - if the dataset contains no current-month row, no KPI row exists for
    that slice
- Aggregation Behavior:
  - not additive across periods
  - must be recomputed from the underlying monthly complaint totals
- Additivity:
  - non-additive
- Dimensional Applicability:
  - time:
    - valid at monthly grain only
  - issue:
    - valid
  - method:
    - valid
  - geography:
    - valid
- Reconciliation Expectation:
  - each period-level complaint count used in the rolling window must
    reconcile to Silver totals for the same dimension filters
- Phase 2 Requirement Mapping:
  - `AR-06`
- Dashboard Mapping:
  - Page 3: Issue Category Analysis
  - Page 5: Trend and Anomaly Monitoring

## 5. Requirement Mapping Summary

| KPI | Phase 2 Requirements |
| --- | --- |
| `complaint_count` | `AR-01`, `AR-02`, `AR-03`, `AR-04`, `AR-05`, `AR-06`, `AR-07` |
| `complaint_growth_rate` | `AR-01`, `AR-07` |
| `category_share` | `AR-02`, `AR-03`, `AR-07` |
| `period_over_period_change` | `AR-05`, `AR-06` |
| `rolling_average_complaint_count` | `AR-06` |

## 6. AR-07 Coverage Confirmation

`AR-07` asks for a concise leadership narrative covering complaint
concentration, trend direction, and the most prominent risk themes in
the FCC data.

The approved KPI coverage for `AR-07` is:

- `complaint_count`
- `complaint_growth_rate`
- `category_share` with `category = issue`

This is sufficient to satisfy the KPI requirement stated in Phase 2 for
the executive summary and narrative view.

`period_over_period_change` and `rolling_average_complaint_count`
support the broader trend and anomaly analysis requirements in:

- `AR-05`
- `AR-06`

They are analytically useful for deeper monitoring, but they are not
required to satisfy `AR-07` because Phase 2 does not list them as
required KPIs for that requirement.

## 7. Ambiguities and Conflicts Found in Source Documents

### 5.1 Date Grain Conflict

`AR-05` references week or month for anomaly-oriented analysis, but the
approved Phase 5 Gold architecture currently supports daily and monthly
only.

Locked resolution for this catalog:

- daily and monthly are the only supported Gold KPI grains in the first
  implementation boundary
- weekly is treated as a future extension, not part of this KPI catalog

### 5.2 Field Naming Alignment

Phase 2 references source-style names such as:

- `id`
- `ticket_created`
- `zip`

Phase 4 Silver exposes the approved canonical names:

- `complaint_id`
- `ticket_created_utc`
- `zip_code`

Locked resolution for this catalog:

- KPI definitions use the approved Silver names only

### 5.3 Canonical Reporting Date

Phase 2 identifies `date_created` as the leading reporting-date
candidate and notes that it should be validated against `ticket_created`
or `ticket_created_utc`.

Locked resolution for this catalog:

- Gold KPI definitions use `date_created` as the canonical reporting
  date, consistent with the approved Phase 5 architecture scope

### 5.4 Power BI Versus Gold Responsibility

Phase 2 notes that the KPI set is intended for later Power BI measures.
Phase 5 architecture now places KPI base logic responsibility in Gold.

Locked resolution for this catalog:

- Power BI remains the presentation and consumption layer
- KPI business definitions and base calculation logic belong to Gold
