# Phase 2 Data Understanding

## Document Control

- Jira Ticket ID: `TCAP-3`
- Git Commit Link: `<add commit URL after commit>`
- Version: `0.2-draft`
- Date: `2026-03-05`

## Purpose

Document the official FCC complaint dataset structure, practical analytical scope, likely grain, constraints, and known quality risks before designing ingestion or reporting logic.

## Data Source Reference

- Dataset name: `CGB Consumer Complaints Data`
- Publisher: `Federal Communications Commission (FCC)`
- Landing page: `https://opendata.fcc.gov/Consumer/CGB-Consumer-Complaints-Data/3xyp-aqkj`
- FCC Consumer Help Center API information page: `https://www.fcc.gov/consumer-help-center-api`
- Metadata endpoint: `https://opendata.fcc.gov/api/views/3xyp-aqkj`
- Columns/schema endpoint: `https://opendata.fcc.gov/api/views/3xyp-aqkj/columns.json`
- Sample API endpoint: `https://opendata.fcc.gov/resource/3xyp-aqkj.json?$limit=1000`

## Dataset Scope

The FCC describes this dataset as individual informal consumer complaint data beginning October 31, 2014. The published records represent information selected by the consumer and are not independently verified by the FCC.

### Scope Notes

- Complaint type coverage appears broader than only telecom carrier service complaints and may include issue types such as phone, TV, and related consumer complaint categories.
- Initial profiling should confirm whether the dataset is appropriate as-is for telecom compliance analytics or whether later filtering rules will be required.
- A 1000-row sample from the official FCC API is sufficient for initial structural profiling in Phase 2.

## Dataset Grain

- Working grain assumption: `1 row = 1 FCC consumer complaint ticket`
- Primary identifier candidate: `id`
- Grain validation steps:
  - Confirm `id` uniqueness in the 1000-row sample.
  - Check whether multiple rows can represent updates to the same complaint.
  - Verify whether downstream analysis should use `ticket_created` or `date_created` as the primary reporting date.

## Expected Key Dimensions

Based on the official FCC columns endpoint, the most likely analytical dimensions currently visible are:

- Complaint ticket identifier: `id`
- Ticket creation timestamp: `ticket_created`
- Complaint creation date: `date_created`
- Issue occurrence date: `issue_date`
- Complaint channel or service method: `method`
- Issue category: `issue`
- Issue type: `issue_type`
- Geography: `city`, `state`, `zip`

### Placeholder for Notebook Results

- Observed in 1000-row sample:
  - Row count: `1000`
  - Column count: `17`
  - Column names: `id`, `ticket_created`, `date_created`, `issue_time`, `issue_type`, `method`, `issue`, `caller_id_number`, `type_of_call_or_messge`, `advertiser_business_phone_number`, `city`, `state`, `zip`, `location_1`, `type_of_property_goods_or_services`, `:@computed_region_5ic8_3ue4`, `issue_date`
  - Pandas-inferred dtypes from the sample:
    - `id`: `int64`
    - `ticket_created`: `object`
    - `date_created`: `object`
    - `issue_time`: `datetime64[ns]` in the sample profiling run, but source semantics remain text-like and should not be treated as a clean time field without further validation
    - `issue_type`, `method`, `issue`, `caller_id_number`, `type_of_call_or_messge`, `advertiser_business_phone_number`, `city`, `state`, `zip`, `location_1`, `type_of_property_goods_or_services`, `issue_date`: `object`
    - `:@computed_region_5ic8_3ue4`: `float64`
  - Likely categorical fields confirmed in the sample: `issue_type`, `method`, `issue`, `state`, `city`, `zip`

## Initial Data Quality Risks

- Missing-field risk:
  - Observed in the 1000-row sample:
    - `issue_time`: `543` nulls
    - `issue_date`: `507` nulls
    - `:@computed_region_5ic8_3ue4`: `22` nulls
    - `location_1`: `2` nulls
- Analytical coverage risk:
  - The dataset does not currently expose fields needed for carrier-level benchmarking, subscriber-normalized metrics, or SLA-style reporting.
- Consumer-entered data risk:
  - Some values are consumer-selected and may be inconsistent, incomplete, or noisy.
- Category drift risk:
  - Issue labels and methods may vary over time, requiring normalization in later phases.
- Date ambiguity risk:
  - Multiple date-like fields exist and may represent different business events.

## Analytical Opportunities

- Complaint volume trend analysis using complaint creation dates
- Issue-type and issue-category concentration analysis
- Geographic hotspot analysis using state and city
- Service-method analysis using `method`
- Exploratory anomaly checks on complaint counts over time or by state/issue
- Observed high-value dimensions in the 1000-row sample:
  - Top `state` values: `CA (136)`, `TX (85)`, `FL (72)`, `NY (62)`, `IL (38)`
  - Top `issue_type` values: `Phone (675)`, `Internet (185)`, `TV (109)`
  - Top `method` values: `Wireless (cell phone/other mobile device) (405)`, `Cable (134)`, `Wired (132)`, `Internet (VOIP) (131)`
  - Top `issue` values: `Unwanted Calls (448)`, `Billing (170)`, `Availability (112)`, `Availability (including rural call completion) (66)`, `Equipment (58)`

## Dataset Limitations

- The FCC explicitly notes that it does not verify the facts alleged in the complaints.
- The sample and schema do not currently show a `company` field.
- The sample and schema do not currently show a `timely_response` field.
- The approved Phase 2 dashboard design is limited to issue, issue type, method, time, and geography analysis supported by the FCC source.
- This dataset alone is not sufficient for carrier benchmarking, response-performance analysis, or internal operational reporting without an additional source.

## Open Questions

- Does the full dataset expose additional carrier-related fields not visible in the initial sample/schema review?
- Which date field should be treated as the canonical complaint reporting date for trends?
- Should Phase 3 scope include only telecom-relevant issue types through explicit filtering?
- Are additional FCC or external datasets needed to support response-performance KPIs?

## Sample Profiling Findings

### Observed in 1000-Row Sample

- Sample endpoint used: `https://opendata.fcc.gov/resource/3xyp-aqkj.json?$limit=1000`
- Sample date coverage:
  - `ticket_created`: minimum `2021-04-20 18:48:15+00:00`, maximum `2024-05-11 17:20:55+00:00`, non-null `1000`
  - `date_created`: minimum `2021-04-20`, maximum `2024-05-11`, non-null `1000`
  - `issue_date`: minimum `2020-04-23`, maximum `2024-02-05`, non-null `493`
- The sample is heavily concentrated in `issue_type = Phone` and `issue = Unwanted Calls`, which suggests the sample is suitable for initial complaint trend and issue-mix profiling.

### Pending Full-Ingestion Validation

- The 1000-row sample is not sufficient to assume category distributions match the full FCC dataset.
- Full-dataset profiling is still required to confirm:
  - `id` uniqueness across all records
  - stability of `issue_type`, `method`, and `issue` distributions
  - whether `date_created` should remain the canonical reporting date
  - whether `issue_time` should be treated as a usable field or retained only as low-value source text
  - whether any additional fields become visible or relevant under a broader extraction pattern

## Source URLs

- `https://opendata.fcc.gov/Consumer/CGB-Consumer-Complaints-Data/3xyp-aqkj`
- `https://www.fcc.gov/consumer-help-center-api`
- `https://opendata.fcc.gov/api/views/3xyp-aqkj`
- `https://opendata.fcc.gov/api/views/3xyp-aqkj/columns.json`
- `https://opendata.fcc.gov/resource/3xyp-aqkj.json?$limit=1000`

## Assumptions

- Phase 2 remains limited to discovery and analytics design.
- FCC official metadata and API endpoints are the authoritative source for this document.
- Notebook-derived profiling results will be added after the sample is run in a connected environment.
- `date_created` is the current primary reporting-date candidate, with `ticket_created` retained for validation.

## Definition of Done for this Document

- Official FCC source references are documented.
- Dataset scope and practical grain are described.
- Expected analytical dimensions are mapped from the official schema.
- Initial risks, limitations, and open questions are captured.
- Placeholder fields are ready to be updated from notebook profiling results.
