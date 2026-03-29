# Dashboard Alignment Matrix

## 1. Purpose

This document maps the approved Gold datasets, KPIs, and dimensions to
the reporting and dashboard requirements defined in Phase 2.

Its purpose is to confirm that the approved Gold model is sufficient to
support the intended reporting experience without hidden coverage gaps,
redundant outputs, or unsupported dependencies.

This document is limited to dashboard-alignment design. It does not
define Power BI implementation, DAX, SQL, semantic-model optimization,
or visual styling.

## 2. Approved Gold Outputs in Scope

Approved fact datasets:

- `fact_complaints_daily`
- `fact_complaints_monthly`

Approved conformed dimensions:

- `dim_date`
- `dim_issue`
- `dim_method`
- `dim_geography`

Approved KPIs:

- `complaint_count`
- `complaint_growth_rate`
- `category_share`
- `period_over_period_change`
- `rolling_average_complaint_count`

## 3. Dashboard Page Inventory

The approved Phase 2 dashboard inventory is:

- Page 1: Compliance Overview
- Page 2: Issue Type and Method Analysis
- Page 3: Issue Category Analysis
- Page 4: Geographic Analysis
- Page 5: Trend and Anomaly Monitoring

## 4. Page-by-Page Alignment Matrix

| Dashboard Page | Required Visuals / Analysis Goals | Supporting Gold Fact(s) | Supporting KPI(s) | Supporting Dimensions / Filters | Required Grain | Constraints / Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `Page 1: Compliance Overview` | KPI summary, monthly trend, top issue concentration, leadership filter panel | `fact_complaints_monthly`; `fact_complaints_daily` for optional lower-period drill path only | `complaint_count`, `complaint_growth_rate`, `category_share` with active category axis = `issue` | time via `dim_date`; issue via `dim_issue`; method via `dim_method`; geography via `dim_geography`; filters: `date_created`, `issue_type`, `method`, `state` | monthly primary | executive page should use monthly grain as the default reporting view; `category_share` is derived from monthly fact counts in reporting/query consumption, not from a persisted share column |
| `Page 2: Issue Type and Method Analysis` | ranked `issue_type` and `method` analysis, issue-type/method comparison matrix, category mix view | `fact_complaints_monthly` | `complaint_count`, `category_share` with active category axis = `issue` or `method` depending on the visual | time via `dim_date`; issue via `dim_issue`; method via `dim_method`; geography via `dim_geography`; filters: `date_created`, `issue`, `state`, `city` | monthly | issue and method comparison is supported through dimensional slicing of the same monthly fact; `category_share` is derived from monthly fact counts rather than a separate persisted share field |
| `Page 3: Issue Category Analysis` | ranked issue view, issue concentration, monthly issue trend, persistence versus spike interpretation | `fact_complaints_monthly`; `fact_complaints_daily` for finer trend inspection when needed | `complaint_count`, `category_share` with active category axis = `issue`, `rolling_average_complaint_count`, `period_over_period_change` | time via `dim_date`; issue via `dim_issue`; method via `dim_method`; geography via `dim_geography`; filters: `date_created`, `issue_type`, `method`, `state` | monthly primary; daily secondary | rolling average is monthly-only; period-over-period change may be surfaced at daily or monthly context depending on the reporting view; `category_share` remains a Gold-defined KPI derived from monthly fact counts |
| `Page 4: Geographic Analysis` | state concentration, ranked geography views, optional over-time comparison by selected geography | `fact_complaints_monthly`; `fact_complaints_daily` for optional lower-period geography trend views | `complaint_count`, `category_share` with active category axis = `geography` when share-style geography comparison is needed | time via `dim_date`; geography via `dim_geography`; issue via `dim_issue`; method via `dim_method`; filters: `date_created`, `issue_type`, `method`, `issue`, `zip_code` | monthly primary | `state` is the primary geography level; `city` remains supported but should be interpreted cautiously because Phase 2 already notes standardization risk; `category_share` is derived from monthly fact counts rather than a persisted geography-share field |
| `Page 5: Trend and Anomaly Monitoring` | trend chart, rolling average overlay, variance table, issue or geography comparison matrix, exception-focused review | `fact_complaints_daily`; `fact_complaints_monthly` | `complaint_count`, `period_over_period_change`, `rolling_average_complaint_count`, `complaint_growth_rate` | time via `dim_date`; issue via `dim_issue`; method via `dim_method`; geography via `dim_geography`; filters: `date_created`, `issue`, `issue_type`, `method`, `state`, `city`, `zip_code` | daily and monthly | `period_over_period_change` is daily-fact based; `rolling_average_complaint_count` and `complaint_growth_rate` are monthly-fact based, so this page intentionally combines both approved fact grains |

## 5. Dashboard Coverage Summary

### 5.1 Time Trend Coverage

Supported by:

- `fact_complaints_daily`
- `fact_complaints_monthly`

Coverage status:

- daily trend inspection is supported
- monthly executive and KPI trend reporting is supported
- weekly reporting is not supported in the approved Phase 5 scope

### 5.2 Issue Analysis Coverage

Supported by:

- `fact_complaints_monthly`
- `dim_issue`

Coverage status:

- issue concentration is supported through `category_share` with active
  category axis = `issue`
- issue trend reporting is supported at monthly grain, with daily
  follow-up trend inspection available where needed

### 5.3 Method Analysis Coverage

Supported by:

- `fact_complaints_monthly`
- `dim_method`

Coverage status:

- method mix analysis is supported through dimensional slicing and
  `category_share` with active category axis = `method`
- no separate method fact is required for the approved reporting scope

### 5.4 Geography Analysis Coverage

Supported by:

- `fact_complaints_monthly`
- `fact_complaints_daily`
- `dim_geography`

Coverage status:

- state and city analysis are supported
- state is the primary geography level
- ZIP-based filtering is supported through the geography dimension and
  reporting context

### 5.5 Executive / High-Level Summary Coverage

Supported by:

- `fact_complaints_monthly`
- `complaint_count`
- `complaint_growth_rate`
- `category_share` with active category axis = `issue`

Coverage status:

- the approved Gold model supports the executive narrative scope
  documented in `AR-07`

## 6. KPI-to-Visual Mapping Summary

| KPI | Primary Reporting Home | Typical Visual Support |
| --- | --- | --- |
| `complaint_count` | all pages | KPI cards, line charts, ranked bars, maps, tables, matrices |
| `complaint_growth_rate` | Page 1, Page 5 | KPI cards, executive summary visuals, monthly trend comparison visuals |
| `category_share` | Page 1, Page 2, Page 3, Page 4 | issue concentration charts, method mix views, share tables, geography share comparisons derived from monthly fact counts within the approved active-axis context |
| `period_over_period_change` | Page 3, Page 5 | variance tables, anomaly review charts, comparison visuals |
| `rolling_average_complaint_count` | Page 3, Page 5 | smoothed trend lines, persistence versus spike views |

Every approved KPI has a clear reporting home in the approved page set.

## 7. Dimension and Filter Support Mapping

| Analysis Need | Gold Support |
| --- | --- |
| time filtering | `dim_date`, daily and monthly facts |
| issue slicing | `dim_issue`, monthly fact primarily |
| method slicing | `dim_method`, monthly fact primarily |
| geography slicing | `dim_geography`, monthly fact primarily with daily support for trend drill paths |
| executive monthly summaries | monthly fact |
| anomaly-oriented trend inspection | daily fact plus monthly derived KPI context |

Filter behavior assumptions consistent with the approved Gold design:

- time filters use the canonical reporting date derived from
  `date_created`
- issue, method, and geography filters operate through conformed
  dimensions
- `category_share` depends on the approved active category axis and
  filtered-context denominator rule and is derived from monthly fact
  counts during reporting/query consumption rather than from a persisted
  share column

## 8. Gaps, Overlaps, and Presentation-Only Output Review

### 8.1 Identified Gaps

No blocking reporting gap is identified within the approved Phase 2 and
Phase 5 scope.

Known constraint:

- weekly reporting is not supported because Phase 5 explicitly locks the
  initial Gold time grains to daily and monthly only

### 8.2 Identified Overlaps

The same monthly fact supports issue, method, and geography analysis.

This is an intentional design choice, not a redundancy defect, because:

- dimensional filtering is the approved mechanism for category-specific
  reporting
- separate category-specific facts were explicitly removed from the
  approved Gold model

### 8.3 Presentation-Only Derived Output Decision

No additional presentation-only derived dataset is required for the
approved Phase 5 reporting scope.

Reason:

- the two-fact Gold model already provides the approved KPI homes,
  dimensions, and time grains needed by the dashboard design
- any later presentation-only helper output would be a convenience
  choice, not a current coverage requirement

## 9. Final Conclusion

The approved two-fact Gold model is sufficient for the current Phase 5
reporting scope.

Specifically:

- `fact_complaints_daily` is sufficient for detailed trend inspection
  and daily period-over-period monitoring
- `fact_complaints_monthly` is sufficient for executive reporting,
  category-share analysis, complaint growth reporting, and rolling
  monthly trend views
- `dim_date`, `dim_issue`, `dim_method`, and `dim_geography` provide
  the required slicing and filtering coverage for all approved Phase 2
  dashboard pages

No additional Gold fact is required to satisfy the approved dashboard
coverage at this stage.

## 10. Acceptance Criteria

This task is complete only when:

- every approved dashboard page is mapped to approved Gold outputs
- every approved KPI has a clear reporting home
- required time, issue, method, and geography slicing is accounted for
- any gaps, overlaps, or constraints are explicitly documented
- the need for presentation-only derived outputs is explicitly assessed
- the conclusion on reporting readiness is explicit
- no implementation detail, DAX, SQL, or Power BI build instruction is
  introduced
