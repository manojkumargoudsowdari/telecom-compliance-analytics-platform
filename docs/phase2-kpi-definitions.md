# Phase 2 KPI Definitions

## Document Control

- Jira Ticket ID: `TCAP-3`
- Git Commit Link: `<add commit URL after commit>`
- Version: `0.2-draft`
- Date: `2026-03-05`

## Purpose

Define the Phase 2 KPI catalog required to support the approved FCC-based analytics requirements and later dashboard design.

## KPI Catalog

- This KPI set is limited to measures supportable by the currently documented FCC fields.
- All formulas are written to be compatible with Power BI measure design.
- The base record-level metric uses the FCC ticket identifier `id`.

## KPI Definitions Table

| KPI Name | Description | Formula | Grain | Numerator | Denominator | Dimensions Supported | Filters Supported | Requirement Source | Notes / Edge Cases |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `complaint_count` | Total count of complaint tickets in the current filter context | `COUNT(id)` | complaint count at selected report grain | `COUNT(id)` | `N/A` | `date_created`, `ticket_created`, `issue_type`, `method`, `issue`, `city`, `state`, `zip` | `date_created`, `issue_type`, `method`, `issue`, `city`, `state`, `zip` | `AR-01`, `AR-02`, `AR-03`, `AR-04`, `AR-05`, `AR-06`, `AR-07` | Depends on `id` behaving as a unique complaint ticket; uniqueness must be validated during profiling |
| `complaint_growth_rate` | Relative change in complaint count between current period and previous comparable period | `(current_period_complaints - previous_period_complaints) / previous_period_complaints` | period level, typically month | `current_period_complaints - previous_period_complaints` | `previous_period_complaints` | `date_created`, `issue_type`, `method`, `issue`, `state`, `city` | `issue_type`, `method`, `issue`, `state`, `city`, `zip` | `AR-01`, `AR-07` | Undefined when previous period complaints = 0; should return blank or handled-safe value in Power BI |
| `complaint_share` | Share of complaint count for the selected category relative to total complaints in the same filter context | `complaint_count / total_complaint_count_in_filter_context` | category share within selected context | `complaint_count` | `total_complaint_count_in_filter_context` | `issue_type`, `method`, `state`, `city`, `zip` | `date_created`, `issue`, `issue_type`, `method`, `state`, `city`, `zip` | `AR-02` | Denominator must remove only the category axis being compared while preserving report filters |
| `issue_share` | Share of complaint count for a specific issue relative to all complaints in the same filter context | `issue_complaint_count / total_complaint_count_in_filter_context` | issue category share within selected context | `issue_complaint_count` | `total_complaint_count_in_filter_context` | `issue`, `date_created`, `issue_type`, `method`, `state`, `city` | `date_created`, `issue_type`, `method`, `state`, `city`, `zip` | `AR-03`, `AR-07` | Should sum to 100% across visible issues only when the same filter context is applied consistently |
| `period_over_period_change` | Absolute change in complaint count from one reporting period to the previous period | `current_period_complaints - previous_period_complaints` | period level, typically week or month | `current_period_complaints` | `previous_period_complaints` | `date_created`, `issue`, `issue_type`, `method`, `state`, `city` | `issue`, `issue_type`, `method`, `state`, `city`, `zip` | `AR-05`, `AR-06` | More stable than percentage growth when prior-period volume is very small; useful for spike review |
| `rolling_average_complaint_count` | Smoothed moving average of complaint count across recent periods | `AVERAGE(complaint_count over trailing N periods)` | rolling period, recommended monthly | `sum of complaint_count over trailing N periods` | `number_of_periods_in_window` | `date_created`, `issue`, `issue_type`, `method`, `state` | `issue`, `issue_type`, `method`, `state`, `city`, `zip` | `AR-06` | Window size must be defined in implementation, e.g. 3-month or 6-month rolling average; early periods may have incomplete windows |

## KPI Edge Cases

- `complaint_growth_rate`
  - If the previous period complaint count is `0`, the measure should return blank, `N/A`, or a safe alternate value instead of dividing by zero.
- `period_over_period_change`
  - Interpretation should consider reporting grain because weekly and monthly changes can tell different stories.
- `complaint_share` and `issue_share`
  - Denominator logic must preserve slicers while removing only the category-level grouping needed for the comparison.
- `rolling_average_complaint_count`
  - The earliest periods in the time series may not have a full trailing window.
- All time-based KPIs
  - Depend on choosing the canonical reporting date; current preference is `date_created`, but this remains subject to validation against `ticket_created`.

## KPI Assumptions

- `id` is the base identifier used for ticket counting.
- `date_created` is the primary date used for trend measures unless later validation indicates `ticket_created` is more appropriate.
- The KPI catalog is limited to descriptive and comparative FCC complaint analytics.
- No KPI in this document requires internal telecom systems, subscriber counts, carrier performance measures, or SLA metrics.
- The KPI set is intended for later implementation as Power BI measures.

## Requirement Traceability

- `complaint_count` → `AR-01`, `AR-02`, `AR-03`, `AR-04`, `AR-05`, `AR-06`, `AR-07`
- `complaint_growth_rate` → `AR-01`, `AR-07`
- `complaint_share` → `AR-02`
- `issue_share` → `AR-03`, `AR-07`
- `period_over_period_change` → `AR-05`, `AR-06`
- `rolling_average_complaint_count` → `AR-06`

## Definition of Done for this Document

- All required KPIs for `AR-01` through `AR-07` are defined.
- Each KPI has an explicit formula, grain, numerator, denominator, and traceability reference.
- Edge cases and filter-context assumptions are documented for later Power BI implementation.
