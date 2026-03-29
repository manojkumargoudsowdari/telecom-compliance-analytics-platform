# Gold Aggregation and Transformation Rules

## 1. Purpose

This document defines the aggregation and transformation rules for the
Gold layer of the Telecom Compliance Analytics Platform (TCAP).

It is based only on the approved Gold architecture, KPI catalog, Gold
data model, and Phase 4 Silver schema contract. It defines aggregation
behavior only. It does not define code, SQL, pipelines, or runtime
orchestration.

## 2. Selected Aggregation Approach

### Approved Approach

The approved Gold aggregation flow is:

- Silver to daily Gold
- daily Gold to monthly Gold

### Rationale

This approach is selected because:

- `fact_complaints_daily` is the canonical base Gold fact
- daily output provides the most granular approved reporting base for
  complaint counts
- monthly output can be derived deterministically from the daily fact
  without changing approved dimensions
- daily-to-monthly aggregation strengthens reconciliation and makes
  monthly rollups auditable

Direct monthly aggregation from Silver is not the approved approach for
the first Gold implementation boundary.

Monthly Gold fact construction must be derived exclusively from
`fact_complaints_daily` to enforce reconciliation and auditability.
Direct Silver-to-monthly aggregation is explicitly prohibited.

## 3. Source-to-Gold Aggregation Flow

1. read the validated Silver dataset `silver_fcc_consumer_complaints`
2. map each Silver record to conformed Gold dimension members
3. build `fact_complaints_daily` from the Silver complaint population
4. aggregate `fact_complaints_daily` into `fact_complaints_monthly`
5. compute monthly non-additive KPIs from monthly complaint totals
6. reconcile daily Gold to Silver and monthly Gold to daily Gold

This sequence establishes one canonical Gold counting path.

## 4. Daily Fact Rules

### Target Dataset

- `fact_complaints_daily`

### Source Fields Used

- `complaint_id`
- `date_created`
- `issue_type`
- `issue`
- `method`
- `state`
- `city`
- `zip_code`

### Grouping Keys

- `date_key`
- `issue_key`
- `method_key`
- `geography_key`

### `complaint_count` Logic

- count validated Silver complaints grouped by:
  - `date_key`
  - `issue_key`
  - `method_key`
  - `geography_key`
- each Gold count represents the number of Silver complaint records in
  that exact daily dimensional slice

### `period_over_period_change` Input Rules

`period_over_period_change` is not summed from stored lower-level
derived values.

It must be recomputed from daily complaint totals by:

- identifying the current daily reporting period
- identifying the immediately previous comparable daily reporting period
- calculating:
  - `current_period_count - previous_period_count`

If no previous comparable period exists, return null.

If either period count is unavailable in the comparison context, return
null.

### Unknown-Member Mapping Behavior

- null `issue` or `issue_type` values map to a deterministic
  unknown-member `issue_key`
- null `method` values map to a deterministic unknown-member
  `method_key`
- null geography values map to a deterministic unknown-member
  `geography_key`
- unknown-member rows remain included in Gold fact totals and must be
  included in reconciliation unless an explicit report filter excludes
  them

## 5. Monthly Fact Rules

### Target Dataset

- `fact_complaints_monthly`

### Source Used

The approved source for monthly Gold is:

- `fact_complaints_daily`

Monthly Gold is not built directly from Silver in the approved first
implementation path.

Monthly fact construction must use `fact_complaints_daily` as its only
approved upstream source. Direct Silver-to-monthly aggregation is not
permitted.

### Source Fields Used

From daily Gold:

- `date_key` mapped to `month_key`
- `issue_key`
- `method_key`
- `geography_key`
- daily `complaint_count`

### Grouping Keys

- `month_key`
- `issue_key`
- `method_key`
- `geography_key`

### `complaint_count` Logic

- sum daily complaint counts into monthly complaint totals grouped by:
  - `month_key`
  - `issue_key`
  - `method_key`
  - `geography_key`

### `complaint_growth_rate` Logic

- compute from monthly complaint totals only
- compare current month complaint count to the immediately previous
  comparable month
- calculate:
  - `(current_month_complaints - previous_month_complaints) / previous_month_complaints`
- if `previous_month_complaints = 0`, return null

### `category_share` Logic

`category_share` is computed only in the monthly fact and only within a
single declared active category axis.

Approved category axes:

- `issue`
- `method`
- `geography`

For a given query or output context:

- exactly one category axis is the active category axis
- the denominator is the sum of `complaint_count` over the same filtered
  context excluding only the active category dimension
- time filters remain preserved
- all non-category dimensions remain preserved

This rule prevents ambiguous denominator behavior.

### `rolling_average_complaint_count` Logic

- compute only from monthly complaint totals
- use a parameterized but fixed rolling window per dataset
- the selected rolling window definition must be declared in metadata
- the rolling window cannot vary dynamically within the same persisted
  dataset

## 6. `category_share` Rules

### Numerator

- complaint count for the selected category value within the active
  monthly filtered context

### Denominator

- sum of `complaint_count` over the same filtered context excluding
  only the active category dimension while preserving all other filters

### Active Category Axis Behavior

For any single output or query context:

- one and only one category axis is active
- examples:
  - if the report is showing issue share, `issue` is the active axis
  - if the report is showing method share, `method` is the active axis
  - if the report is showing geography share, `geography` is the active
    axis

The denominator must always be aligned to the same monthly filtered
context and the same active-axis choice.

### Filtered-Context Behavior

- preserve:
  - time filters
  - all non-axis dimension filters
  - all explicit report filters
- remove:
  - only the active category axis from the denominator

This means:

- issue share preserves method and geography filters
- method share preserves issue and geography filters
- geography share preserves issue and method filters

Concrete example:

- if:
  - `month = Jan 2024`
  - `state = FL`
  - active category axis = `issue`
- then:
  - numerator = complaints for `(Jan 2024, FL, specific issue)`
  - denominator = complaints for `(Jan 2024, FL, all issues)`

### Zero-Denominator Handling

- if the denominator total is `0`, return null
- forced zero-share values are not allowed for invalid comparison
  contexts

## 7. Non-Additive KPI Rules

The following KPIs are non-additive:

- `complaint_growth_rate`
- `category_share`
- `period_over_period_change`
- `rolling_average_complaint_count`

### Recompution Rules

- non-additive KPIs must be recomputed from the appropriate fact-level
  complaint totals
- they must not be summed across rows, periods, or categories
- they must not be rolled up from previously derived KPI values

### No Summation Rule

The following are explicitly prohibited:

- summing daily `period_over_period_change` values to create a monthly
  result
- summing share values across categories to derive a parent-level share
- summing growth-rate values across periods
- summing rolling-average values across periods

## 8. Reconciliation Rules

### Gold to Silver Count Reconciliation

- daily Gold complaint totals must reconcile to Silver complaint totals
  for the same:
  - `date_created`
  - issue context
  - method context
  - geography context
- unknown-member rows must remain included in reconciliation totals
  unless explicitly excluded by the same reporting filter context

### Daily to Monthly Reconciliation

- monthly complaint totals must equal the sum of the corresponding daily
  complaint totals for the same:
  - month
  - issue context
  - method context
  - geography context

### Unknown-Member Reconciliation

- unknown-member issue, method, and geography rows are valid Gold rows
- they must reconcile back to the Silver records that produced them
- unknown-member rows must not be silently dropped during daily or
  monthly aggregation

## 9. Design Trade-Offs

- daily-to-monthly aggregation is slightly more structured than direct
  monthly aggregation from Silver, but it improves auditability and
  reconciliation
- the unified monthly fact simplifies the Gold model, but it requires
  strict control of the active category axis for `category_share`
- unknown-member handling improves completeness and reconciliation, but
  it requires consistent downstream filtering discipline

## 10. Acceptance Criteria

This task is complete only when:

- the selected aggregation approach is explicit
- the daily fact build rules are defined
- the monthly fact build rules are defined
- `category_share` numerator, denominator, active axis behavior, and
  filtered-context behavior are explicit
- non-additive KPI recomputation rules are explicit
- Gold-to-Silver reconciliation rules are explicit
- daily-to-monthly reconciliation rules are explicit
- unknown-member behavior is explicit
- no code, SQL, or pipeline implementation details are introduced
