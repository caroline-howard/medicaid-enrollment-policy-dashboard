# Medicaid Enrollment Policy Dashboard

## About

A healthcare policy analytics project that reviews official Medicaid/CHIP enrollment and eligibility operations data, validates source quality, and builds a descriptive monitoring workflow for state-level policy and operations context.

## Project Summary

This repository reviews official CMS/Data.Medicaid.gov Medicaid and CHIP enrollment and eligibility operations data to monitor state-level enrollment trends, application and determination patterns, population-adjusted context, data quality issues, and changes that may warrant further policy or operations review.

The project emphasizes source review, reproducible documentation, data validation, diagnostic monitoring indicators, and policy-facing interpretation. It is descriptive and monitoring-focused; it does not make causal claims.

Current status: Diagnostic monitoring workflow, population-adjusted state context, dashboard-ready tables, and Plotly Dash Version 1 are complete.

## Why Medicaid Enrollment And Eligibility Operations Matter

Medicaid and CHIP enrollment data helps analysts, policy teams, and public-sector decision makers understand how coverage access changes over time. Eligibility operations measures can provide important context about application processing, renewals, procedural outcomes, and administrative workload. Together, these data can support better reporting, policy interpretation, and operational monitoring.

## Intended Use

This project is designed for source-aware public reporting and exploratory monitoring. It can help analysts, policy teams, and operations stakeholders review:

- state-level Medicaid/CHIP enrollment shifts
- Medicaid vs CHIP enrollment context
- applications and eligibility determinations activity
- population-adjusted state comparisons
- data quality and reporting caveats
- neutral review flags that may warrant follow-up review

## Selected Data Source

This project uses the official CMS/Data.Medicaid.gov dataset:

- [State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data](https://data.medicaid.gov/dataset/6165f45b-ca93-5bb5-9d06-db29c692a360/data)
- CSV download used by the ingestion script: `https://download.medicaid.gov/data/pi-dataset-may-2026-release.csv`
- Reporting grain: monthly state-level aggregate data
- Scope after cleaning: all 50 states plus DC, January 2019 through February 2026

The dashboard also uses an official U.S. Census Bureau state population denominator source:

- [Annual Estimates of the Resident Population: April 1, 2020 to July 1, 2024 (NST-EST2024-POP)](https://www2.census.gov/programs-surveys/popest/tables/2020-2024/state/totals/NST-EST2024-POP.xlsx)
- Latest denominator year used in Version 1: 2024
- Population-adjusted measures are descriptive context only and should not be described as healthcare utilization or usage rates.

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

## Dashboard Sections

The redesigned Plotly Dash app includes story-driven tabs:

- National Snapshot
- State Map Explorer
- Medicaid vs CHIP Drivers
- Eligibility Operations
- Monitoring Flags
- Data Quality Review
- Methods & Limits

The app uses a custom light-gray, white-card, navy/teal/amber visual identity designed for public healthcare policy analytics. It includes concise global caveats, question-based tab headers, interactive Plotly time-series explorers with range sliders and range selector buttons, and a professional footer emphasizing descriptive monitoring only.

## Planned Analytics Outputs

Planned outputs include:

- Cleaned dashboard tables
- Source validation summaries
- Data dictionary updates
- Trend charts
- State comparison figures
- Diagnostic monitoring indicators
- Neutral state/month review flags
- Written source notes and limitations

Version 1 will focus on policy analytics, data quality, and dashboard reporting. Causal inference, event studies, and forecasting are outside the initial scaffold and may be considered only after validated dashboard-ready data exists.

## What This Project Helps Monitor

- Enrollment shifts across states
- Medicaid vs CHIP patterns
- Applications and determinations activity
- Application-Determination Balance as a descriptive eligibility operations diagnostic
- Population-adjusted enrollment context
- State/month review flags
- Data quality and reporting caveats

Review flags are monitoring prompts, not problem labels or performance scores.

## Policy Context

This dashboard is designed for descriptive monitoring and policy context, not causal policy evaluation. See [docs/policy_context.md](docs/policy_context.md) for plain-language context on Medicaid/CHIP state variation, MAGI eligibility, Medicaid expansion, COVID continuous enrollment and unwinding, applications and determinations, population denominators, and dataset limitations.

## Processed Outputs Created

- `data/processed/medicaid_enrollment_clean.csv`
- `data/processed/medicaid_state_month_summary.csv`
- `data/processed/medicaid_sample_for_dashboard.csv`
- `data/processed/data_quality_summary.csv`
- `data/processed/state_population_denominators.csv`

## Dashboard-Ready Tables Created

- `outputs/dashboard_tables/kpi_summary.csv`
- `outputs/dashboard_tables/national_enrollment_trend.csv`
- `outputs/dashboard_tables/national_applications_determinations_trend.csv`
- `outputs/dashboard_tables/state_latest_snapshot.csv`
- `outputs/dashboard_tables/state_enrollment_change.csv`
- `outputs/dashboard_tables/state_eligibility_operations_summary.csv`
- `outputs/dashboard_tables/state_map_metrics.csv`
- `outputs/dashboard_tables/state_population_adjusted_metrics.csv`
- `outputs/dashboard_tables/enrollment_change_from_peak.csv`
- `outputs/dashboard_tables/state_population_adjusted_context.csv`
- `outputs/dashboard_tables/monitoring_review_flags.csv`
- `outputs/dashboard_tables/state_monitoring_summary.csv`
- `outputs/dashboard_tables/national_monitoring_summary.csv`
- `outputs/dashboard_tables/application_determination_balance.csv`
- `outputs/dashboard_tables/application_determination_balance_latest.csv`
- `outputs/dashboard_tables/national_application_determination_balance_trend.csv`
- `outputs/dashboard_tables/top_application_determination_balance_states.csv`
- `outputs/dashboard_tables/application_determination_balance_summary.csv`
- `outputs/dashboard_tables/data_quality_by_field.csv`
- `outputs/dashboard_tables/data_quality_by_state.csv`
- `outputs/dashboard_tables/data_quality_by_month.csv`
- `outputs/dashboard_tables/dashboard_notes.csv`

The `state_map_metrics.csv` table provides one row per state/DC for State Map Explorer context and selected state profile cards.

The Dash app includes a GIS-style State Map Explorer with a linked U.S. choropleth map, ranked horizontal state bar chart, metric selector, reporting-month time control, Top 10/Bottom 10/All ranking control, selected state snapshot, and selected state self-comparison panel. The map uses state-level aggregate data only; it does not create county-level, beneficiary-level, claims, utilization, or cost views.

The selected state self-comparison view shows January 2019 baseline enrollment, peak enrollment, latest enrollment, change since January 2019, change from peak, last-12-month change, Medicaid/CHIP component values, applications, determinations, and Application-Determination Balance where available.

The Medicaid vs CHIP Drivers tab shows national and selected-state Medicaid vs CHIP split views plus a selected-state component trend explorer.

Population-adjusted Medicaid/CHIP metrics include enrollment per 1,000 residents, Medicaid enrollment per 1,000 residents, CHIP enrollment per 1,000 residents, applications submitted per 100,000 residents, and eligibility determinations per 100,000 residents.

The Monitoring Flags tab uses `monitoring_review_flags.csv` to help users review unusual state/month changes and reporting caveats. Review flags are context prompts, not problem labels, performance failures, or causal findings.

The project also includes Application-Determination Balance, a descriptive eligibility operations metric comparing same-month applications submitted and Medicaid/CHIP determinations. It is not a backlog metric, approval rate, timeliness measure, or performance score.

## Run The Dash App

```bash
python app.py
```

Then open `http://127.0.0.1:8050`.

## What This Project Demonstrates

- Reproducible public healthcare data ingestion from official CMS sources
- Source validation and data dictionary documentation
- Medicaid/CHIP enrollment trend analysis
- Eligibility operations reporting using applications and determinations
- Application-Determination Balance for descriptive operations monitoring
- State-by-state comparison and dashboard table preparation
- Population-adjusted enrollment context using official Census denominators
- Diagnostic monitoring indicators and neutral review flags
- Data quality, missingness, and preliminary/final reporting checks
- Policy-facing interpretation without unsupported causal claims

## Repository Structure

```text
medicaid-enrollment-policy-dashboard/
├── README.md
├── app.py
├── requirements.txt
├── .gitignore
├── assets/
│   └── styles.css
├── data/
│   ├── raw/
│   ├── processed/
│   └── data_dictionary.md
├── notebooks/
│   ├── 01_data_ingestion_and_source_validation.ipynb
│   ├── 02_eda_and_dashboard_tables.ipynb
│   └── 03_diagnostic_monitoring_indicators.ipynb
├── src/
│   ├── load_data.py
│   ├── clean_medicaid_data.py
│   ├── eda_medicaid.py
│   ├── build_dashboard_tables.py
│   ├── load_population_data.py
│   ├── build_population_adjusted_metrics.py
│   └── build_monitoring_indicators.py
├── outputs/
│   ├── dashboard_tables/
│   └── figures/
└── docs/
    ├── source_notes.md
    ├── project_brief.md
    ├── project_tasks.md
    ├── data_viability_and_next_steps.md
    ├── eda_findings.md
    ├── population_denominator_notes.md
    ├── monitoring_questions.md
    ├── diagnostic_monitoring_plan.md
    ├── policy_context.md
    └── limitations.md
```

## Next Steps

1. Review the expanded Dash app tabs for wording and portfolio presentation.
2. Add dashboard screenshots to the README after final visual QA.
3. Consider deployment options such as Render, Railway, or another lightweight Dash hosting target.
4. Keep forecasting, causal analysis, call center analysis, and processing-time analysis deferred until a separate validation step supports them.
