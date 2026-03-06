# FCC Consumer Complaints Source Contract

## Purpose

This document defines the draft production source contract for the FCC
Consumer Complaints dataset used by the Telecom Compliance Analytics
Platform (TCAP) ingestion pipeline.

This PR establishes the source contract draft for Phase 3. Endpoint
validation is intentionally deferred to the next task so the ingestion
pipeline can be implemented against a documented contract while the final
machine-readable extraction URL is confirmed.

## Traceability

- Jira Ticket ID: `TCAP-4`
- Version: `0.2-draft`
- Date: `2026-03-06`
- Phase: `Phase 3 - Production Data Ingestion Pipeline`
- Status: `Draft source contract pending endpoint validation`

## 1. Data Source

- Source Name: `FCC Consumer Complaints`
- Provider: `Federal Communications Commission (FCC)`
- Access Method: `Open Data API / downloadable open dataset`
- Dataset Portal: `https://www.fcc.gov/consumer-complaints-center-data`
- Source Classification: `Official public source`

## 2. Access Method

The ingestion pipeline retrieves data from the FCC public open data source
using a machine-readable endpoint.

- Access Type: `API`
- Protocol: `HTTPS`
- Supported Formats: `JSON / CSV`
- Authentication: `None (public dataset)`
- Retrieval Pattern: `Batch pull`

## 3. Dataset Endpoint

The pipeline will use the FCC open data endpoint once validated during the
next implementation task.

- Candidate API Endpoint:
  `https://opendata.fcc.gov/resource/consumer-complaints.csv`
- Endpoint Status: `Draft - to be validated before production use`
- Contract Rule:
  `The validated endpoint becomes the sole production extraction endpoint unless this document is updated`

## 4. Expected Schema (Initial)

The following fields represent the initial expected schema observed during
profiling and documentation. This is the schema contract the ingestion
pipeline expects at the start of Phase 3.

- `id`
- `ticket_created`
- `issue_time`
- `issue_type`
- `method`
- `issue`
- `caller_id_number`
- `city`
- `state`
- `zip`
- `type_of_call_or_message`
- `advertiser_business_phone_number`
- `type_of_property_goods_or_services`
- `issue_date`

## 5. Update Frequency

- Update Frequency: `Periodic`
- Ingestion Mode: `Batch`
- Expected Refresh Behavior: `New and/or appended records may appear over time`

Until the FCC publishing cadence is validated, the pipeline should assume
the dataset may change between runs and should support repeatable
ingestion.

## 6. Source Guarantees

The ingestion design currently assumes the following:

- The dataset is publicly maintained by the FCC.
- The source schema may evolve over time.
- The number of records may increase over time.
- Historical data may be appended or updated.
- The source remains the authoritative external system for complaint
  records made available through this dataset.

## 7. Source Reliability Risks

The ingestion pipeline must account for the following operational risks:

- API rate limits or throttling
- Schema changes or field additions/removals
- Dataset content updates between runs
- Temporary source downtime or network failures
- Endpoint relocation or portal changes
- Incomplete or delayed source publishing

## Why This Step Matters

Enterprise ingestion pipelines define a source contract before
implementation because this:

- prevents silent schema breakage
- documents data lineage
- supports governance and audit
- clarifies assumptions for downstream bronze, silver, and gold layers

Without a documented source contract, the ingestion pipeline becomes
fragile and harder to operate safely in production.
