# Phase 6 KPI Validation and Reconciliation

## 1. Purpose

This document records the Phase 6 reporting-layer validation and
reconciliation results for the approved Gold KPI set.

The objective is to confirm that reporting-layer KPI behavior is
statistically correct, reconciles to persisted Gold facts, and remains
aligned to the approved Gold contracts from Phase 5.

All validations in this document use recomputed expected values and
compare them to persisted Gold values. The validation does not rely only
on stored KPI fields or summary outputs.

## 2. Scope

Confirmed KPIs validated:

- `complaint_count`
- `complaint_growth_rate`
- `rolling_average_complaint_count`
- `category_share`

Validated Gold sources:

- `data/gold/fact_complaints_daily/`
- `data/gold/fact_complaints_monthly/`
- `data/gold/_quality/20260328T214636092984Z/validation_summary.json`
- `data/gold/_metadata/20260328T214636092984Z.json`

Approved evidence run:

- `source_run_id = 20260328T214636092984Z`

Out of scope for this document:

- `period_over_period_change`
  - remains a validation item pending explicit KPI-contract confirmation

## 3. Validation Approach

The reporting-layer validation followed these rules:

- recompute expected values from persisted Gold fact rows
- compare recomputed expected values to persisted Gold KPI values where
  the KPI is physically stored
- compute reporting-layer-only KPIs from Gold fact counts and validate
  denominator behavior directly
- verify both global totals and filtered-context behavior
- document pass or fail explicitly for every scenario

## 4. Complaint Count Validation

### Validation Scenario

- recompute total complaint counts from `fact_complaints_daily`
- recompute total complaint counts from `fact_complaints_monthly`
- compare daily and monthly totals globally
- compare daily and monthly totals by `month_key`

### Expected Result

- daily and monthly totals reconcile exactly
- month-level complaint totals reconcile exactly
- no zero-count persisted fact rows exist under the current Gold
  contract

### Actual Result

- daily total complaints: `2,603,475`
- monthly total complaints: `2,603,475`
- daily fact rows: `2,351,099`
- monthly fact rows: `1,998,296`
- zero daily rows: `0`
- zero monthly rows: `0`
- month mismatch count: `0`

### Status

- `PASS`

## 5. Complaint Growth Rate Validation

### Validation Scenario

- recompute expected growth rate from persisted monthly
  `complaint_count`
- compare recomputed values row-by-row against persisted
  `fact_complaints_monthly.complaint_growth_rate`
- inspect edge cases where the previous month is missing or zero

### Expected Result

- persisted Gold growth-rate values match the recomputed values
- rows with no previous comparable month return `null`
- rows with previous-month complaint count equal to zero return `null`

### Actual Result

- rows checked: `1,998,296`
- rows failed: `0`
- null due to missing previous month: `1,714,476`
- null due to zero previous month: `0`
- sample failures: none

### Status

- `PASS`

## 6. Rolling Average Validation

### Validation Scenario

- recompute expected `rolling_average_complaint_count` from persisted
  monthly `complaint_count`
- use the declared fixed calendar-month window
- compare recomputed values row-by-row against persisted monthly Gold
  values

### Expected Result

- persisted rolling-average values match recomputed values exactly
- missing months inside the fixed calendar window are treated as
  zero-complaint months
- early periods use zero-filled pre-history months inside the declared
  window

### Actual Result

- rows checked: `1,998,296`
- rows failed: `0`
- rolling window months: `3`
- sample failures: none
- zero-fill example:
  - `month_key = 2014-10`
  - partition:
    - `issue_type=Accessibility|issue=Hearing Aid Compatibility of Wireless Phones`
    - `__UNKNOWN_METHOD__`
    - `state=AZ|city=Phoenix|zip_code=85032`
  - `complaint_count = 1`
  - `rolling_average_complaint_count = 0.3333333333333333`

### Status

- `PASS`

## 7. Category Share Validation

### Validation Scenario

- compute `category_share` from persisted monthly `complaint_count`
- validate share behavior for:
  - issue axis
  - method axis
  - geography axis
- validate denominator behavior under filtered contexts

### Expected Result

- category shares sum to `100%` for each month within the active
  category axis
- denominator removes only the active category axis
- time and non-category filters remain preserved

### Actual Result

Global axis validation:

- issue axis across all months: `PASS`
- method axis across all months: `PASS`
- geography axis across all months: `PASS`

Filtered-context validation:

- issue axis with state filter: `PASS`
- method axis with issue filter: `PASS`
- issue axis with method filter: `PASS`
- issue axis with combined state and method filters: `PASS`

Months checked:

- global: `138`
- with state filter: `138`
- with issue filter: `114`
- with method filter: `138`
- with combined filters: `138`

Concrete denominator example:

- `month_key = 2014-10`
- `state_filter = CA`
- `method_filter = method=Wireless (cell phone/other mobile device)`
- active axis: `issue`
- numerator complaint count: `2`
- denominator complaint count: `12`
- share: `0.16666666666666666`

### Status

- `PASS`

## 8. Filter Behavior Validation

### Validation Scenario

- validate KPI behavior under:
  - state filters
  - issue filters
  - method filters
  - combined filters

### Expected Result

- filtered totals remain internally consistent
- `category_share` denominator preserves all non-category filters
- persisted monthly KPIs remain consistent with the filtered monthly
  complaint counts

### Actual Result

- state-filtered `category_share`: `PASS`
- issue-filtered `category_share`: `PASS`
- method-filtered `category_share`: `PASS`
- combined-filter `category_share`: `PASS`
- monthly complaint-count-based KPI recomputation remained consistent
  under filtered contexts

### Status

- `PASS`

## 9. Edge Case Validation

### Validation Scenario

- inspect missing months in monthly partitions
- inspect sparse categories
- inspect zero-value behavior

### Expected Result

- missing months do not break calendar-month rolling averages
- sparse categories remain valid inputs where denominator rules hold
- zero-count persisted fact rows do not appear in the current Gold
  contract

### Actual Result

- growth null due to missing previous month: `1,714,476`
- growth null due to zero previous month: `0`
- partitions with gap detected: `944,684`
- zero daily rows: `0`
- zero monthly rows: `0`

Sample partition gaps:

- `issue_type=Internet|issue=Availability` / `method=Cable` /
  `state=CO|city=Evergreen|zip_code=80439`:
  latest seen month `2014-10`, current month `2014-12`
- `issue_type=Internet|issue=Availability` / `method=Cable` /
  `state=IA|city=Ankeny|zip_code=50021`:
  latest seen month `2014-10`, current month `2014-12`
- `issue_type=Internet|issue=Speed` / `method=Cable` /
  `state=OH|city=Dayton|zip_code=45424`:
  latest seen month `2014-10`, current month `2014-12`

Sample sparse categories:

- `2014-10` / `issue_type=Accessibility|issue=Telecommunications Relay Service (TRS)` / count `1`
- `2014-10` / `issue_type=Internet|issue=Equipment` / count `1`
- `2014-10` / `issue_type=Radio|issue=Equipment` / count `1`
- `2014-11` / `issue_type=Accessibility|issue=Video Description` / count `1`
- `2014-12` / `issue_type=Accessibility|issue=Hearing Aid Compatibility of Wireless Phones` / count `1`

### Status

- `PASS`

## 10. Discrepancies

No KPI discrepancies were identified in the validated scope.

The reporting-layer KPI validations passed for:

- recomputed `complaint_count`
- recomputed `complaint_growth_rate`
- recomputed `rolling_average_complaint_count`
- recomputed `category_share`

## 11. Outcome

All confirmed Phase 6 KPIs passed validation against the persisted Gold
facts for `source_run_id = 20260328T214636092984Z`.

The Gold facts support:

- trend analysis
- anomaly-oriented smoothing through the approved rolling average
- reporting-layer share calculations
- leadership-safe monthly reporting using reconciled complaint totals

No inconsistencies were found in the validated KPI scope.
