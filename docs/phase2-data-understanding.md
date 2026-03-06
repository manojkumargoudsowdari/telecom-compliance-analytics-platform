# Phase 2 Data Understanding

## Document Control

- Jira Ticket ID: `TCAP-3`
- Git Commit Link: `<add commit URL after commit>`
- Version: `0.1-draft`
- Date: `2026-03-05`

## Purpose

Document the FCC complaint dataset structure, analytical grain, constraints, and known quality risks before designing ingestion or reporting logic.

## Data Source

- Source Name: `FCC Consumer Complaint Dataset`
- Source Endpoint: `<add dataset URL>`
- Access Method: `<API / CSV download / portal export>`
- License / Usage Notes: `<add source usage notes>`

## Dataset Grain

- Expected grain: `1 row = 1 telecom complaint`
- Grain validation approach: `<describe how row uniqueness will be confirmed>`

## Expected Analytical Dimensions

- Time
- Carrier
- Geography
- Issue category
- Sub-issue
- Response performance

## Schema Overview

| Field Name | Expected Type | Nullable | Analytical Role | Notes |
| --- | --- | --- | --- | --- |
| `<field_name>` | `<type>` | `<yes/no>` | `<dimension/measure/audit>` | `<notes>` |

## Profiling Summary

### Record Counts

- Sample size reviewed: `<count>`
- Distinct complaint identifiers: `<count>`
- Distinct carriers: `<count>`
- Distinct issue categories: `<count>`

### Date Coverage

- Minimum complaint date: `<date>`
- Maximum complaint date: `<date>`
- Coverage gaps observed: `<notes>`

### Initial Observations

- `<observation 1>`
- `<observation 2>`
- `<observation 3>`

## Data Quality Risks

- Missing critical identifiers: `<risk>`
- Inconsistent carrier naming: `<risk>`
- Null or ambiguous SLA fields: `<risk>`
- Duplicate complaints or duplicate extracts: `<risk>`
- Categorical drift across time: `<risk>`

## Assumptions

- The FCC source provides a stable complaint-level dataset suitable for trend analysis.
- Initial profiling will be done on a sample, not the full extract.
- Field meanings may require confirmation against FCC metadata documentation.

## Open Questions

- `<question 1>`
- `<question 2>`
- `<question 3>`

## Definition of Done for this Document

- Dataset grain is explicitly defined.
- Key analytical dimensions are identified.
- Initial schema summary is documented.
- Key data quality risks and open questions are captured.
