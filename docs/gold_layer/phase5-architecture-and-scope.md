# Phase 5 Gold Layer Architecture and Scope

## 1. Purpose of Phase 5

Phase 5 defines the Gold layer for the Telecom Compliance Analytics
Platform (TCAP).

The purpose of the Gold layer is to transform the validated Phase 4
Silver dataset into analytics-facing datasets that directly support the
approved FCC complaint reporting requirements, KPI definitions, and
Power BI dashboard design established in Phase 2.

Phase 5 is the first layer in TCAP that is intentionally organized for
business reporting rather than source capture or record-level
standardization.

## 2. Architectural Role of Gold Relative to Raw and Silver

The current layered role in the repository is:

- Raw layer:
  - stores FCC source data as landed from ingestion runs
- Silver layer:
  - standardizes records
  - enforces schema
  - deduplicates to one latest valid row per `complaint_id`
  - persists validation, reject, and metadata artifacts
- Gold layer:
  - organizes Silver outputs into reporting-ready datasets and measures
    aligned to approved analytics requirements and dashboard views

Gold should consume only validated Silver outputs, not raw landing files
directly.

This preserves the current TCAP boundary:

- Raw answers "what was ingested"
- Silver answers "what is the validated canonical complaint record"
- Gold answers "what business-facing analytical view should be reported"

## 3. Phase 5 Objectives

- Define the Gold-layer role as the reporting and analytics layer above
  Silver
- Translate approved Phase 2 analytics requirements into candidate Gold
  datasets
- Define the Gold scope needed to support the approved KPI catalog
- Align candidate Gold outputs to the approved Power BI dashboard pages
- Establish design constraints for Gold without implementing pipelines,
  SQL, or semantic models
- Clarify what belongs in Gold versus what remains in Silver or later
  dashboard-only logic

## 4. In-Scope Items

Phase 5 Step 1 is limited to architecture and scope definition for the
Gold layer.

In scope:

- defining the architectural purpose of Gold
- defining Gold relative to Raw and Silver
- identifying candidate Gold datasets based on approved Phase 2
  analytics requirements
- defining how Gold should support the KPI catalog documented in Phase 2
- defining dashboard alignment principles for later Power BI work
- documenting risks, assumptions, and open design decisions for the
  first Gold implementation slice
- defining Step 1 acceptance criteria

## 5. Out-of-Scope Items

This Step 1 document does not include:

- Gold pipeline implementation
- SQL transformations
- Python transformations
- Power BI report implementation
- DAX measure implementation
- scheduling or orchestration
- alerting or anomaly-engine implementation
- visual layout assets or screenshots
- changes to Silver logic or Silver schema

## 6. Candidate Gold Datasets / Tables

The candidate Gold dataset set below is derived directly from:

- `docs/phase2-analytics-requirements.md`
- `docs/phase2-kpi-definitions.md`
- `docs/phase2-dashboard-design.md`

These are the approved candidate reporting datasets for the first Gold
design iteration. The Gold layer will use multiple fact and dimension
datasets aligned to the approved Phase 2 reporting scope. A single wide
reporting dataset is not the approved modeling approach because it would
mix grains, duplicate dimensional attributes, and weaken reconciliation
discipline.

### 6.1 Approved Fact Datasets

#### `fact_complaints_daily`

- Primary purpose:
  - support daily complaint trend reporting from the Silver canonical
    record set
- Phase 2 alignment:
  - `AR-01`
  - `AR-05`
  - `AR-06`
  - `AR-07`

#### `fact_complaints_monthly`

- Primary purpose:
  - support monthly trend reporting, month-over-month comparison, and
    executive summary views
- Phase 2 alignment:
  - `AR-01`
  - `AR-05`
  - `AR-06`
  - `AR-07`

### 6.2 Approved Dimension Datasets

#### `dim_date`

- Primary purpose:
  - provide a canonical reporting calendar aligned to the approved Gold
    date strategy

#### `dim_issue`

- Primary purpose:
  - provide issue-level reporting attributes required for issue-focused
    analysis

#### `dim_method`

- Primary purpose:
  - provide method-level reporting attributes required for service mix
    analysis

#### `dim_geography`

- Primary purpose:
  - provide reporting geography attributes with `state` as the primary
    level and `city` as a secondary level

## 7. Guiding Design Principles

- Silver-first dependency:
  - Gold consumes validated Silver outputs only
- Reporting alignment:
  - Gold datasets must map directly to approved analytics requirements
    and dashboard use cases
- Minimal duplication:
  - Gold should not replicate unnecessary record-level Silver structure
- KPI supportability:
  - Gold must support the approved KPI catalog without inventing new
    unsupported business measures
- KPI ownership:
  - KPI base logic belongs in Gold dataset design, not in Power BI-only
    ad hoc logic
- Deterministic structure:
  - Gold dataset definitions and grains must be explicit and stable
- Business-readability:
  - Gold naming should be more reporting-oriented than Silver where that
    improves clarity without changing approved semantics
- Scope control:
  - Gold should support descriptive and comparative FCC reporting only,
    consistent with Phase 2 constraints
- Traceability:
  - Gold outputs should remain attributable to their upstream
    `source_run_id` or equivalent Silver-run lineage
- Modeling approach:
  - Gold should use multiple fact and dimension datasets rather than a
    single wide reporting table

## 8. Grain Definition Principle

Every Gold dataset must declare its grain explicitly before any
implementation begins.

This is a mandatory architecture rule, not an implementation detail.
Gold datasets must not mix multiple grains within the same persisted
output.

Examples:

- `fact_complaints_daily`
  - one row per reporting date and approved Gold dimensions
- `fact_complaints_monthly`
  - one row per reporting month and approved Gold dimensions

The same rule applies to all later Gold outputs. If a dataset cannot
state its row-level grain clearly, it is not ready for implementation.

## 9. Reconciliation Contract

Gold aggregates must reconcile to the validated Silver dataset within
the same business context.

Required expectation:

- Gold totals must reconcile to Silver complaint totals for the same
  filters, dimensions, and time windows
- reconciliation must be performed using the canonical Gold reporting
  date strategy defined for this phase
- filtered Gold views must remain explainable in terms of the upstream
  Silver record population they summarize

Examples of expected reconciliation behavior:

- monthly complaint totals in `fact_complaints_monthly` must reconcile
  to Silver complaint counts grouped by the same month definition
- daily complaint totals in `fact_complaints_daily` must reconcile to
  Silver complaint counts under the same daily and dimensional filter
  context
- monthly dimensional totals in `fact_complaints_monthly` must remain
  explainable through the same issue, method, and geography filter
  context used in reporting

This contract is required so Gold remains auditable and suitable for
Power BI reporting.

## 10. Time Standardization

The canonical reporting date source for Gold is `date_created` from the
validated Silver dataset.

This decision is aligned to the approved Phase 2 analytics requirements,
KPI definitions, and dashboard design, all of which treat
`date_created` as the primary reporting-date candidate.

Supported Gold time grains for the first implementation boundary:

- daily
- monthly

Weekly aggregation is explicitly out of scope for the initial Gold
implementation boundary. It may be introduced later as a controlled
extension after the daily and monthly model is established.

Daily grain supports detailed trend inspection and future exception
analysis. Monthly grain supports executive reporting, KPI summaries, and
the approved Power BI trend views.

## 11. Physical Gold Layout

Gold storage should be analytics-first, not ingestion-run-first.

Approved layout rule:

- Gold datasets are not partitioned by `source_run_id`
- Gold datasets are partitioned by business time grain
- upstream run lineage should be preserved in metadata rather than in
  the Gold dataset path structure

Recommended physical pattern:

- `data/gold/<dataset_name>/`
  - `grain=<daily|monthly>/`
    - `year=YYYY/`
      - `month=MM/`
        - files

This layout is the approved Gold architecture direction for the initial
implementation because:

- dashboards query by business time, not by ingestion run
- it reduces fragmentation across reporting outputs
- it aligns better to BI consumption patterns
- it preserves determinism through metadata and build context rather
  than ingestion-run path partitioning

## 12. Dashboard / Reporting Alignment Approach

Gold design should align directly to the approved Power BI page design
in `docs/phase2-dashboard-design.md`.

Planned alignment approach:

- Page 1: Compliance Overview
  - supported by daily and monthly complaint trend outputs plus monthly
    category-share capable outputs
- Page 2: Issue Type and Method Analysis
  - supported by monthly fact outputs filtered by issue and method
    dimensions
- Page 3: Issue Category Analysis
  - supported by monthly fact outputs filtered by issue dimensions and
    daily fact trend outputs where needed
- Page 4: Geographic Analysis
  - supported by monthly fact outputs filtered by geography dimensions
    using `state` as the primary geographic level
- Page 5: Trend and Anomaly Monitoring
  - supported by Gold datasets that expose period-over-period and
    rolling comparison-ready structures

Phase 5 should therefore optimize for:

- Power BI-ready dataset shape
- KPI support for the approved Phase 2 catalog, with base KPI logic
  defined in Gold rather than left entirely to Power BI
- consistency of dimensions and date usage across Gold outputs

## 13. Risks and Open Design Decisions

### Risks

- Gold design depends on the continued stability of Silver field naming,
  especially `date_created`, `issue_type`, `method`, `issue`, `city`,
  `state`, and `zip_code`
- geography reporting may require careful handling because Phase 2
  already notes that `city` may need standardization review
- anomaly-oriented reporting must remain descriptive; it must not drift
  into unsupported predictive logic
- the KPI catalog assumes `date_created` remains the primary reporting
  date unless later validation changes that decision

### Open Design Decisions

- Whether some KPI logic should remain in Power BI measures only, or be
  partially materialized in Gold outputs for consistency and reuse

## 14. Acceptance Criteria for Step 1

Phase 5 Step 1 is complete only when:

- the architectural role of Gold is documented relative to Raw and
  Silver
- the purpose and objectives of Phase 5 are explicitly documented
- in-scope and out-of-scope boundaries are clear
- candidate Gold datasets are identified and traceable to approved Phase
  2 requirements and dashboard pages
- every candidate Gold dataset follows the explicit grain-definition
  principle
- the Gold modeling approach is explicitly defined as multiple fact and
  dimension datasets, not a single wide dataset
- the reconciliation contract is documented
- the canonical Gold reporting date and supported time grains are
  documented
- guiding design principles are documented
- dashboard/reporting alignment is documented without implementation
  speculation
- risks and open decisions are captured explicitly
- no implementation code, SQL, or pipelines are introduced as part of
  this step

## Assumptions Used in This Step

- Phase 2 documents remain the source of truth for analytics
  requirements, KPI definitions, and dashboard scope
- Phase 4 Silver outputs are sufficiently complete and validated to act
  as the upstream source for Gold design
- Gold remains limited to FCC-based descriptive and comparative
  analytics, consistent with the repository’s current documented scope
