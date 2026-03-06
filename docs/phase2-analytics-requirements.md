# Phase 2 Analytics Requirements

## Document Control

- Jira Ticket ID: `TCAP-3`
- Git Commit Link: `<add commit URL after commit>`
- Version: `0.2-draft`
- Date: `2026-03-05`

## Purpose

Translate the approved Phase 2 business questions into structured analytics requirements that can guide dashboard design and later modeling work.

## Requirements

### Requirement ID: AR-01

- Business Question: Are complaint volumes increasing, decreasing, or remaining stable over time based on `date_created`?
- Metrics Required: `complaint_count`, `complaint_growth_rate`
- Dimensions: `date_created` (month)
- Filters: `issue_type`, `method`, `state`
- Expected Visualization: time-series line chart with KPI summary cards
- Notes / Assumptions: growth rate should be computed month-over-month; `date_created` is the current primary reporting-date candidate and should be validated against `ticket_created`

### Requirement ID: AR-02

- Business Question: Which complaint forms or service areas, such as `issue_type` and `method`, generate the highest complaint volume?
- Metrics Required: `complaint_count`, `complaint_share`
- Dimensions: `issue_type`, `method`
- Filters: `date_created`, `state`, `issue`
- Expected Visualization: ranked bar chart and share table
- Notes / Assumptions: counts should be shown in both absolute volume and percentage share to support leadership comparison

### Requirement ID: AR-03

- Business Question: Which issue categories in `issue` represent the largest share of total complaint activity?
- Metrics Required: `complaint_count`, `issue_share`
- Dimensions: `issue`
- Filters: `date_created`, `issue_type`, `method`, `state`
- Expected Visualization: ranked bar chart or treemap with optional percentage labels
- Notes / Assumptions: issue labels may require later standardization if category drift is observed across time

### Requirement ID: AR-04

- Business Question: Which states or cities contribute the highest complaint counts, and are those patterns stable over time?
- Metrics Required: `complaint_count`
- Dimensions: `state`, `city`, `date_created` (month)
- Filters: `issue_type`, `method`, `issue`, `zip`
- Expected Visualization: filled map or state heatmap plus ranked location table and trend view
- Notes / Assumptions: `state` should be the primary geography level; `city` should be treated as secondary and may need standardization review

### Requirement ID: AR-05

- Business Question: Are there visible spikes or unusual shifts in complaint activity by issue, issue type, or geography that warrant management attention?
- Metrics Required: `complaint_count`, `period_over_period_change`
- Dimensions: `date_created` (week or month), `issue`, `issue_type`, `state`
- Filters: `method`, `city`, `zip`
- Expected Visualization: annotated time-series chart with variance table or conditional-format matrix
- Notes / Assumptions: this requirement supports descriptive anomaly spotting, not predictive modeling; threshold rules will need to be defined in a later KPI design step

### Requirement ID: AR-06

- Business Question: Which complaint categories appear to be persistent versus event-driven when viewed across time?
- Metrics Required: `complaint_count`, `rolling_average_complaint_count`, `period_over_period_change`
- Dimensions: `date_created` (month), `issue`
- Filters: `issue_type`, `method`, `state`
- Expected Visualization: multi-series trend chart or small multiples by issue category
- Notes / Assumptions: persistence should be evaluated from repeated occurrence across periods rather than inferred business causality

### Requirement ID: AR-07

- Business Question: What concise narrative can be given to leadership about complaint concentration, trend direction, and the most prominent risk themes in the FCC data?
- Metrics Required: `complaint_count`, `complaint_growth_rate`, `issue_share`
- Dimensions: `date_created` (month), `issue_type`, `method`, `issue`, `state`
- Filters: `city`, `zip`
- Expected Visualization: executive summary page with KPI cards, top-issue table, and supporting charts
- Notes / Assumptions: this requirement is intended for leadership-ready storytelling; the narrative should summarize what changed, where it changed, and which issue themes dominate

## Source Inputs

- [phase2-business-problem.md](./phase2-business-problem.md)
- [phase2-data-understanding.md](./phase2-data-understanding.md)
- [phase2-data-dictionary.md](./phase2-data-dictionary.md)

## Non-Goals for Phase 2

- Building ingestion logic or a production data pipeline
- Implementing bronze, silver, or gold transformations
- Using internal telecom operational or subscriber datasets
- Designing carrier performance, SLA, or customer-account metrics

## Assumptions

- Requirements are limited to analytics that can be supported by the currently documented FCC fields.
- `date_created` is the leading candidate for trend reporting, with `ticket_created` retained as a validation field.
- Dashboard outputs are expected to support Power BI design and later Power BI implementation.

## Definition of Done for this Document

- Seven requirements are documented and aligned to the seven approved business questions.
- Each requirement specifies metrics, dimensions, filters, visualization intent, and assumptions.
- No unsupported internal telecom metrics or datasets are referenced.
