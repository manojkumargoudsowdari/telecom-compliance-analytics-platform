# Phase 6 Dashboard Mapping

## 1. Purpose

This document maps the approved Phase 2 dashboard requirements to the
Phase 6 Power BI reporting design.

The goal is to translate the approved reporting scope into a grain-safe,
KPI-safe dashboard structure that can be implemented on top of the
completed Gold layer and the approved Phase 6 semantic-model rules.

This document does not define DAX, Power BI files, or visual styling. It
defines reporting intent, valid KPI usage, valid fact-grain usage, and
dashboard guardrails.

## 2. Confirmed Reporting Inputs

Confirmed Gold-backed reporting inputs:

- `fact_complaints_daily`
  - `complaint_count`
- `fact_complaints_monthly`
  - `complaint_count`
  - `complaint_growth_rate`
  - `rolling_average_complaint_count`

Confirmed reporting-layer KPI:

- `category_share`
  - derived from monthly `complaint_count`
  - not persisted physically in Gold

Confirmed Phase 6 KPI set for dashboard mapping:

- `complaint_count`
- `complaint_growth_rate`
- `rolling_average_complaint_count`
- `category_share`

Validation item not locked for dashboard implementation:

- `period_over_period_change`
  - referenced in the Phase 2 dashboard draft
  - not part of the currently confirmed KPI set for Phase 6
  - must not be treated as an approved KPI until explicitly confirmed

## 3. Global Dashboard Rules

The following rules apply to every page:

- a single visual must use only one fact grain
- daily and monthly facts must not be mixed in the same visual
- non-additive KPIs must not be summed or averaged as if they were
  additive
- `category_share` is valid only when exactly one supported category
  axis is active
- leadership-facing visuals must prioritize monthly clarity and
  state-level geography

Supported filter families:

- time
- issue
- method
- geography

## 4. Page 1: Compliance Overview

### Business Purpose

Answer the leadership question: what is the current complaint volume,
what is the monthly direction of change, and which issue categories
deserve attention next.

### KPIs Used

- `complaint_count`
- `complaint_growth_rate`
- `category_share`

### Visual Definitions

- KPI card
  - value:
    - monthly `complaint_count`
  - grouping:
    - none
- KPI card
  - value:
    - monthly `complaint_growth_rate`
  - grouping:
    - none
- line chart
  - x-axis:
    - `month_key`
  - y-axis:
    - monthly `complaint_count`
  - grouping:
    - none
- ranked bar chart or top table
  - axis:
    - `issue`
  - value:
    - monthly `complaint_count`
    - optional `category_share`
  - grouping:
    - issue only

### Grain

- monthly

### Data Source

- `fact_complaints_monthly`

### Filters

- time:
  - monthly date filters
- issue:
  - `issue_type`
  - `issue`
- method:
  - `method`
- geography:
  - `state`

### Interaction Design

- slicers:
  - month range
  - `issue_type`
  - `method`
  - `state`
- drilldowns:
  - issue selection to Page 3
  - state selection to Page 4

### Executive vs Exploratory Usage

- executive:
  - headline volume
  - monthly direction
  - top issue concentration
- exploratory:
  - filtered monthly issue ranking within the current executive context

### Constraints

- `category_share` is valid only when the issue axis is the single
  active category axis
- no daily visuals belong on this page

## 5. Page 2: Issue Type and Method Analysis

### Business Purpose

Compare complaint mix across issue type and method to understand which
service areas and delivery methods drive complaint volume.

### KPIs Used

- `complaint_count`
- `category_share`

### Visual Definitions

- ranked bar chart
  - axis:
    - `issue_type`
  - value:
    - monthly `complaint_count`
- ranked bar chart
  - axis:
    - `method`
  - value:
    - monthly `complaint_count`
- matrix
  - rows:
    - `issue_type`
  - columns:
    - `method`
  - value:
    - monthly `complaint_count`
- share chart
  - axis:
    - `issue_type` or `method`
  - value:
    - `category_share`
  - grouping:
    - exactly one active category axis per visual

### Grain

- monthly

### Data Source

- `fact_complaints_monthly`

### Filters

- time:
  - monthly date filters
- issue:
  - `issue`
  - `issue_type`
- method:
  - `method`
- geography:
  - `state`
  - `city`

### Interaction Design

- slicers:
  - month range
  - `issue`
  - `state`
  - `city`
- drilldowns:
  - issue-type or method selection to Page 5 where supported by
    confirmed KPI scope

### Executive vs Exploratory Usage

- executive:
  - top issue-type and method concentration summaries
- exploratory:
  - issue-type by method matrices
  - share breakdowns under filtered contexts

### Constraints

- do not show issue-type share and method share together in the same
  category-share visual
- `category_share` must preserve all non-category filters and remove
  only the active category axis

## 6. Page 3: Issue Category Analysis

### Business Purpose

Identify dominant issue categories and distinguish persistent issue
themes from short-lived movement using monthly trends and smoothed
monthly trend behavior.

### KPIs Used

- `complaint_count`
- `category_share`
- `rolling_average_complaint_count`

### Visual Definitions

- ranked issue bar chart
  - axis:
    - `issue`
  - value:
    - monthly `complaint_count`
- issue share chart
  - axis:
    - `issue`
  - value:
    - `category_share`
- monthly trend line
  - x-axis:
    - `month_key`
  - y-axis:
    - monthly `complaint_count`
  - grouping:
    - selected `issue`
- smoothed trend line
  - x-axis:
    - `month_key`
  - y-axis:
    - `rolling_average_complaint_count`
  - grouping:
    - selected `issue`
- small multiples or multi-series monthly trend
  - x-axis:
    - `month_key`
  - y-axis:
    - monthly `complaint_count`
  - grouping:
    - top issues

### Grain

- monthly

### Data Source

- `fact_complaints_monthly`

### Filters

- time:
  - monthly date filters
- issue:
  - `issue_type`
  - `issue`
- method:
  - `method`
- geography:
  - `state`

### Interaction Design

- slicers:
  - month range
  - `issue_type`
  - `method`
  - `state`
- drilldowns:
  - selected issue to Page 5 for monthly anomaly-oriented review within
    the confirmed KPI set

### Executive vs Exploratory Usage

- executive:
  - dominant issue concentration and smoothed issue trend
- exploratory:
  - top-issue comparisons and filtered issue share analysis

### Constraints

- `rolling_average_complaint_count` must be shown only in monthly
  visuals
- Phase 2 reference to `period_over_period_change` remains a validation
  item and is not part of the locked Phase 6 page design

## 7. Page 4: Geographic Analysis

### Business Purpose

Show where complaint activity is concentrated and whether those patterns
remain stable over time.

### KPIs Used

- `complaint_count`
- `category_share`

### Visual Definitions

- filled map or state heatmap
  - location:
    - `state`
  - value:
    - monthly `complaint_count`
- ranked state table
  - rows:
    - `state`
  - value:
    - monthly `complaint_count`
- ranked city table
  - rows:
    - `city`
  - value:
    - monthly `complaint_count`
- optional monthly geography trend
  - x-axis:
    - `month_key`
  - y-axis:
    - monthly `complaint_count`
  - grouping:
    - selected geography
- optional geography share comparison
  - axis:
    - `state`
  - value:
    - `category_share`
  - grouping:
    - geography as the single active category axis

### Grain

- monthly

### Data Source

- `fact_complaints_monthly`

### Filters

- time:
  - monthly date filters
- issue:
  - `issue`
  - `issue_type`
- method:
  - `method`
- geography:
  - `state`
  - `city`
  - `zip_code`

### Interaction Design

- slicers:
  - month range
  - `issue`
  - `issue_type`
  - `method`
  - `state`
- drilldowns:
  - state to city
  - state selection to Page 5 within the confirmed KPI set

### Executive vs Exploratory Usage

- executive:
  - state-level geography summaries
  - state trend monitoring
- exploratory:
  - city-level inspection where data completeness supports it

### Constraints

- leadership views should default to state-level geography
- `city` and `zip_code` are secondary exploratory filters only
- geography share visuals are valid only when geography is the single
  active category axis

## 8. Page 5: Trend and Anomaly Monitoring

### Business Purpose

Support descriptive monitoring of shifts in complaint activity using
daily volume detail and monthly smoothed context without misusing
non-additive KPIs.

### KPIs Used

- `complaint_count`
- `complaint_growth_rate`
- `rolling_average_complaint_count`

### Visual Definitions

- daily line chart
  - x-axis:
    - `date_key`
  - y-axis:
    - daily `complaint_count`
  - grouping:
    - selected issue, method, or geography slice
- monthly line chart with rolling average overlay
  - x-axis:
    - `month_key`
  - y-axis:
    - monthly `complaint_count`
    - `rolling_average_complaint_count`
  - grouping:
    - selected issue, method, or geography slice
- monthly variance summary visual
  - axis:
    - `month_key`
  - value:
    - `complaint_growth_rate`
- comparison matrix
  - rows:
    - selected issue, issue type, method, or state
  - values:
    - monthly `complaint_count`
    - optional `complaint_growth_rate` where monthly grain is preserved

### Grain

- page allows both daily and monthly visuals
- each visual must remain grain-pure

### Data Source

- daily visuals:
  - `fact_complaints_daily`
- monthly visuals:
  - `fact_complaints_monthly`

### Filters

- time:
  - daily date filters for daily visuals
  - monthly date filters for monthly visuals
- issue:
  - `issue`
  - `issue_type`
- method:
  - `method`
- geography:
  - `state`
  - `city`
  - `zip_code`

### Interaction Design

- slicers:
  - time
  - `issue`
  - `issue_type`
  - `method`
  - `state`
  - `city`
  - `zip_code`
- drilldowns:
  - selected issue trend
  - selected state trend
  - selected issue-type or method trend

### Executive vs Exploratory Usage

- executive:
  - monthly trend direction
  - rolling-average context
  - focused exception review
- exploratory:
  - daily complaint-count inspection
  - filtered monthly trend comparisons

### Constraints

- no single visual may combine daily and monthly facts
- `complaint_growth_rate` and `rolling_average_complaint_count` must
  remain in monthly visuals only
- Phase 2 reference to `period_over_period_change` remains a validation
  item and is not part of the locked Phase 6 page design

## 9. Dashboard Design Guardrails

The following rules must be enforced in the reporting implementation:

- use only the confirmed KPI set:
  - `complaint_count`
  - `complaint_growth_rate`
  - `rolling_average_complaint_count`
  - `category_share`
- do not expose `period_over_period_change` unless its KPI contract is
  confirmed later
- do not mix daily and monthly facts in a single visual
- do not sum or average non-additive KPIs as if they were additive
- treat persisted Gold KPI values as the source of truth where the KPI
  is physically stored
- compute `category_share` only from monthly `complaint_count`
- allow `category_share` only where exactly one supported category axis
  is active
- default leadership geography to `state`
- keep `city` and `zip_code` as secondary exploratory geography levels
- keep leadership pages monthly-first for clarity and correctness

## 10. Ambiguities and Validation Items

The following items remain open from the Phase 2 dashboard draft:

- `period_over_period_change`
  - referenced in Page 3 and Page 5
  - not part of the currently locked Phase 6 KPI set
- Phase 2 drilldown note about month to lower period grain
  - daily drilldown is valid only on daily visuals
  - monthly KPI visuals must remain monthly

No other blocking ambiguity was identified for the confirmed KPI set and
approved Gold-backed reporting scope.
