# Phase 2 Data Dictionary

## Document Control

- Jira Ticket ID: `TCAP-3`
- Git Commit Link: `<add commit URL after commit>`
- Version: `0.1-draft`
- Date: `2026-03-05`

## Purpose

Provide a field-level reference for the FCC complaint dataset to support ingestion mapping, analytics design, and dashboard development.

## Dictionary

| Column Name | Business Description | Type | Example Value | Required | Usage | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `<column_name>` | `<business meaning>` | `<string/date/integer/...>` | `<example>` | `<yes/no>` | `<dimension/measure/filter/audit>` | `<notes>` |

## Candidate Priority Fields

- Complaint identifier
- Complaint received date
- Carrier / company
- State
- Issue
- Sub-issue
- Timely response flag
- Consumer consent or closure status if available

## Naming and Standardization Notes

- `<document standard naming decisions here>`

## Assumptions

- Field names and definitions will be validated against FCC metadata.
- Some source fields may be renamed later for curated silver/gold models.

## Definition of Done for this Document

- All analytically relevant source fields are documented.
- Each field has a business description and intended usage.
- Required versus optional fields are identified.
- Standardization notes are captured where ambiguity exists.
