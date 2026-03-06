# Metadata Folder Guidance

## Purpose

This folder stores lightweight metadata artifacts used during discovery and analytics design.

## What Goes Here

- Source metadata notes
- Column lists
- Data dictionaries
- Schema snapshots
- Small text-based profiling outputs
- Sample field mappings

## What Must Not Go Here

- Full FCC dataset extracts
- Large CSV exports
- Raw complaint records containing sensitive or operationally heavy data
- Binary dashboard files
- Production ingestion outputs

## Traceability

- Jira Ticket ID: `TCAP-3`
- Git Commit Link: `<add commit URL after commit>`
- Version: `0.1-draft`
- Date: `2026-03-05`

## Assumptions

- Metadata artifacts stored here are lightweight, reviewable, and safe to version.
- Any actual raw extracts belong in the appropriate data layer only after ingestion design is approved.

## Definition of Done for this Document

- Folder purpose is clearly stated.
- Allowed and disallowed contents are explicit.
- Traceability fields are present.
