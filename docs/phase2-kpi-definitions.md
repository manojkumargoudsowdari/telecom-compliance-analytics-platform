# Phase 2 KPI Definitions

## Document Control

- Jira Ticket ID: `TCAP-3`
- Git Commit Link: `<add commit URL after commit>`
- Version: `0.1-draft`
- Date: `2026-03-05`

## Purpose

Define the metrics that will be used to measure complaint activity, distribution, and response performance.

## KPI Catalog

| KPI Name | Formula | Grain | Numerator | Denominator | Business Purpose | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Complaint Volume | `COUNT(complaint_id)` | `<time grain>` | `COUNT(complaint_id)` | `N/A` | Monitor overall complaint activity | `<notes>` |
| Complaint Growth Rate | `(current_period - previous_period) / previous_period` | `<time grain>` | `current period complaints - previous period complaints` | `previous period complaints` | Detect rising complaint patterns | Define handling when prior period is zero |
| Carrier Complaint Share | `carrier_complaints / total_complaints` | `<time grain>` | `carrier complaints` | `all complaints in filter context` | Compare carrier complaint load | Should sum to 100% within same filter context |
| Issue Category Distribution | `complaints_by_issue / total_complaints` | `<time grain>` | `complaints for issue` | `all complaints in filter context` | Identify dominant complaint causes | `<notes>` |
| Timely Response Rate | `timely_responses / total_responses` | `<time grain>` | `timely responses` | `all responses` | Measure responsiveness | Confirm source semantics for SLA status |

## KPI Design Notes

- `<note 1>`
- `<note 2>`

## Assumptions

- Complaint identifier uniqueness will be validated before KPI implementation.
- KPI filter context rules will be applied consistently across all visuals.

## Definition of Done for this Document

- Each KPI has a formula and business purpose.
- Numerator and denominator definitions are explicit.
- Edge cases and assumptions are documented.
