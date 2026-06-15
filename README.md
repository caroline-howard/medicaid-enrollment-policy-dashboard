# Medicaid Enrollment Policy Dashboard

## About

A healthcare policy analytics portfolio project focused on Medicaid/CHIP enrollment, eligibility operations, data quality, and policy-facing dashboard reporting using public CMS data.

## Project Summary

This repository will support a healthcare policy analytics portfolio project focused on public Medicaid and CHIP enrollment and eligibility operations data. The final project will combine source validation, data cleaning, policy context, and dashboard-ready outputs for analysis of Medicaid enrollment trends and operational indicators.

This project emphasizes not only code, but also reproducible documentation, data quality checks, and policy-facing interpretation for healthcare analytics and Medicaid program reporting.

Current status: Project scaffold created; data ingestion pending.

## Why Medicaid Enrollment And Eligibility Operations Matter

Medicaid and CHIP enrollment data helps analysts, policy teams, and public-sector decision makers understand how coverage access changes over time. Eligibility operations measures can provide important context about application processing, renewals, procedural outcomes, and administrative workload. Together, these data can support better reporting, policy interpretation, and operational monitoring.

## Target Roles

This project is designed to support portfolio evidence for:

- Healthcare data analyst roles
- Healthcare business analyst roles
- Medicaid policy research roles
- Healthcare operations analytics roles
- Public-sector data and reporting roles

## Planned Data Sources

Planned public data sources may include:

- [Data.Medicaid.gov](https://data.medicaid.gov/) Medicaid and CHIP open data
- [State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data](https://data.medicaid.gov/dataset/6165f45b-ca93-5bb5-9d06-db29c692a360/data)
- [Medicaid and CHIP Eligibility Operations and Enrollment Snapshot Data](https://data.medicaid.gov/medicaid-chip-eligibility-enrollment-snapshot-data)
- [Medicaid.gov Medicaid and CHIP Enrollment Data](https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-chip-enrollment-data)
- Supporting policy documentation from CMS, MACPAC, KFF, or state Medicaid agencies

No data has been ingested yet.

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

1. Identify and document exact public data sources.
2. Download raw source files into `data/raw/`.
3. Validate source files, reporting periods, and field definitions.
4. Update `data/data_dictionary.md` with confirmed source fields.
5. Build ingestion and cleaning logic in `src/`.
6. Create dashboard-ready tables in `outputs/dashboard_tables/`.
7. Build the dashboard after validated data outputs are available.
