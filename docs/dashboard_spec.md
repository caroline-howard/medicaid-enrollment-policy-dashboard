# Dashboard Specification

This specification defines the Version 1 Plotly Dash app for the Medicaid Enrollment & Eligibility Operations Dashboard. It uses the dashboard-ready tables created during EDA and does not add forecasting, causal analysis, or new data sources.

## 1. Dashboard Sections

### National Overview

Purpose: Show national Medicaid/CHIP enrollment trends and high-level current status.

Primary tables:

- `outputs/dashboard_tables/kpi_summary.csv`
- `outputs/dashboard_tables/national_enrollment_trend.csv`
- `outputs/dashboard_tables/dashboard_notes.csv`

Core visuals:

- KPI cards
- national Medicaid/CHIP enrollment line chart
- Medicaid vs CHIP enrollment line chart

### State Comparison

Purpose: Compare latest state enrollment and enrollment changes across states.

Primary tables:

- `outputs/dashboard_tables/state_latest_snapshot.csv`
- `outputs/dashboard_tables/state_enrollment_change.csv`
- `outputs/dashboard_tables/national_enrollment_trend.csv`

Core visuals:

- selected state profile card
- state comparison table
- top state enrollment change chart
- selected state vs national trend comparison

### Eligibility Operations

Purpose: Show applications and determinations as descriptive operational indicators.

Primary tables:

- `outputs/dashboard_tables/national_applications_determinations_trend.csv`
- `outputs/dashboard_tables/state_eligibility_operations_summary.csv`
- `outputs/dashboard_tables/dashboard_notes.csv`

Core visuals:

- national applications and determinations trend chart
- state applications/determinations comparison table
- descriptive ratios such as determinations per application and applications per 1,000 enrollees

### Data Quality

Purpose: Make missingness, preliminary reporting, and reporting caveats visible.

Primary tables:

- `outputs/dashboard_tables/data_quality_by_field.csv`
- `outputs/dashboard_tables/data_quality_by_state.csv`
- `outputs/dashboard_tables/data_quality_by_month.csv`
- `outputs/dashboard_tables/dashboard_notes.csv`

Core visuals:

- field missingness table
- state missingness table
- monthly completeness/preliminary reporting table
- warning banner

### Policy Interpretation

Purpose: Explain what the dashboard can and cannot show in plain language.

Primary tables and docs:

- `outputs/dashboard_tables/dashboard_notes.csv`
- `docs/source_notes.md`
- `docs/eda_findings.md`
- `docs/data_viability_and_next_steps.md`

Core content:

- data source note
- interpretation note
- missingness caveat
- unsupported claims note
- limitations list

## 2. KPI Cards

Use 4-6 KPI cards in Version 1:

1. Latest reporting month
2. Latest month preliminary status
3. States/DC included
4. Latest total Medicaid/CHIP enrollment
5. Change since January 2019
6. Latest applications submitted or latest total determinations

Use `latest_applications_submitted` and `latest_total_determinations` as descriptive operations KPIs only. They should not be labeled as performance scores.

## 3. Filters

### State Selector

Input: `state_abbreviation` or `state_name`

Use for:

- selected state profile
- selected state vs national comparison
- state-specific enrollment and operations values

Default: largest state by latest total Medicaid/CHIP enrollment, or alphabetical first state if simpler.

### Metric Selector

Recommended metrics:

- total Medicaid/CHIP enrollment
- total Medicaid enrollment
- total CHIP enrollment
- applications submitted
- Medicaid/CHIP determinations
- applications per 1,000 enrollees
- determinations per 1,000 enrollees

Do not include high-missingness call center or processing-time fields in the default metric selector for Version 1.

### Date Range Selector

Input: reporting month range from January 2019 through February 2026.

Use for:

- national trend charts
- selected state trend charts
- applications/determinations trend chart

The latest month should display a caution if preliminary records are included.

### Selected State Vs National Comparison

Show selected state trend against national context. For enrollment comparisons, use either:

- indexed trend values where January 2019 equals 100, or
- selected state enrollment alongside national enrollment on separate axes or normalized scale.

Avoid plotting raw state and national counts on the same single-axis chart because national counts will dwarf state values.

## 4. State Profile Card Fields

Use fields from `state_latest_snapshot.csv` and `state_enrollment_change.csv`:

- state name
- state abbreviation
- latest reporting month
- latest total Medicaid/CHIP enrollment
- latest Medicaid enrollment
- latest CHIP enrollment
- national enrollment rank
- change since January 2019
- percent change since January 2019
- change over last 12 months
- final/preliminary status for latest month

Optional operations fields from `state_eligibility_operations_summary.csv`:

- total applications submitted
- total Medicaid/CHIP determinations
- determinations per application
- applications per 1,000 average enrollees
- determinations per 1,000 average enrollees

## 5. Data Quality Warning Banner Text

Recommended banner text:

> Data quality note: February 2026 is the latest available reporting month and is preliminary for all 50 states plus DC. Adult Medicaid enrollment, call center fields, and application processing-time fields have substantial missingness. Applications and determinations are descriptive operational indicators, not complete performance measures.

Keep the warning visible near the top of the dashboard or within the Data Quality section.

## 6. Fields Excluded From Headline KPIs

Do not use these fields as headline KPI cards in Version 1:

| field | reason |
|---|---|
| `total_adult_medicaid_enrollment` | High missingness, 76.74%. |
| `total_call_center_volume_number_of_calls` | High missingness around 59%. |
| `average_call_center_wait_time_minutes` | High missingness around 59%; not complete enough for a headline KPI. |
| `average_call_center_abandonment_rate` | High missingness around 59%; interpretation depends on call center reporting practices. |
| processing-time fields | Missingness around 31.40%; better as supplemental analysis later. |
| renewals/redeterminations | Not available as a clean dedicated numeric field. |
| pending applications | Not available in the preserved source fields. |
| State-Based Marketplace applications | Many zero values and state-specific applicability concerns. |

## 7. Limitations That Must Appear In The App

The dashboard must clearly state:

- Data is public aggregate CMS/Data.Medicaid.gov data.
- The dashboard does not contain beneficiary-level data.
- The dashboard does not contain claims, utilization, cost, diagnosis, or encounter data.
- The dashboard does not estimate causal effects of policy changes.
- Some operational fields are incomplete and should not be treated as complete performance measures.
- Renewals/redeterminations and pending applications are not available as clean standalone fields.
- February 2026 is preliminary for all 50 states plus DC in the current tables.

## 8. Dashboard-Ready Tables By Section

| dashboard_section | tables |
|---|---|
| National Overview | `kpi_summary.csv`, `national_enrollment_trend.csv`, `dashboard_notes.csv` |
| State Comparison | `state_latest_snapshot.csv`, `state_enrollment_change.csv`, `national_enrollment_trend.csv` |
| Eligibility Operations | `national_applications_determinations_trend.csv`, `state_eligibility_operations_summary.csv`, `dashboard_notes.csv` |
| Data Quality | `data_quality_by_field.csv`, `data_quality_by_state.csv`, `data_quality_by_month.csv`, `dashboard_notes.csv` |
| Policy Interpretation | `dashboard_notes.csv` plus `docs/source_notes.md`, `docs/eda_findings.md`, and `docs/data_viability_and_next_steps.md` |

## 9. Final Version 1 Scope

Version 1 should include:

- KPI cards using reliable fields
- national enrollment trend chart
- Medicaid vs CHIP trend chart
- applications and determinations trend chart
- state selector
- state profile card
- state comparison table or chart
- data quality/missingness section
- policy interpretation notes
- limitations text

Version 1 should prioritize clarity, reproducibility, and policy-facing interpretation over complexity.

## 10. Deferred Features

Defer these features until after Version 1 is stable:

- forecasting
- causal analysis
- call center analysis
- processing-time analysis
- Medicaid expansion comparison
- renewal/redetermination analysis
- pending application analysis

These features require either additional design, better field completeness, more policy context, or additional data sources.
