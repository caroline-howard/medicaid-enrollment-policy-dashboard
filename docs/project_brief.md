# Project Brief

## Medicaid Enrollment & Eligibility Operations Analytics

This brief summarizes a public-data healthcare policy analytics portfolio project focused on Medicaid/CHIP enrollment, eligibility operations, state comparison, and reporting quality. It is written as a concise project brief that could be adapted into a short writing sample for healthcare research, Medicaid policy, or program evaluation support roles.

## Purpose

Medicaid and CHIP are state-federal coverage programs serving low-income and medically vulnerable populations. Public reporting data can help analysts monitor enrollment levels, state variation, applications, eligibility determinations, and reporting completeness. However, these data must be interpreted carefully because they are aggregate, state-reported, and descriptive.

This project turns official public Medicaid/CHIP data into a reproducible monitoring workflow and Plotly Dash dashboard. The goal is to support evidence-informed reporting, not causal evaluation.

## Policy And Program Monitoring Questions

The dashboard helps answer questions such as:

- How has national Medicaid/CHIP enrollment changed since January 2019?
- How do selected states compare with the national trend and with each other?
- Are state differences driven by raw enrollment scale, population-adjusted context, Medicaid vs CHIP composition, or eligibility operations activity?
- What application and determination indicators are available for descriptive monitoring?
- Which fields have reporting caveats, missingness, or limited interpretability?
- How should fiscal-year expenditure context be distinguished from monthly enrollment context?

## Data Sources

Primary source:

- CMS/Data.Medicaid.gov State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data

Supporting context sources:

- U.S. Census Bureau state population estimates
- Medicaid.gov State Profiles context files for enrollment and MAGI eligibility threshold context
- Medicaid.gov MBES/CBES Financial Management Report files for fiscal-year expenditure context
- KFF State Health Facts FMAP/eFMAP data and Medicaid.gov CHIP program structure files retained for financing and program design context

The main analytic dataset is monthly state-level aggregate data for all 50 states plus DC from January 2019 through February 2026.

## Analytic Workflow

1. Data ingestion: Downloaded official CMS/Data.Medicaid.gov Medicaid/CHIP source files and retained raw-source traceability.
2. Cleaning: Standardized column names, parsed reporting months, standardized state names and abbreviations, and preserved key enrollment and eligibility operations fields.
3. Validation: Reviewed row counts, date range, state coverage, duplicate state-month records, preliminary/final reporting status, and missingness.
4. Derived metrics: Created descriptive measures such as enrollment change since January 2019, change from observed peak, Medicaid/CHIP shares, population-adjusted rates, application-determination balance, and fiscal-year expenditure summaries.
5. Dashboard outputs: Built dashboard-ready tables and a Plotly Dash app with national monitoring, state comparison, enrollment trend, eligibility context, operations/program mix, and fiscal profile views.
6. Interpretation: Documented limitations and framed findings as descriptive monitoring rather than causal evidence.

## Dashboard Outputs

The current app includes two visible sections:

### National Snapshot

An executive-style summary of national enrollment trends. It includes KPI cards, a selected-state vs national indexed trend, state map context, and a policy/reporting timeline.

### State Comparison Explorer

A two-state workflow for comparing selected states and reviewing within-state context. It includes national rank context, a direct comparison table, trend-over-time comparison, and profile tabs for enrollment trend, eligibility context, and fiscal profile.

## Relevance To Healthcare Research And Medicaid Policy Roles

This project demonstrates applied skills relevant to healthcare research, Medicaid policy, and public-sector analytics roles:

- collecting and reviewing official Medicaid program data
- preparing reproducible quantitative summaries in Python
- creating charts, tables, and dashboard views for program monitoring
- documenting source quality, missingness, and reporting limitations
- translating technical findings into clear policy-facing language
- supporting evidence-informed reporting for policymakers, payers, providers, and healthcare program audiences

It does not imply direct Medicaid program administration experience or formal causal program evaluation.

## Limitations

The project uses public aggregate state-month data. It does not include beneficiary-level records, claims, utilization, costs, diagnoses, managed care plan data, county-level variation, or individual coverage outcomes.

Applications and determinations are descriptive eligibility operations indicators. They should not be interpreted as approval rates, backlog measures, timeliness metrics, or complete performance scores.

Fiscal profile values come from fiscal-year MBES/CBES financial reporting and are not monthly enrollment values.

The dashboard does not estimate causal effects of Medicaid expansion, unwinding, waiver policy, CHIP program design, or administrative changes.

## Resume Bullet Options

- Built a reproducible Medicaid/CHIP public-data analytics workflow using Python and Plotly Dash, including source validation, data cleaning, derived metrics, dashboard-ready tables, and policy-facing interpretation.
- Analyzed official CMS Medicaid/CHIP enrollment and eligibility operations data to create state comparison outputs, charts, source notes, and limitations documentation for healthcare policy monitoring.
- Developed a dashboard and written project brief translating public Medicaid program data into concise findings for healthcare research, program evaluation support, and public-sector reporting audiences.

## Writing Sample Note

This brief can be adapted into a concise writing sample for healthcare research and Medicaid policy applications. A writing-sample version should keep the same descriptive framing, cite the official source files, include selected screenshots or charts, and preserve the limitations language.
