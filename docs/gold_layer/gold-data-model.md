# Gold Data Model

## 1. Purpose

This document defines the Gold layer data model for the Telecom
Compliance Analytics Platform (TCAP).

It translates the approved Gold architecture and KPI catalog into a
deterministic fact-and-dimension model that supports the approved Phase
2 reporting requirements and Power BI dashboard design.

This document is limited to logical Gold dataset design. It does not
define code, SQL, pipelines, storage optimization, or Power BI semantic
configuration.

## 2. Dataset Inventory

### Fact Tables

- `fact_complaints_daily`
- `fact_complaints_monthly`

### Dimension Tables

- `dim_date`
- `dim_issue`
- `dim_method`
- `dim_geography`

## 3. Fact Tables

### 3.1 `fact_complaints_daily`

- Grain:
  - one row per `date_key`, `issue_key`, `method_key`, and
    `geography_key`
- Purpose:
  - provide the lowest approved Gold reporting grain for complaint
    volume and daily trend analysis
- Included KPIs:
  - `complaint_count`
  - base inputs for `period_over_period_change`
- Supported Dimensions:
  - date
  - issue
  - method
  - geography
- Non-Additive Handling Notes:
  - derived KPIs are not stored as additive measures in this fact
  - non-additive KPIs must be recalculated from the underlying daily
    complaint counts

### 3.2 `fact_complaints_monthly`

- Grain:
  - one row per `month_key`, `issue_key`, `method_key`, and
    `geography_key`
- Purpose:
  - support monthly trend reporting, executive reporting, and stable
    monthly KPI computation across all approved category dimensions
- Included KPIs:
  - `complaint_count`
  - `complaint_growth_rate`
  - `category_share`
  - `rolling_average_complaint_count`
- Supported Dimensions:
  - date
  - issue
  - method
  - geography
- Non-Additive Handling Notes:
  - `complaint_growth_rate` and `rolling_average_complaint_count` are
    non-additive and must be computed from monthly complaint totals
  - `category_share` is non-additive and must be evaluated within the
    selected monthly category context
  - in the first Gold implementation, `category_share` is not persisted
    as a separate physical column; it remains a Gold-defined KPI derived
    from monthly `complaint_count` in reporting or query consumption
  - no mixed daily and monthly rows are allowed in this dataset

## 4. Dimension Tables

### 4.1 `dim_date`

- Key:
  - `date_key`
- Source Fields:
  - `date_created`
- Purpose:
  - provide the canonical Gold reporting calendar for daily and monthly
    reporting
- Null / Unknown Handling:
  - no null `date_key` rows are allowed in Gold facts
  - unknown date values are not expected because `date_created` is
    required in Silver

### 4.2 `dim_issue`

- Key:
  - `issue_key`
- Source Fields:
  - `issue_type`
  - `issue`
- Purpose:
  - provide issue-category reporting attributes and hierarchy context
- Null / Unknown Handling:
  - if `issue` or `issue_type` is null in the upstream Silver record,
    the fact row must use a deterministic unknown-member issue key

### 4.3 `dim_method`

- Key:
  - `method_key`
- Source Fields:
  - `method`
- Purpose:
  - provide method-level reporting attributes for complaint mix analysis
- Null / Unknown Handling:
  - null methods must map to a deterministic unknown-member method key

### 4.4 `dim_geography`

- Key:
  - `geography_key`
- Source Fields:
  - `state`
  - `city`
  - `zip_code`
- Purpose:
  - provide reporting geography attributes with `state` as the primary
    level
- Null / Unknown Handling:
  - null geographic attributes must map to a deterministic
    unknown-member geography key
  - `state` remains the primary analysis level even when lower-level
    values are null

## 5. KPI-to-Fact Mapping

| KPI | Fact Table | Mapping Rule |
| --- | --- | --- |
| `complaint_count` | `fact_complaints_daily` | canonical base fact for complaint counting across the approved Gold dimensions and daily grain |
| `complaint_growth_rate` | `fact_complaints_monthly` | computed only from monthly complaint totals |
| `category_share` for all approved categories | `fact_complaints_monthly` | Gold-defined KPI derived from monthly `complaint_count` by applying the selected category axis (`issue`, `method`, or `geography`); not persisted as a separate physical column in the first implementation |
| `period_over_period_change` | `fact_complaints_daily` | computed from daily complaint totals and rolled to monthly when needed |
| `rolling_average_complaint_count` | `fact_complaints_monthly` | computed only from monthly complaint totals with a fixed rolling window per dataset |

No KPI is assigned to multiple inconsistent fact grains.

## 6. Relationship Model

### Fact to Dimension Relationships

| Fact Table | Dimension Table | Join Key | Cardinality |
| --- | --- | --- | --- |
| `fact_complaints_daily` | `dim_date` | `date_key` | many-to-one |
| `fact_complaints_daily` | `dim_issue` | `issue_key` | many-to-one |
| `fact_complaints_daily` | `dim_method` | `method_key` | many-to-one |
| `fact_complaints_daily` | `dim_geography` | `geography_key` | many-to-one |
| `fact_complaints_monthly` | `dim_date` | `month_key` to monthly date member | many-to-one |
| `fact_complaints_monthly` | `dim_issue` | `issue_key` | many-to-one |
| `fact_complaints_monthly` | `dim_method` | `method_key` | many-to-one |
| `fact_complaints_monthly` | `dim_geography` | `geography_key` | many-to-one |

### Relationship Summary

- all facts use conformed dimensions
- all fact-to-dimension joins are many-to-one
- no many-to-many relationships are approved in the Gold model
- date joins are standardized through `dim_date`
- only two Gold facts are approved in the simplified model:
  - one daily fact
  - one monthly fact

## 7. Grain Enforcement Rules

- every fact table must enforce one explicit grain only
- no fact table may contain mixed daily and monthly rows
- dimensions must remain conformed and reusable across facts
- rollups for non-additive KPIs must be recomputed from the correct fact
  grain rather than summed from lower-level KPI values

## 8. Design Decisions

- multiple fact tables are used because the approved Gold architecture
  rejects a single wide reporting dataset
- daily and monthly reporting needs are separated to avoid mixed-grain
  time modeling
- the unified monthly fact replaces category-specific facts because all
  approved category-share use cases can be supported through the same
  monthly grain with conformed dimensions
- category-specific analysis should be driven by dimensional filtering
  and grouping, not by creating separate reporting facts for each
  category axis
- dimensions are conformed so dashboard filters can behave consistently
  across Gold datasets
- non-additive KPI logic is tied to specific fact grains to prevent
  incorrect rollup behavior

## 9. Acceptance Criteria

- every fact table has an explicit grain
- every KPI is mapped to one clear fact table
- no KPI is implemented across multiple inconsistent grains
- dimension usage is consistent across datasets
- the model supports the approved Phase 2 dashboard query patterns
- there is no ambiguity in grain or fact-to-dimension relationships
- no implementation details, SQL, or orchestration logic are included
