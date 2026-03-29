# Phase 6 Power BI Implementation Notes

## 1. Purpose

This document is a manual implementation-notes stub for the Power BI
reporting-layer build.

It is intended to be updated manually during Power BI Desktop
implementation and review.

## 2. Report Context

- Jira ticket:
  - `TCAP-28`
- approved Gold fact sources:
  - `data/gold/fact_complaints_daily/`
  - `data/gold/fact_complaints_monthly/`
- approved KPI scope:
  - `complaint_count`
  - `complaint_growth_rate`
  - `rolling_average_complaint_count`
  - `category_share`

## 3. Data Source Notes

- Power Query query name:
  - `fact_complaints_daily`
- source path:
  - `[update during implementation]`
- import status:
  - `[not started]`
- notes:
  - `[add notes]`

- Power Query query name:
  - `fact_complaints_monthly`
- source path:
  - `[update during implementation]`
- import status:
  - `[not started]`
- notes:
  - `[add notes]`

## 4. Semantic Model Notes

- daily fact loaded:
  - `[not started]`
- monthly fact loaded:
  - `[not started]`
- semantic dimensions approach used:
  - `[update after implementation]`
- relationship notes:
  - `[add notes]`

## 5. Measure Notes

- `complaint_count`
  - `[not started]`
- `complaint_growth_rate`
  - `[not started]`
- `rolling_average_complaint_count`
  - `[not started]`
- `category_share`
  - `[not started]`

## 6. Dashboard Page Status

- Page 1: Compliance Overview
  - `[not started]`
- Page 2: Issue Type and Method Analysis
  - `[not started]`
- Page 3: Issue Category Analysis
  - `[not started]`
- Page 4: Geographic Analysis
  - `[not started]`
- Page 5: Trend and Anomaly Monitoring
  - `[not started]`

## 7. Constraints and Follow-Up Notes

- do not mix daily and monthly facts in one visual
- do not expose unsupported KPIs
- `category_share` must remain reporting-layer only
- `period_over_period_change` remains outside the approved KPI scope
- follow-up items:
  - `[add items during implementation]`
