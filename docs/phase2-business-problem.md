# Phase 2 Business Problem Statement

## Document Control

- Jira Ticket ID: `TCAP-3`
- Git Commit Link: `<add commit URL after commit>`
- Version: `0.2-draft`
- Date: `2026-03-05`

## Purpose

Define the business problem, stakeholder decisions, and realistic analytical scope for a telecom compliance analytics reporting workflow based on FCC consumer complaint records.

## Business Context

This portfolio project is framed as an internal analytics initiative for a telecom compliance and reporting team. The objective is to use publicly available FCC consumer complaint data as an external signal to monitor complaint patterns, identify emerging risk themes, and translate complaint activity into reporting that leadership can review in recurring dashboards and ad hoc analysis.

The target analyst role emphasizes four practical outcomes:

- analyzing compliance-related data
- identifying trends, patterns, and anomalies
- building recurring and ad hoc reporting in Power BI
- translating complex complaint activity into simple leadership narratives

The FCC dataset does not provide internal operational measures such as customer counts, service-level targets, case-resolution workflow, or revenue impact. As a result, the Phase 2 business framing must stay anchored to what the FCC records can actually support: complaint timing, issue mix, service method, and geography.

## Target Users / Stakeholders

- Compliance leadership reviewing external complaint trends and issue hotspots
- Regulatory affairs teams monitoring complaint patterns that may require escalation or narrative context
- Reporting and analytics teams preparing recurring dashboards and ad hoc summaries
- Operational leaders who need high-level visibility into issue concentrations by complaint category, form type, and geography

## Decision-Making Scenarios

- Monthly compliance review:
  - Determine whether complaint activity is stable, increasing, or concentrated in new issue areas.
- Quarterly issue review:
  - Identify which complaint topics are growing fast enough to justify deeper investigation.
- Geographic monitoring:
  - Review whether complaint concentrations in specific states or cities suggest localized customer-impact or regulatory concerns.
- Executive dashboard preparation:
  - Convert complaint volumes and issue mix into a small set of leadership-facing indicators.
- Ad hoc pattern analysis:
  - Respond to leadership questions about spikes in complaint categories, issue types, or service methods.

## Core Business Questions

1. Are complaint volumes increasing, decreasing, or remaining stable over time based on `date_created`?
2. Which complaint forms or service areas, such as `issue_type` and `method`, generate the highest complaint volume?
3. Which issue categories in `issue` represent the largest share of total complaint activity?
4. Which states or cities contribute the highest complaint counts, and are those patterns stable over time?
5. Are there visible spikes or unusual shifts in complaint activity by issue, issue type, or geography that warrant management attention?
6. Which complaint categories appear to be persistent versus event-driven when viewed across time?
7. What concise narrative can be given to leadership about complaint concentration, trend direction, and the most prominent risk themes in the FCC data?

## What Regulatory Risk Means in This Project

In this project, regulatory risk does not mean a confirmed compliance violation. It means an external complaint signal that may indicate:

- rising customer dissatisfaction in a complaint category
- recurring complaint themes that could attract regulatory scrutiny
- geographic concentration of complaints that merits review
- sustained growth in specific issue types that leadership should monitor

The FCC itself states that the published complaint records are informal complaints and that the agency does not verify the facts alleged in those complaints. For this reason, the analytics output should be framed as an early-warning monitoring view, not a finding of non-compliance.

## Analytical Scope Supported by FCC Data

The current FCC fields support the following realistic Phase 2 analytics scope:

- complaint volume trends using `date_created` or `ticket_created`
- issue-type distribution using `issue_type`
- service-method analysis using `method`
- complaint issue concentration using `issue`
- geographic distribution using `city`, `state`, and `zip`
- high-level exploratory anomaly detection on counts over time or by dimension
- leadership-oriented reporting that summarizes trend direction, top issues, and complaint hotspots

## Analytical Scope Not Supported by FCC Data

The current FCC source does not support the following without additional datasets:

- carrier-level benchmarking where a carrier/company field is required
- timely response or SLA reporting
- operational case-resolution performance
- internal call-center or customer-account linkage
- complaint rates normalized by subscriber base
- financial or revenue impact analysis

These gaps should remain out of scope unless a later phase introduces additional public or internal data sources.

## Assumptions

- FCC complaint records are being used as an external monitoring dataset, not as an authoritative internal compliance ledger.
- Phase 2 is focused on reporting design and analytical framing, not model deployment or operational ingestion.
- The canonical date for trend reporting is still to be validated between `date_created` and `ticket_created`.
- The business framing should avoid claims that require internal telecom operational data.
- Dashboard outputs should be leadership-friendly and explain what is changing, where it is changing, and why it may matter.

## Source Inputs

- [phase2-data-understanding.md](./phase2-data-understanding.md)
- [phase2-data-dictionary.md](./phase2-data-dictionary.md)
- [fcc_dataset_exploration.ipynb](/d:/Work/Code/telecom-compliance-analytics-platform/notebooks/fcc_dataset_exploration.ipynb)

## Definition of Done for this Document

- The business problem is aligned to a telecom compliance analytics reporting use case.
- Stakeholders and decision scenarios are clearly documented.
- Core business questions are supportable by the FCC fields already documented in Phase 2.
- Unsupported analytics use cases are explicitly called out.
- The document avoids claims of access to internal telecom operational data.
