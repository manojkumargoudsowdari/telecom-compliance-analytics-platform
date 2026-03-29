# Phase 6 Power BI Import Readiness

## 1. Purpose

This document records the Phase 6 implementation-readiness checks for
manual Power BI Desktop import of the approved Gold fact outputs.

It is limited to source inspection and import-readiness guidance. It
does not change Gold logic, reshape data, or define Power BI code.

## 2. Confirmed Source Paths

Approved Gold fact roots for Power BI import:

- `data/gold/fact_complaints_daily/`
- `data/gold/fact_complaints_monthly/`

Expected Power Query fact query names:

- `fact_complaints_daily`
- `fact_complaints_monthly`

## 3. Folder and Partition Inspection Results

### `fact_complaints_daily`

- root path:
  - `data/gold/fact_complaints_daily/`
- partition pattern:
  - `grain=daily/year=YYYY/month=MM/fact_complaints_daily.json`
- first partition found:
  - `grain=daily/year=2014/month=10/fact_complaints_daily.json`
- last partition found:
  - `grain=daily/year=2026/month=03/fact_complaints_daily.json`
- file count:
  - `138`

### `fact_complaints_monthly`

- root path:
  - `data/gold/fact_complaints_monthly/`
- partition pattern:
  - `grain=monthly/year=YYYY/month=MM/fact_complaints_monthly.json`
- first partition found:
  - `grain=monthly/year=2014/month=10/fact_complaints_monthly.json`
- last partition found:
  - `grain=monthly/year=2026/month=03/fact_complaints_monthly.json`
- file count:
  - `138`

## 4. Structural Consistency Results

Confirmed inspection outcomes:

- partition path consistency:
  - `PASS`
- file naming consistency:
  - `PASS`
- empty-file check:
  - `PASS`
- malformed JSON check:
  - `PASS`
- structural schema consistency across sampled partitions:
  - `PASS`

Observed JSON array shapes:

- daily fact file keys:
  - `date_key`
  - `issue_key`
  - `method_key`
  - `geography_key`
  - `complaint_count`
- monthly fact file keys:
  - `month_key`
  - `issue_key`
  - `method_key`
  - `geography_key`
  - `complaint_count`
  - `complaint_growth_rate`
  - `rolling_average_complaint_count`

## 5. Import Risks and Caveats

The Gold sources appear import-ready for Power BI, but the following
folder-based JSON caveats should be watched during import:

- each partition file is a pretty-printed JSON array, not JSON Lines
- folder import will load many partition files and then require a
  transform step to expand each JSON array into rows
- Power Query may auto-generate helper queries and sample-file logic;
  those should be reviewed carefully rather than accepted blindly
- the folder path includes partition metadata (`grain=...`, `year=...`,
  `month=...`); these path tokens may appear as file attributes in Power
  Query and should not be confused with business columns
- daily and monthly facts must remain separate queries
- no attempt should be made to merge daily and monthly facts into one
  import table
- `issue_key`, `method_key`, and `geography_key` are persisted keys, not
  presentation-ready dimension tables

## 6. Recommended Import Approach

Recommended Power BI import approach:

- use Power Query folder import from each fact root separately
- build the transform steps first
- expand the JSON arrays into rows
- promote the final fact query names to:
  - `fact_complaints_daily`
  - `fact_complaints_monthly`
- keep helper queries separate from final fact queries
- validate row counts and column names before starting semantic-model
  work

This is the approved starting point before manual Phase 6 Power BI model
implementation.
