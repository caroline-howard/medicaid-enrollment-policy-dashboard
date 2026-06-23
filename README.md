# Medicaid Enrollment & Eligibility Operations Analytics

## Portfolio Summary

This portfolio project uses official public Medicaid/CHIP enrollment and eligibility operations data to build a descriptive healthcare policy analytics dashboard. The project focuses on source validation, reproducible data preparation, state-level monitoring, policy-aware interpretation, and deployment-ready dashboard reporting.

The project is intentionally descriptive. It does not use beneficiary-level data, claims data, utilization data, cost outcomes, or causal inference methods.

Live dashboard: pending Plotly Cloud deployment  
GitHub repository: https://github.com/caroline-howard/medicaid-enrollment-policy-dashboard

## Project Purpose

Medicaid and CHIP enrollment changes can reflect policy rules, administrative processes, renewal activity, economic conditions, program design, and reporting practices. This project turns public aggregate data into a structured monitoring tool that helps users review:

- national Medicaid/CHIP enrollment patterns
- state-by-state enrollment variation
- applications and eligibility determinations
- Medicaid vs CHIP composition
- population-adjusted state context
- fiscal-year expenditure context
- data quality and reporting limitations

## Intended Audience And Target Roles

This project is designed for portfolio review by hiring managers and teams hiring for:

- healthcare data analyst roles
- healthcare business analyst roles
- Medicaid policy or healthcare research roles
- healthcare operations analyst roles
- public-sector data analyst roles

It demonstrates public healthcare data ingestion, source documentation, dashboard-ready table design, policy-facing interpretation, and responsible limitations language.

## Relevance For Medicaid Policy And Program Evaluation Roles

This project is especially relevant to Medicaid policy, healthcare research, and program evaluation support roles because it demonstrates how public program data can be collected, reviewed, documented, analyzed, and translated into charts, tables, and concise interpretation for policy audiences.

The workflow aligns with applied healthcare research tasks such as:

- reviewing official Medicaid/CHIP program data sources
- preparing reproducible quantitative data summaries
- creating dashboard-ready tables, charts, and written findings
- documenting data quality, missingness, and reporting caveats
- translating analytic outputs for policymakers, payers, providers, and healthcare program stakeholders
- keeping interpretation honest when data support monitoring but not causal conclusions

## Official Data Sources

Primary CMS/Data.Medicaid.gov source:

- [State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data](https://data.medicaid.gov/dataset/6165f45b-ca93-5bb5-9d06-db29c692a360/data)
- CSV extract used by the ingestion workflow: `https://download.medicaid.gov/data/pi-dataset-may-2026-release.csv`
- Grain: monthly state-level aggregate records
- Cleaned dashboard scope: all 50 states plus DC, January 2019 through February 2026

Additional context sources used in local review files and dashboard context tabs:

- U.S. Census Bureau state population estimates for population-adjusted metrics
- Medicaid.gov State Profiles context files for enrollment and eligibility threshold context
- Medicaid.gov MBES/CBES Financial Management Report files for fiscal-year expenditure context
- KFF State Health Facts FMAP/eFMAP files and Medicaid.gov CHIP program structure files retained in `data/context/`

## Main Reporting Questions

1. How has national Medicaid/CHIP enrollment changed from January 2019 through the latest available reporting month?
2. How do selected states compare with national enrollment patterns and with each other?
3. Which state-level metrics are best interpreted as raw counts, rates, shares, or fiscal-year context?
4. What eligibility operations indicators are available from the public aggregate data?
5. What can and cannot be claimed from public state-month Medicaid/CHIP reporting data?

## Dashboard Sections

The current Plotly Dash app uses two visible top-level sections.

### National Snapshot

An executive-style monitoring view for national Medicaid/CHIP enrollment. It includes:

- national KPI cards for baseline, peak, latest enrollment, and change from reference points
- selected-state vs national indexed enrollment trend
- state-level map context for enrollment change
- a policy/reporting timeline for interpreting major enrollment trend periods

### State Comparison Explorer

A state comparison and profile workflow for two selected states. It includes:

- selected-state controls and a national rank strip
- direct state-to-state comparison table
- trend-over-time comparison
- within-state profile tabs:
  - Enrollment trend
  - Eligibility context
  - Fiscal profile

The State Comparison Explorer uses state-level aggregate records only. It does not show county-level, beneficiary-level, claims, utilization, diagnosis, or cost-outcome data.

## Data Pipeline Overview

1. Source ingestion: download official CMS/Data.Medicaid.gov Medicaid/CHIP monthly aggregate data.
2. Cleaning: standardize field names, parse reporting months, standardize state names/abbreviations, and preserve key enrollment and eligibility fields.
3. Validation: check duplicate state-month rows, missingness, latest-month status, and fields with high missingness.
4. Dashboard table build: create national trend tables, state comparison tables, population-adjusted metrics, data quality summaries, and state profile context tables.
5. App rendering: load lightweight CSV outputs from `data/processed/`, `data/manual/`, `data/context/`, and `outputs/dashboard_tables/`.

## Key Repository Structure

```text
medicaid-enrollment-policy-dashboard/
├── app.py
├── Procfile
├── requirements.txt
├── assets/
│   └── styles.css
├── data/
│   ├── context/
│   ├── manual/
│   ├── processed/
│   ├── raw/
│   └── data_dictionary.md
├── docs/
│   ├── project_brief.md
│   ├── limitations.md
│   ├── source_notes.md
│   ├── policy_context.md
│   └── dashboard_user_guide.md
├── notebooks/
├── outputs/
│   ├── dashboard_tables/
│   ├── figures/
│   └── policy_summary.md
└── src/
```

## Local Run Instructions

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the Dash app locally:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:8050
```

## Plotly Cloud Deployment Notes

The app is prepared for a Plotly Cloud-style Dash deployment.

Deployment configuration:

- app entry file: `app.py`
- server object: `server`
- start command: `gunicorn app:server --workers 2 --threads 4 --timeout 120`
- Procfile command: `web: gunicorn app:server --workers 2 --threads 4 --timeout 120`

Before deploying, make sure these paths are pushed to GitHub:

- `app.py`
- `Procfile`
- `requirements.txt`
- `assets/`
- `outputs/dashboard_tables/`
- `data/processed/`
- `data/manual/`
- `data/context/`

`data/raw/` may remain outside Git. Raw source files can be re-downloaded or documented, while the lightweight processed and dashboard-ready files are needed for the hosted app.

Validation completed before deployment preparation:

- `python -m py_compile app.py`
- app import smoke test
- Gunicorn local smoke test returned HTTP 200 OK

## Screenshots

Screenshots will be added after final Plotly Cloud deployment.

- National Snapshot screenshot: pending
- State Comparison Explorer screenshot: pending

## Limitations And Guardrails

- Public aggregate state-month data cannot describe individual beneficiaries.
- The dashboard does not include claims, utilization, cost outcomes, diagnoses, provider access, managed care plan performance, or county-level variation.
- Applications and determinations are descriptive eligibility operations indicators. They are not approval rates, backlog measures, timeliness measures, or performance scores.
- Population-adjusted metrics provide comparison context but should not be called usage rates.
- Fiscal profile values are fiscal-year MBES/CBES financial reporting values, not monthly enrollment values.
- Latest-month data may be preliminary, and reporting practices vary by state.
- The project supports monitoring and interpretation. It does not estimate causal policy effects.

See [docs/limitations.md](docs/limitations.md) for more detail.

## Resume-Ready Language

General:

- Built a public-data Medicaid/CHIP analytics dashboard using CMS enrollment and eligibility operations data, with reproducible data processing, dashboard-ready tables, and deployment-ready Plotly Dash reporting.

Medicaid policy / healthcare analyst version:

- Developed a Medicaid/CHIP policy monitoring dashboard using official CMS state-month data to compare enrollment trends, eligibility operations indicators, state variation, and public reporting limitations.

Public-sector / business analyst version:

- Created a state comparison dashboard and documentation workflow that translates public Medicaid/CHIP administrative data into clear monitoring views, data quality notes, and decision-ready summaries.

Healthcare policy and research role options:

- Analyzed official public Medicaid/CHIP program data to produce state comparison tables, dashboard visuals, source notes, and limitations language for policy-facing healthcare research communication.
- Built a reproducible Medicaid/CHIP monitoring workflow in Python and Plotly Dash, including data ingestion, validation, derived metrics, charts, and written interpretation for program evaluation support.
- Prepared documentation and dashboard outputs that synthesize Medicaid enrollment, eligibility operations, fiscal context, and data quality findings for healthcare policy and public-sector audiences.

## Current Status

Project scaffold, ingestion, validation, dashboard-ready table builds, documentation, and Plotly Dash app development are complete for the current portfolio version. The remaining manual steps are deployment, screenshot capture, and live URL insertion.

## Remaining Manual Steps

1. Push the required deployment folders and files to GitHub.
2. Deploy the app on Plotly Cloud.
3. Add the final live dashboard URL to this README.
4. Capture and add screenshots after deployment.
5. Optionally convert `docs/project_brief.md` into a short PDF portfolio brief.
