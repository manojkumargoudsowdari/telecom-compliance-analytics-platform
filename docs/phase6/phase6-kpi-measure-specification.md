# Phase 6 KPI and Measure Specification

## 1. Purpose

This document defines the Phase 6 KPI and measure specification for the
Power BI reporting layer of the Telecom Compliance Analytics Platform
(TCAP).

It translates the approved Phase 2 KPI requirements and the completed
Phase 5 Gold KPI contracts into a reporting-safe measure specification
for the semantic model.

This document is limited to KPI and measure behavior. It does not define
DAX, Power BI files, Gold transformations, or report implementation.

## 2. Confirmed Inputs

Confirmed Gold inputs available for reporting:

- `fact_complaints_daily`
  - `complaint_count`

- `fact_complaints_monthly`
  - `complaint_count`
  - `complaint_growth_rate`
  - `rolling_average_complaint_count`

Confirmed reporting-layer KPI:

- `category_share`
  - Gold-defined
  - not persisted physically in Gold
  - computed in the reporting layer from monthly fact counts

## 3. KPI Inventory

### Confirmed KPIs

- `complaint_count`
- `complaint_growth_rate`
- `category_share`
- `rolling_average_complaint_count`

### Validation Item

- `period_over_period_change`
  - referenced in Phase 2 and Phase 5 documents
  - not currently part of the explicitly confirmed persisted Gold metric
    set named for the Phase 6 implementation kickoff
  - must be validated before it is treated as a locked reporting-layer
    KPI

## 4. KPI Specifications

### 4.1 `complaint_count`

- Business Definition:
  - total number of complaints in the active reporting context
- Source:
  - `fact_complaints_daily.complaint_count`
  - `fact_complaints_monthly.complaint_count`
- Calculation Logic:
  - sum complaint counts at the active fact grain and filter context
- Numerator:
  - complaint count total in scope
- Denominator:
  - not applicable
- Grain:
  - daily
  - monthly
- Classification:
  - additive
- Filter Context Behavior:
  - respects the active time, issue, method, and geography filters
- Allowed Aggregations:
  - sum within the same fact grain
- Disallowed Aggregations:
  - blending daily and monthly values inside the same visual
- Recommended Visual Usage:
  - KPI cards
  - trend lines
  - ranked bar charts
  - tables
  - maps

### 4.2 `complaint_growth_rate`

- Business Definition:
  - relative change in monthly complaint count between the current month
    and the immediately previous comparable month
- Source:
  - `fact_complaints_monthly.complaint_growth_rate`
- Calculation Logic:
  - `(current_month_complaints - previous_month_complaints) / previous_month_complaints`
- Numerator:
  - `current_month_complaints - previous_month_complaints`
- Denominator:
  - `previous_month_complaints`
- Grain:
  - monthly only
- Classification:
  - non-additive
- Filter Context Behavior:
  - must be evaluated under identical non-time filters for both current
    and previous months
- Source-of-Truth Rule:
  - reporting must treat the Gold persisted value as the source of truth
  - the conceptual formula is explanatory and must not be used to
    redefine the KPI independently in the reporting layer
- Allowed Aggregations:
  - use only at the native monthly fact grain
- Disallowed Aggregations:
  - summing monthly growth-rate values
  - averaging monthly growth-rate values across unrelated grouped
    outputs as if they were additive
  - exposing the KPI in daily-grain visuals
- Recommended Visual Usage:
  - executive KPI cards
  - monthly trend comparison visuals
  - leadership summary pages

### 4.3 `category_share`

- Business Definition:
  - percentage share of complaint volume for the selected category value
    relative to total complaints in the same filtered monthly context
- Source:
  - derived from `fact_complaints_monthly.complaint_count`
- Calculation Logic:
  1. identify the active category axis
  2. calculate complaint count for the selected category value
  3. calculate total complaint count in the same filtered context
  4. remove only the active category axis from the denominator
  5. divide numerator by denominator
- Numerator:
  - monthly `complaint_count` for the selected category value
- Denominator:
  - sum of monthly `complaint_count` over the same filtered context
    excluding only the active category dimension
- Grain:
  - monthly only for the first reporting implementation
- Classification:
  - non-additive
- Active Category Axes:
  - issue
  - method
  - geography
- Validity Rule:
  - `category_share` is valid only on visuals where exactly one
    supported category axis is active for the share calculation
- Filter Context Behavior:
  - preserve time filters
  - preserve all non-category filters
  - remove only the active category axis from the denominator
- Allowed Aggregations:
  - evaluate per monthly reporting context and active category axis
- Disallowed Aggregations:
  - summing category-share values across categories
  - persisting separate issue-share, method-share, or geography-share
    columns in the semantic model
  - using a denominator that removes more than the active category axis
- Recommended Visual Usage:
  - issue concentration charts
  - method mix visuals
  - geography share comparisons
  - executive narrative support visuals

### 4.4 `rolling_average_complaint_count`

- Business Definition:
  - smoothed monthly moving average of complaint count across the fixed
    trailing calendar-month window
- Source:
  - `fact_complaints_monthly.rolling_average_complaint_count`
- Calculation Logic:
  - average monthly complaint counts across the fixed calendar-month
    window defined in Gold metadata
- Numerator:
  - sum of complaint counts across the trailing calendar-month window
- Denominator:
  - fixed number of months in the declared window
- Grain:
  - monthly only
- Classification:
  - non-additive
- Filter Context Behavior:
  - must be evaluated under identical non-time filters across the full
    rolling window
- Allowed Aggregations:
  - use only at the native monthly fact grain
- Disallowed Aggregations:
  - summing rolling-average values across months
  - averaging precomputed rolling-average values across unrelated
    grouped outputs as if they were additive
  - exposing the KPI in daily-grain visuals
- Recommended Visual Usage:
  - smoothed trend lines
  - persistence-versus-spike views
  - anomaly-monitoring overlays

## 5. Edge Cases

### Zero Values

- `complaint_count`
  - zero-count persisted fact rows are not expected in the current Gold
    contract
- `complaint_growth_rate`
  - if the previous month complaint count is `0`, return null
- `category_share`
  - if the denominator is `0`, return null
- `rolling_average_complaint_count`
  - zero-complaint months inside the rolling window remain valid inputs

### Missing Months

- `complaint_growth_rate`
  - if the previous comparable month is unavailable, return null
- `rolling_average_complaint_count`
  - the current Gold implementation and Gold KPI contract define the
    rolling window as calendar-month based
  - missing months inside the window are treated as zero-complaint
    months
  - early months in the series therefore use zero-filled pre-history
    months inside the fixed window

### Sparse Categories

- `category_share`
  - sparse category participation is valid
  - share must still be computed against the full filtered monthly
    denominator after removing only the active category axis
- all non-additive KPIs
  - sparse dimensional slices must not be rolled up from precomputed KPI
    values

## 6. Allowed and Disallowed Measure Usage Rules

### Allowed

- use `complaint_count` as the additive base measure
- use `complaint_growth_rate` only in monthly visuals
- use `rolling_average_complaint_count` only in monthly visuals
- compute `category_share` from monthly `complaint_count`
- keep each visual grain-pure

### Disallowed

- blending daily and monthly facts in a single visual
- summing or averaging non-additive KPI values as if they were additive
- redefining Gold-owned KPI business logic independently in visuals
- treating all FCC raw attributes as reportable dimensions

## 7. Recommended Visual Usage Summary

| KPI | Recommended Usage |
| --- | --- |
| `complaint_count` | executive-safe: KPI cards, monthly trend summaries, state comparisons; analyst/exploratory: detailed rankings, maps, and drilldown tables |
| `complaint_growth_rate` | executive-safe: monthly summary cards and trend comparisons; analyst/exploratory: monthly exception review visuals |
| `category_share` | executive-safe: top-category concentration summaries; analyst/exploratory: issue, method, and geography share breakdowns where exactly one active category axis is used |
| `rolling_average_complaint_count` | executive-safe: monthly smoothed trend summaries; analyst/exploratory: persistence-versus-spike and anomaly-monitoring visuals |
| `period_over_period_change` | validation item only pending KPI-contract confirmation |

## 8. KPI Validation Checklist

Before semantic-model implementation, confirm the following for each KPI:

- the KPI is explicitly approved in Phase 2 and Phase 5 documents
- the KPI grain is locked as daily or monthly
- numerator and denominator behavior are documented
- null and zero handling are documented
- additive versus non-additive classification is explicit
- filter-context behavior is explicit
- allowed and disallowed aggregations are explicit
- visual usage matches the approved dashboard scope
- the KPI does not require unsupported Gold fields or new datasets

Additional checklist items:

- confirm `category_share` uses the approved active-axis denominator rule
- confirm `rolling_average_complaint_count` uses the fixed
  calendar-month window from Gold
- confirm `complaint_growth_rate` is never exposed in daily-grain
  visuals
- confirm `period_over_period_change` before including it in the
  semantic-model KPI set

## 9. Conclusion

The confirmed Phase 6 reporting KPI set is intentionally conservative
and fully grounded in the completed Gold implementation:

- `complaint_count`
- `complaint_growth_rate`
- `category_share`
- `rolling_average_complaint_count`

This specification preserves statistical correctness by keeping
`complaint_count` as the additive base measure and by preventing
incorrect aggregation of non-additive KPIs.

`period_over_period_change` remains a validation item rather than a
locked reporting-layer KPI until the implementation scope is explicitly
confirmed.
