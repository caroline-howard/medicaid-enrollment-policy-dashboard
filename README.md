# Medicaid Enrollment Policy Dashboard

## About

A healthcare policy analytics portfolio project focused on Medicaid/CHIP enrollment, eligibility operations, data quality, and policy-facing dashboard reporting using public CMS data.

## Project Summary

This repository will support a healthcare policy analytics portfolio project focused on public Medicaid and CHIP enrollment and eligibility operations data. The final project will combine source validation, data cleaning, policy context, and dashboard-ready outputs for analysis of Medicaid enrollment trends and operational indicators.

This project emphasizes not only code, but also reproducible documentation, data quality checks, and policy-facing interpretation for healthcare analytics and Medicaid program reporting.

Current status: Exploratory analysis and dashboard-ready table creation complete; Plotly Dash app development pending.

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

## EDA Status

Exploratory analysis is complete for the first dashboard version. The EDA phase created national enrollment trends, state comparison summaries, eligibility operations summaries, data quality summaries, dashboard notes, and static figures for documentation.

Key descriptive findings:

- National Medicaid/CHIP enrollment rose from early 2020 to an April 2023 peak, then declined through the latest available reporting month.
- February 2026 is the latest available month and is preliminary for all 50 states plus DC.
- Applications and eligibility determinations support descriptive operations analysis, but they should not be treated as complete performance metrics.
- Adult enrollment, call center, and processing-time fields have high missingness and should be used cautiously.

## Planned Dashboard Sections

The dashboard is planned to include:

- National enrollment overview
- State-level enrollment comparisons
- Medicaid and CHIP trend views
- Eligibility operations indicators
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

## Dashboard-Ready Tables Created

- `outputs/dashboard_tables/kpi_summary.csv`
- `outputs/dashboard_tables/national_enrollment_trend.csv`
- `outputs/dashboard_tables/national_applications_determinations_trend.csv`
- `outputs/dashboard_tables/state_latest_snapshot.csv`
- `outputs/dashboard_tables/state_enrollment_change.csv`
- `outputs/dashboard_tables/state_eligibility_operations_summary.csv`
- `outputs/dashboard_tables/state_map_metrics.csv`
- `outputs/dashboard_tables/data_quality_by_field.csv`
- `outputs/dashboard_tables/data_quality_by_state.csv`
- `outputs/dashboard_tables/data_quality_by_month.csv`
- `outputs/dashboard_tables/dashboard_notes.csv`

The `state_map_metrics.csv` table provides one row per state/DC for the future State Map Explorer choropleth and selected state profile cards.

## What This Project Demonstrates

- Reproducible public healthcare data ingestion from official CMS sources
- Source validation and data dictionary documentation
- Medicaid/CHIP enrollment trend analysis
- Eligibility operations reporting using applications and determinations
- State-by-state comparison and dashboard table preparation
- Data quality, missingness, and preliminary/final reporting checks
- Policy-facing interpretation without unsupported causal claims

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
│   ├── 01_data_ingestion_and_source_validation.ipynb
│   └── 02_eda_and_dashboard_tables.ipynb
├── src/
│   ├── load_data.py
│   ├── clean_medicaid_data.py
│   ├── eda_medicaid.py
│   └── build_dashboard_tables.py
├── outputs/
│   ├── dashboard_tables/
│   └── figures/
└── docs/
    ├── source_notes.md
    ├── project_brief.md
    ├── project_tasks.md
    ├── data_viability_and_next_steps.md
    ├── eda_findings.md
    └── limitations.md
```

## Next Steps

1. Build the Plotly Dash app using the dashboard-ready tables in `outputs/dashboard_tables/`.
2. Add national overview, state comparison, eligibility operations, data quality, and policy interpretation sections.
3. Include visible caution language for preliminary latest-month data and high-missingness fields.
4. Add dashboard screenshots to the README after the app is built.
