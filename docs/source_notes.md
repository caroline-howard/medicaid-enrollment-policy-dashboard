# Source Notes

## Selected Source

This project uses the official CMS/Data.Medicaid.gov dataset:

- Dataset name: State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data
- Publisher: CMS/Data.Medicaid.gov
- Dataset page: https://data.medicaid.gov/dataset/6165f45b-ca93-5bb5-9d06-db29c692a360/data
- CSV download used by the ingestion script: https://download.medicaid.gov/data/pi-dataset-may-2026-release.csv
- Data dictionary endpoint: https://data.medicaid.gov/api/1/metastore/schemas/data-dictionary/items/7d80cfd8-3266-4c55-8436-948b7c55b9dd
- Access date: 2026-06-15
- Source metadata modified date: 2026-05-29
- Reporting frequency: monthly
- Access method: public HTTPS download from CMS

The raw source CSV is saved locally in `data/raw/` when the ingestion script runs, but raw files are excluded from Git. The source URL above allows the raw file to be downloaded again.

## What The Dataset Measures

The dataset contains public aggregate state-level Medicaid and CHIP performance indicator data. It includes monthly measures related to:

- Medicaid and CHIP enrollment
- Medicaid enrollment
- CHIP enrollment
- child enrollment
- adult Medicaid enrollment where available
- applications submitted
- eligibility determinations at application
- application processing timing categories
- selected call center indicators
- preliminary/updated and final-report status fields

The cleaned project dataset keeps all 50 states plus DC, beginning in January 2019 and running through the most recent month available in this source extract, February 2026.

## Processed Outputs

The ingestion and cleaning scripts create:

- `data/processed/medicaid_enrollment_clean.csv`: full cleaned 2019-present all-state/DC state-month dataset.
- `data/processed/medicaid_state_month_summary.csv`: compact state-month summary for analysis.
- `data/processed/medicaid_sample_for_dashboard.csv`: smaller recent-month sample for quick testing and dashboard development.
- `data/processed/data_quality_summary.csv`: dataset, duplicate, field missingness, monthly completeness, and state-month missingness checks.

## Source Validation Summary

- Raw source rows: 10,710
- Cleaned state-month rows: 4,386
- Date range after filtering: January 2019 through February 2026
- States/DC included: 51
- Reporting months included: 86
- Duplicate cleaned state-month records: 0
- Source duplicate state-month records before cleaning: 4,335, due to preliminary and updated/final reporting records
- Final/updated records in cleaned data: 4,335
- Preliminary records in cleaned data: 51, all in the latest available reporting month

## What The Project Can Claim

This project can support descriptive analysis of public Medicaid/CHIP enrollment and eligibility operations trends. It can be used for:

- state-month trend analysis
- state comparisons
- enrollment reporting
- application and eligibility determination monitoring
- data quality review
- policy-facing interpretation of public aggregate reporting patterns

## What The Project Cannot Claim

This project cannot claim:

- beneficiary-level outcomes
- claims-level utilization, cost, or diagnosis patterns
- causal effects of policy changes
- complete operational performance for every state and month
- eligibility or enrollment experiences for specific individuals

Any causal analysis, event study, or forecast would require a separate design and should not be inferred from this descriptive source-validation step.

## Reporting Lag And Update Limitations

CMS publishes monthly state-reported data that may include preliminary and updated/final records. The cleaned dataset prefers final/updated records when both are available. The latest reporting month in this extract remains preliminary for all states/DC and should be treated cautiously in analysis and dashboard interpretation.

## State Reporting Variation

States may vary in reporting practices, completeness, operational definitions, and timing. Some fields may be more consistently reported than others. Dashboard labels and policy notes should clearly distinguish between enrollment measures, application/determination measures, processing-time fields, and call center fields.

## Missingness And Completeness Concerns

The core enrollment, application, and determination fields needed for trend analysis are available for the cleaned 2019-present all-state/DC panel. Several operational fields have substantial missingness:

- adult Medicaid enrollment
- call center volume, wait time, and abandonment rate
- application processing timing categories

These fields can still support selected exploratory analysis, but they should be labeled carefully and should not be interpreted as complete all-state operational performance measures without further review.

## Public Aggregate Data Limitations

Public aggregate data is useful for transparent reporting and policy monitoring, but it does not include individual-level demographic, eligibility, claims, or utilization detail. The dataset should be used for descriptive monitoring and reporting, not for individual-level inference or unsupported causal claims.
