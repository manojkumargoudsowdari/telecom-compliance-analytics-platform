# FCC Consumer Complaints Source Contract

## Purpose

This document defines the production source contract for the FCC
Consumer Complaints dataset used by the Telecom Compliance Analytics
Platform (TCAP) ingestion pipeline.

## Traceability

- Jira Ticket ID: `TCAP-4`
- Version: `1.0`
- Date: `2026-03-06`
- Phase: `Phase 3 - Production Data Ingestion Pipeline`
- Status: `Production source contract approved`

## 1. Data Source

- Source Name: `FCC Consumer Complaints`
- Provider: `Federal Communications Commission (FCC)`
- Access Method: `Open Data API`
- Dataset Portal: `https://www.fcc.gov/consumer-complaints-center-data`
- Source Classification: `Official public source`

## 2. Access Method

The ingestion pipeline retrieves data from the FCC public open data source
using the Socrata JSON API.

- Access Type: `API`
- Protocol: `HTTPS`
- Supported Formats: `JSON`
- Authentication: `None (public dataset)`
- Retrieval Pattern: `Paginated full snapshot batch pull`

## 3. Dataset Endpoint

The pipeline uses the FCC Socrata JSON base endpoint as the production
source for full snapshot ingestion.

- Production API Endpoint:
  `https://opendata.fcc.gov/resource/3xyp-aqkj.json`
- Dataset Landing Page:
  `https://opendata.fcc.gov/Consumer/CGB-Consumer-Complaints-Data/3xyp-aqkj`
- Metadata Endpoint:
  `https://opendata.fcc.gov/api/views/3xyp-aqkj`
- Columns Schema Endpoint:
  `https://opendata.fcc.gov/api/views/3xyp-aqkj/columns.json`
- Pagination Method: `$limit + $offset`
- Page Size: `50000`
- Contract Rule:
  `The production ingestion pipeline must use this base endpoint unless this document is updated`

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
- Ingestion Mode: `Batch full snapshot`
- Expected Refresh Behavior: `New and/or updated records may appear over time`

The pipeline should assume the dataset may change between runs and should
support repeatable full snapshot ingestion.

## 6. Source Guarantees

The ingestion design currently assumes the following:

- The dataset is publicly maintained by the FCC.
- The source schema may evolve over time.
- The number of records may increase over time.
- Historical data may be appended or updated.
- The source remains the authoritative external system for complaint
  records made available through this dataset.
- The JSON API supports paginated retrieval using `$limit` and `$offset`.

## 7. Source Reliability Risks

The ingestion pipeline must account for the following operational risks:

- API rate limits or throttling
- Schema changes or field additions/removals
- Dataset content updates between runs
- Pagination logic errors or incomplete page retrieval
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
