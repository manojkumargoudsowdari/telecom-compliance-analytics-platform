# Phase 4-2 Silver Schema Contract

## 1. Overview

This document defines the schema contract for the FCC Consumer
Complaints Silver layer in the Telecom Compliance Analytics Platform
(TCAP).

It follows the functional boundary established in
`docs/phase4/phase4-1-silver-functional-spec.md` and defines the
canonical persisted structure of `silver_fcc_consumer_complaints`.

This contract is intentionally limited to schema shape, column typing,
nullability, and structural expectations. It does not define
transformation rules, quality thresholds, or reject-handling behavior.

The contract is based on the approved Phase 3 source contract and the
committed full-run evidence in the repository. It is intended to be a
durable analytics-facing contract rather than a one-off reflection of a
single raw sample.

## 2. Dataset Definition

- Dataset name: `silver_fcc_consumer_complaints`
- Grain: `one latest valid record per complaint_id`
- Applies to: `the persisted Silver dataset produced from Phase 3 FCC raw runs`

The contract assumes Silver records are derived from raw FCC payloads
landed under `data/raw/fcc/consumer_complaints/{run_id}/` and remain
traceable to the originating raw ingestion run.

The naming approach is intentionally conservative:

- use canonical Silver names where the improvement is structural and
  low-risk, such as `complaint_id`, `zip_code`, and
  `type_of_call_or_message`
- retain source-faithful temporal names where aggressive business
  renaming would imply semantics that are not yet formally approved

## 3. Schema Design Principles

- Deterministic: column names, data types, and nullability must not vary
  across runs without an approved schema revision
- Analytics-ready: fields should be directly usable for filtering,
  slicing, and trend analysis without Gold-layer aggregation logic
- Traceable to raw: Silver records must retain enough lineage to link
  back to the Phase 3 raw run
- Strict typing: canonical types must be defined explicitly rather than
  inferred downstream
- Minimal business logic: the contract should standardize structure, not
  embed KPI logic or reporting interpretations
- Explicit nullability: nullable versus required fields must be declared
  intentionally
- Stable column names: Silver names should be durable and avoid carrying
  obvious raw-source spelling defects where a safe canonical name exists
- Semantic stability: where source-business meaning is not yet fully
  settled, prefer a source-faithful canonical name over a more
  interpretive business alias

## 4. Column-Level Schema Contract

### A. Technical / Lineage Fields

| column_name | data_type | nullable | description | source_notes |
| --- | --- | --- | --- | --- |
| `source_run_id` | `STRING` | `NO` | Phase 3 raw ingestion run identifier that produced the source snapshot | Derived from raw landing path and metadata file name |
| `silver_processed_at_utc` | `TIMESTAMP` | `NO` | UTC timestamp when the Silver record was materialized | Derived during Silver processing |
| `source_system` | `STRING` | `NO` | Stable source-system label for the dataset | Constant value: `fcc_consumer_complaints` |

### B. Complaint Identity Fields

| column_name | data_type | nullable | description | source_notes |
| --- | --- | --- | --- | --- |
| `complaint_id` | `STRING` | `NO` | Canonical FCC complaint identifier for the Silver record | Mapped from raw field `id`; kept as string to preserve source representation |

### C. Date / Temporal Fields

| column_name | data_type | nullable | description | source_notes |
| --- | --- | --- | --- | --- |
| `ticket_created_utc` | `TIMESTAMP` | `YES` | FCC ticket-creation timestamp retained for audit and event sequencing | Mapped from raw field `ticket_created`; retained in source-faithful form because a business alias such as "submitted" or "received" has not yet been formally approved |
| `date_created` | `DATE` | `NO` | Canonical complaint date retained from the FCC source for current Silver analytics | Mapped from raw field `date_created`; retained in source terminology to avoid asserting a stronger business meaning than the current contract supports |
| `issue_date` | `DATE` | `YES` | Consumer-reported date on which the issue occurred | Mapped from raw field `issue_date` |
| `issue_time_raw` | `STRING` | `YES` | Raw consumer-reported issue time retained as text because the source values are not yet contract-safe as a typed time field | Mapped from raw field `issue_time` |

### D. Product / Issue Fields

| column_name | data_type | nullable | description | source_notes |
| --- | --- | --- | --- | --- |
| `issue_type` | `STRING` | `YES` | High-level complaint type or category exposed by the FCC source | Mapped from raw field `issue_type`; current source does not expose a separate `product` field |
| `issue` | `STRING` | `YES` | Specific issue category associated with the complaint | Mapped from raw field `issue` |
| `type_of_property_goods_or_services` | `STRING` | `YES` | Supplemental complaint classification present for some source records | Mapped from raw field `type_of_property_goods_or_services` |
| `type_of_call_or_message` | `STRING` | `YES` | Standardized Silver name for the raw call/message subtype field | Mapped from raw field `type_of_call_or_messge`; Silver corrects the raw spelling defect in the column name only |

### E. Company / Response Fields

Company and response-management concepts remain relevant to the broader
complaint domain, but the current FCC raw source evidenced in Phase 3
does not expose those columns.

The following fields are therefore reviewed intentionally but are not
part of the initial persisted Silver schema contract:

| candidate_field | status | review_note |
| --- | --- | --- |
| `company` | `not_in_initial_contract` | Complaint-domain relevant, but not present in the current FCC raw source |
| `company_public_response` | `not_in_initial_contract` | Not present in the current FCC raw source |
| `company_response_to_consumer` | `not_in_initial_contract` | Not present in the current FCC raw source |
| `timely_response_flag` | `not_in_initial_contract` | Not present in the current FCC raw source |

### F. Consumer Outcome / Dispute Fields

Consumer outcome and dispute concepts were also reviewed explicitly.

The following fields are not part of the initial persisted Silver
schema contract because they are not present in the current FCC raw
source:

| candidate_field | status | review_note |
| --- | --- | --- |
| `consumer_disputed_flag` | `not_in_initial_contract` | Complaint-domain relevant, but not present in the current FCC raw source |

### G. Submission / Channel Fields

| column_name | data_type | nullable | description | source_notes |
| --- | --- | --- | --- | --- |
| `method` | `STRING` | `YES` | Service delivery method or complaint context dimension carried from the FCC source | Mapped from raw field `method`; retained in source-faithful form because `submitted_via` would imply a narrower submission-channel meaning than the current source contract supports |

### H. Geography Fields

| column_name | data_type | nullable | description | source_notes |
| --- | --- | --- | --- | --- |
| `city` | `STRING` | `YES` | Consumer city as represented in the FCC source | Mapped from raw field `city` |
| `state` | `STRING` | `YES` | Consumer state or territory code | Mapped from raw field `state`; intended normalized target remains a state code stored as text |
| `zip_code` | `STRING` | `YES` | Consumer ZIP/postal code retained as text | Mapped from raw field `zip`; Silver uses `zip_code` as the canonical name |
| `caller_id_number` | `STRING` | `YES` | Caller ID number associated with the complaint context, where present | Mapped from raw field `caller_id_number` |
| `advertiser_business_phone_number` | `STRING` | `YES` | Advertiser or business phone number present in some complaint types | Mapped from raw field `advertiser_business_phone_number` |

### I. Optional Narrative / Text Handling Fields

The current Phase 3 raw FCC source evidence does not expose a complaint
narrative field.

No narrative or free-text fields are included in the initial Silver
schema contract.

### Reviewed but Not Included in the Initial Persisted Contract

The following candidate fields were reviewed because they are common in
complaint-domain models or were explicitly raised during architecture
review, but they are not part of the initial persisted Silver contract.

| candidate_field | status | rationale |
| --- | --- | --- |
| `date_received` | `deferred_for_review` | A business-friendly alias may be appropriate later, but the current contract keeps `date_created` until Phase 4-3 formally defines the mapping semantics |
| `date_sent_to_company` | `not_in_initial_contract` | Not present in the current FCC raw source contract |
| `product` | `not_in_initial_contract` | Current source exposes `issue_type`, not a separate approved product taxonomy |
| `sub_product` | `not_in_initial_contract` | Not present in the current FCC raw source contract |
| `sub_issue` | `not_in_initial_contract` | Not present in the current FCC raw source contract |
| `submitted_via` | `deferred_for_review` | Current source supports `method`; a later approved transformation rule could decide whether `submitted_via` is a justified alias or a semantic narrowing |

## 5. Required Fields

The minimum required fields for inclusion in the Silver dataset are:

- `complaint_id`
- `source_run_id`
- `silver_processed_at_utc`
- `source_system`
- `date_created`

All other fields remain optional at the schema-contract level unless a
later approved revision explicitly elevates them to required status.

## 6. Type Decisions

### `complaint_id`

- Type: `STRING`
- Rationale:
  - the raw JSON payload already carries `id` as a string
  - string typing avoids downstream numeric formatting assumptions
  - the identifier is used as a business key, not as a measure

### Temporal Fields

- `ticket_created_utc` is typed as `TIMESTAMP` because the raw source
  presents a full UTC timestamp
- `date_created` and `issue_date` are typed as `DATE` because they are
  date-grain fields in the source and downstream trend analysis is
  naturally date-based
- `issue_time_raw` remains `STRING` because the current source values
  are not sufficiently standardized for a contract-safe time type

### Naming Decisions

- `date_created` is retained instead of renaming it to
  `date_received` in the initial contract
- `ticket_created_utc` is retained instead of renaming it to a more
  interpretive label such as `submitted_at_utc`
- the contract prefers semantic stability over aggressive business
  renaming until Phase 4-3 defines and approves any field mappings that
  would materially change the business meaning of a column

### Boolean / Flag Fields

No explicit boolean complaint-response flags are present in the current
Phase 3 FCC raw source evidence. As a result, no boolean flag columns
are included in the current Silver contract.

If future approved source revisions introduce response or dispute flags,
the preferred target contract type is `BOOLEAN`.

### Categorical / Text Fields

- dimension-like fields such as `issue_type`, `issue`, `method`,
  `city`, and `state` remain `STRING`
- text-based source columns remain nullable unless explicitly promoted
  to required status
- the contract standardizes only stable column naming, not the full
  transformation rules for values

### `zip_code`

- Type: `STRING`
- Rationale:
  - ZIP codes are identifiers, not numeric measures
  - preserving them as strings avoids dropping leading zeroes
  - source values may contain non-purely numeric content that should not
    be coerced into an integer type

### Null Handling at Contract Level

Nullability is defined at the schema level, not left to downstream tool
inference. Optional source attributes remain nullable unless the schema
contract explicitly states otherwise.

## 7. Derived / Standardized Fields

The initial Silver contract keeps derived fields intentionally narrow.

Included standardizations:

- `complaint_id` as the canonical business-key name for raw `id`
- `zip_code` as the canonical name for raw `zip`
- `type_of_call_or_message` as the canonical name for raw
  `type_of_call_or_messge`
- `source_system` as a stable lineage field

These standardizations are limited to structural cleanup and durable
canonical naming. They do not introduce new business-event semantics.

Not included in the initial contract:

- `received_year`
- `received_month`
- `received_year_month`
- complaint aging or response-duration fields

These can be added later if Phase 4 architecture review concludes that
they are necessary in Silver rather than Gold.

## 8. Primary Key and Uniqueness Contract

- Primary business key: `complaint_id`
- Final Silver expectation: `one row per complaint_id`
- Uniqueness rule: `complaint_id` must be unique in the persisted Silver dataset

This document defines uniqueness as a schema-level expectation. The
exact deduplication rule hierarchy that produces that outcome belongs to
Phase 4-3.

## 9. Nullability Contract

Nullability in this schema is explicit and intentional.

- required columns are marked `NO`
- optional columns are marked `YES`
- optional FCC source attributes remain nullable unless a later approved
  schema revision promotes them

Downstream implementations should not infer stricter nullability without
an approved contract change.

## 10. Out of Scope

This schema contract does not define:

- field-level transformation rules
- deduplication implementation logic
- data quality thresholds or pass/fail criteria
- reject or quarantine handling logic
- Gold-layer aggregates, KPIs, or dashboard fields

Those concerns belong to later Phase 4 tasks.

## 11. Open Questions / Review Notes

- Should `date_created` remain the long-term canonical complaint date
  name in Silver, or should a future approved schema revision introduce
  a business-friendly alias after transformation rules are defined?
- Should `method` remain the long-term Silver channel field name, or
  should a future approved schema revision introduce a canonical alias
  only after its business meaning is formally defined?
- Should the raw `location_1` object be decomposed into additional
  structured geography fields in a later schema revision, or remain out
  of the primary Silver contract?
- Should call-specific fields such as `caller_id_number` and
  `advertiser_business_phone_number` remain in the primary Silver table,
  or move to a narrower subtype-oriented structure if the analytics
  scope becomes more tightly telecom-call focused?
