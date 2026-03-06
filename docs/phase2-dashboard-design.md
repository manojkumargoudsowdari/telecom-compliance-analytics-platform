# Phase 2 Dashboard Design

## Document Control

- Jira Ticket ID: `TCAP-3`
- Git Commit Link: `<add commit URL after commit>`
- Version: `0.2-draft`
- Date: `2026-03-05`

## Purpose

Translate the approved FCC-based analytics requirements and KPI catalog into a realistic Power BI dashboard design specification for telecom compliance monitoring.

## Dashboard Overview

The dashboard is designed as a multi-page Power BI report for compliance leadership, regulatory reporting stakeholders, and analytics users who need a structured view of FCC consumer complaint activity. The report is intentionally limited to what can be supported by the FCC complaint fields documented in Phase 2.

The report design emphasizes:

- simple executive summary indicators
- trend monitoring over time
- issue-type and method distribution
- issue-category concentration
- geography-based complaint monitoring
- descriptive anomaly spotting

## Page 1: Compliance Overview

- Purpose:
  - Provide a leadership-level summary of total complaint activity, directional trend, and top issue concentration.
- Target audience:
  - Compliance leadership
  - Regulatory affairs leadership
  - Reporting leads
- KPIs shown:
  - `complaint_count`
  - `complaint_growth_rate`
  - `issue_share`
- Visuals:
  - KPI card: total complaint count
  - KPI card: complaint growth rate
  - monthly trend line using `date_created`
  - top issue table or bar chart using `issue`
  - supporting slicer summary panel
- Filters:
  - `date_created`
  - `issue_type`
  - `method`
  - `state`
- Drilldowns:
  - month to lower period grain if enabled later
  - top issue visual to Page 3
  - state selection to Page 4
- Notes:
  - This page should answer the executive question: what changed and where should leadership look next.

## Page 2: Issue Type and Method Analysis

- Purpose:
  - Compare complaint mix across `issue_type` and `method` to understand which service areas or delivery methods drive the highest complaint volumes.
- Target audience:
  - Compliance analysts
  - Reporting analysts
  - Operational reviewers
- KPIs shown:
  - `complaint_count`
  - `complaint_share`
- Visuals:
  - ranked bar chart by `issue_type`
  - ranked bar chart by `method`
  - matrix crossing `issue_type` and `method`
  - share visualization showing relative mix within current filter context
- Filters:
  - `date_created`
  - `issue`
  - `state`
  - `city`
- Drilldowns:
  - `issue_type` to `method`
  - selection from `issue_type` or `method` to Page 5 for trend monitoring
- Notes:
  - Relative mix matters as much as raw count on this page, so both count and share should be visible.

## Page 3: Issue Category Analysis

- Purpose:
  - Identify dominant complaint categories and distinguish persistent issue themes from short-lived spikes.
- Target audience:
  - Compliance analysts
  - Regulatory reporting teams
- KPIs shown:
  - `complaint_count`
  - `issue_share`
  - `rolling_average_complaint_count`
  - `period_over_period_change`
- Visuals:
  - ranked issue bar chart using `issue`
  - issue share chart
  - monthly trend line by selected issue
  - small multiples or multi-series trend view for top issue categories
- Filters:
  - `date_created`
  - `issue_type`
  - `method`
  - `state`
- Drilldowns:
  - issue selection to issue trend detail within the same page
  - issue selection to Page 5 for anomaly review
- Notes:
  - This page supports both AR-03 and AR-06 and should make persistence versus event-driven patterns easier to interpret.

## Page 4: Geographic Analysis

- Purpose:
  - Show where complaint activity is concentrated and whether those geographic patterns are stable over time.
- Target audience:
  - Compliance leadership
  - Regulatory affairs
  - Analysts preparing location-based summaries
- KPIs shown:
  - `complaint_count`
- Visuals:
  - filled map or state-level heatmap using `state`
  - ranked state table
  - ranked city table
  - optional trend chart for selected geography over time
- Filters:
  - `date_created`
  - `issue_type`
  - `method`
  - `issue`
  - `zip`
- Drilldowns:
  - state to city
  - state or city to Page 5 for trend and anomaly monitoring
- Notes:
  - `state` is the primary geography dimension; `city` should be treated carefully because standardization issues may exist.

## Page 5: Trend and Anomaly Monitoring

- Purpose:
  - Surface period-over-period shifts, spikes, and unusual movement in complaint activity across issue, issue type, method, and geography.
- Target audience:
  - Compliance analysts
  - Reporting analysts
  - Leadership reviewers needing exception-based monitoring
- KPIs shown:
  - `complaint_count`
  - `period_over_period_change`
  - `rolling_average_complaint_count`
  - `complaint_growth_rate`
- Visuals:
  - time-series line chart with rolling average overlay
  - variance table with conditional formatting
  - issue or geography comparison matrix
  - focused exception panel for largest increases and decreases
- Filters:
  - `date_created`
  - `issue`
  - `issue_type`
  - `method`
  - `state`
  - `city`
  - `zip`
- Drilldowns:
  - trend anomaly by issue
  - trend anomaly by state
  - trend anomaly by issue type or method
- Notes:
  - This page is for descriptive monitoring only. It should not imply predictive scoring or root-cause attribution.

## Global Filters

- `date_created`
- `issue_type`
- `method`
- `issue`
- `state`
- `city`
- `zip`

## Drilldown Paths

- Compliance Overview → Issue Category Analysis
- Compliance Overview → Geographic Analysis
- Issue Type and Method Analysis → Trend and Anomaly Monitoring
- Issue Category Analysis → Trend and Anomaly Monitoring
- Geographic Analysis → Trend and Anomaly Monitoring
- Geographic Analysis: state → city

## KPI-to-Visual Mapping

- `complaint_count`
  - KPI cards
  - line charts
  - ranked bar charts
  - maps
  - tables
- `complaint_growth_rate`
  - KPI cards
  - executive summary visuals
  - trend monitoring visuals
- `complaint_share`
  - issue type / method comparison charts
  - share tables
- `issue_share`
  - issue concentration charts
  - executive summary support visuals
- `period_over_period_change`
  - variance tables
  - anomaly review charts
  - issue persistence comparison visuals
- `rolling_average_complaint_count`
  - smoothed trend lines
  - issue trend comparison visuals

## Assumptions and Limitations

- The dashboard is based only on FCC-supported fields: `date_created`, `ticket_created`, `issue_type`, `method`, `issue`, `city`, `state`, and `zip`.
- No page includes subscriber KPIs, SLA metrics, carrier operations measures, or internal case-management views.
- The report is intended for external complaint monitoring, not as evidence of confirmed non-compliance.
- `date_created` is the default reporting date unless later validation supports `ticket_created` as the preferred reporting timestamp.
- Phase 2 defines the logical Power BI design only; final layout, formatting, and Power BI measure implementation are deferred to later build phases.

## Definition of Done for this Document

- Five dashboard pages are defined with clear business purpose and audience.
- Approved KPIs are mapped to appropriate visuals.
- Global filters and drilldown paths are documented.
- Unsupported internal telecom reporting concepts are excluded.
