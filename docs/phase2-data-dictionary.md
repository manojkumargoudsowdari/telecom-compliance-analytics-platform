# Phase 2 Data Dictionary

## Document Control

- Jira Ticket ID: `TCAP-3`
- Git Commit Link: `<add commit URL after commit>`
- Version: `0.2-draft`
- Date: `2026-03-05`

## Purpose

Provide a field-level reference for the FCC complaint dataset to support analytics design, dataset profiling, and later ingestion mapping.

## Dataset Grain

- Working grain: `1 row = 1 FCC consumer complaint ticket`
- Validation status: `to validate from sample/schema`

## Candidate Primary Key

- `id`
  - FCC label: `Ticket ID`
  - Rationale: metadata describes this field as `Ticket Identifier`
  - Validation needed: confirm uniqueness in sample and full dataset

## Data Dictionary

| source_column_name | business_name | business_meaning | expected_type | example_values | nullable | role_in_model | phase2_usage |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | Ticket ID | Unique complaint ticket identifier assigned in the FCC dataset | number | `4923410`, `4947156` | no | identifier | Uniquely identify complaint records and validate dataset grain |
| `ticket_created` | Ticket Created Timestamp | Timestamp when the complaint was submitted to the FCC | date/time | `2021-07-26T21:59:38Z` | no | audit | Evaluate record creation timing and compare with reporting date choices |
| `date_created` | Complaint Created Date | Calendar date associated with complaint creation in the dataset | date | `2021-07-26T00:00:00` | no | dimension | Primary candidate for complaint trend analysis and date filtering |
| `issue_date` | Date of Issue | Date the consumer states the issue or violation occurred | date | `2021-08-12T00:00:00` | yes | dimension | Potential event-date analysis; validate completeness and outlier values before use |
| `issue_time` | Time of Issue | Consumer-reported time when the issue occurred | text | `1:17 p.m.`, `6:53 pm`, `` | yes | filter | Exploratory profiling only in Phase 2; likely low-value unless standardized later |
| `issue_type` | Form / Complaint Type | High-level complaint form category such as Phone, Internet, or TV | text | `Phone`, `TV`, `Internet` | no | dimension | Core category for dashboard slicing and scope filtering |
| `method` | Service Delivery Method | Manner in which the consumer gets the product or service | text | `Cable`, `Wired`, `Wireless (cell phone/other mobile device)` | yes | dimension | Important dimension for complaint mix analysis |
| `issue` | Issue Category | Specific issue the consumer is complaining about | text | `Billing`, `Unwanted Calls` | yes | dimension | Primary issue-category analysis field |
| `caller_id_number` | Caller ID Number | Number that appeared on caller ID for complaint types where applicable | text | `203-760-1637`, `None` | yes | filter | Exploratory field for robocall/unwanted-call subsets; not a core KPI field |
| `type_of_call_or_messge` | Type of Call or Message | Consumer-reported type of communication associated with the complaint | text | `Prerecorded Voice`, `` | yes | dimension | Candidate subcategory for unwanted-call analysis; spelling and semantics to validate from sample/schema |
| `advertiser_business_phone_number` | Advertiser / Business Phone Number | Phone number associated with the advertiser or business in the complaint context | text | `203-760-1637`, `None` | yes | filter | Exploratory field for call-related complaint patterns; may require cleansing |
| `city` | Consumer City | City where the consumer is located | text | `Wenhan`, `Prospect`, `Fort Lauderdale` | yes | dimension | Geographic analysis at city level, subject to standardization review |
| `state` | Consumer State | State where the consumer is located | text | `MA`, `CO`, `FL` | yes | dimension | Primary geography dimension for dashboards |
| `zip` | Consumer ZIP Code | ZIP code where the consumer is located | text | `01984`, `80130`, `33301` | yes | filter | Candidate fine-grained geography filter; validate missing/placeholder values |
| `location_1` | ZIP Center Point Location | Geocoded point for the center of the ZIP code, not the individual address | point | `{latitude: 42.59996, longitude: -70.881083}` | yes | dimension | Candidate map field for state/ZIP visualizations; validate suitability for analytics |
| `location_1_address` | ZIP Geocode Address Component | Address component used in the derived ZIP center-point geocode | text | `40601 1034`, `` | yes | audit | Metadata/derived-field support only; not a primary analytics field |
| `location_1_city` | ZIP Geocode City Component | Derived city/locality component used in the center-point geocode | text | `CA`, `TX` | yes | audit | Derived location helper field; semantics to validate from sample/schema because values resemble state codes |
| `type_of_property_goods_or_services` | Property / Goods / Services Type | Supplemental classification for certain complaint contexts | text | `None`, `Health Insurance Services`, `unknown_services` | yes | dimension | Exploratory dimension; likely relevant only for certain issue subsets |
| `location_1_state` | ZIP Geocode State Component | Derived state component used in the center-point geocode | text | `CA`, `TX`, `` | yes | audit | Geocoding support field; not expected to be a primary reporting dimension |
| `location_1_zip` | ZIP Geocode ZIP Component | Derived ZIP component used in the center-point geocode | text | `20850`, `51401-3049` | yes | audit | Geocoding support field; may help validate geographic consistency |
| `:@computed_region_5ic8_3ue4` | Computed Region Code | FCC/Socrata computed geographic region identifier derived from the location point | number | `26`, `9`, `31` | yes | audit | Platform-generated region field; business use to validate from sample/schema |

## Candidate Dimensions

- `date_created`
- `issue_date`
- `issue_type`
- `method`
- `issue`
- `city`
- `state`
- `zip`
- `type_of_call_or_messge`
- `type_of_property_goods_or_services`

## Candidate Filters for Dashboards

- Complaint date
- Issue type
- Method
- Issue category
- State
- City
- ZIP

## Known Ambiguities / To Validate

- Whether `date_created` or `ticket_created` should be the canonical reporting date
- Whether `issue_date` contains unusable outliers or placeholder dates in the full source
- Whether `location_1_city` is mislabeled or carries transformed state-like values
- Whether `type_of_property_goods_or_services` is analytically relevant for telecom-focused reporting or only for subsets
- Whether `type_of_call_or_messge` spelling should be preserved from source or standardized later
- Whether the computed region field has any business reporting value beyond internal platform metadata

## Source URLs

- `https://opendata.fcc.gov/api/views/3xyp-aqkj`
- `https://opendata.fcc.gov/api/views/3xyp-aqkj/columns.json`
- `https://opendata.fcc.gov/resource/3xyp-aqkj.json?$limit=1000`

## Assumptions

- This dictionary is based only on the official FCC metadata, columns schema, and sample API endpoints.
- Nullable status is inferred from the official schema cached contents and should be treated as draft until validated during profiling.
- Business names and usage guidance are Phase 2 design interpretations, not FCC official terminology.

## Definition of Done for this Document

- Analytically relevant source fields visible in the FCC schema/sample are documented.
- Candidate identifier, dimensions, and filters are identified.
- Known ambiguities are explicitly called out for later validation.
- No telecom-internal fields or invented measures are introduced.
