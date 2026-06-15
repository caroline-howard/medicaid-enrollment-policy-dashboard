# Medicaid Enrollment Policy Dashboard

## About

A healthcare policy analytics portfolio project focused on Medicaid/CHIP enrollment, eligibility operations, data quality, and policy-facing dashboard reporting using public CMS data.

## Project Summary

This repository will support a healthcare policy analytics portfolio project focused on public Medicaid and CHIP enrollment and eligibility operations data. The final project will combine source validation, data cleaning, policy context, and dashboard-ready outputs for analysis of Medicaid enrollment trends and operational indicators.

This project emphasizes not only code, but also reproducible documentation, data quality checks, and policy-facing interpretation for healthcare analytics and Medicaid program reporting.

Current status: Data ingestion and source validation complete; exploratory analysis pending.

## Why Medicaid Enrollment And Eligibility Operations Matter

Medicaid and CHIP enrollment data helps analysts, policy teams, and public-sector decision makers understand how coverage access changes over time. Eligibility operations measures can provide important context about application processing, renewals, procedural outcomes, and administrative workload. Together, these data can support better reporting, policy interpretation, and operational monitoring.

## Target Roles

This project is designed to support portfolio evidence for:

- Healthcare data analyst roles
- Healthcare business analyst roles
- Medicaid policy research roles
- Healthcare operations analytics roles
- Public-sector data and reporting roles

## Selected Data Source

This project uses the official CMS/Data.Medicaid.gov dataset:

- [State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data](https://data.medicaid.gov/dataset/6165f45b-ca93-5bb5-9d06-db29c692a360/data)
- CSV download used by the ingestion script: `https://download.medicaid.gov/data/pi-dataset-may-2026-release.csv`
- Reporting grain: monthly state-level aggregate data
- Scope after cleaning: all 50 states plus DC, January 2019 through February 2026

The raw CMS CSV is downloaded to `data/raw/`, which is excluded from Git. Processed, lightweight CSV outputs are saved in `data/processed/`.

## Ingestion Status

Completed source validation and processing:

- Raw source rows: 10,710
- Cleaned state-month rows: 4,386
- States/DC included: 51
- Reporting months included: 86
- Cleaned duplicate state-month records: 0
- Latest available month in this source extract: February 2026

## Available Fields

The processed data preserves:

- state and reporting month fields
- preliminary/updated and final-report status fields
- Medicaid enrollment
- CHIP enrollment
- total Medicaid/CHIP enrollment
- child enrollment
- adult Medicaid enrollment where available
- applications submitted
- Medicaid and CHIP eligibility determinations
- application processing timing fields where available
- selected call center fields where available

Renewals/redeterminations and pending applications are not preserved because they are not available as dedicated fields in the selected source extract.

## Planned Dashboard Sections

The dashboard is planned to include:

- National enrollment overview
- State-level enrollment comparisons
- Medicaid and CHIP trend views
- Eligibility operations and renewal indicators
- Reporting quality and missingness notes
- Policy interpretation notes and limitations

## Planned Analytics Outputs

Planned outputs include:

- Cleaned dashboard tables
- Source validation summaries
- Data dictionary updates
- Trend charts
- State comparison figures
- Written source notes and limitations

Version 1 will focus on policy analytics, data quality, and dashboard reporting. Causal inference, event studies, and forecasting are outside the initial scaffold and may be considered only after validated dashboard-ready data exists.

## Processed Outputs Created

- `data/processed/medicaid_enrollment_clean.csv`
- `data/processed/medicaid_state_month_summary.csv`
- `data/processed/medicaid_sample_for_dashboard.csv`
- `data/processed/data_quality_summary.csv`

## Repository Structure

```text
medicaid-enrollment-policy-dashboard/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/
│   ├── processed/
│   └── data_dictionary.md
├── notebooks/
│   └── 01_data_ingestion_and_source_validation.ipynb
├── src/
│   ├── load_data.py
│   └── clean_medicaid_data.py
├── outputs/
│   ├── dashboard_tables/
│   └── figures/
└── docs/
    ├── source_notes.md
    ├── project_brief.md
    ├── project_tasks.md
    └── limitations.md
```

## Next Steps

1. Complete exploratory analysis of enrollment and eligibility operations trends.
2. Create dashboard-ready summary tables in `outputs/dashboard_tables/`.
3. Draft policy-facing interpretation notes and data quality caveats.
4. Build the Plotly Dash dashboard after EDA and dashboard tables are complete.
