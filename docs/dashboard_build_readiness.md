# Dashboard Build Readiness Report

This report reviews the completed EDA outputs and dashboard-ready tables before starting Plotly Dash app development. It does not add new analysis or build the dashboard.

## 1. Dashboard-Ready Table Check

All expected dashboard-ready tables were created successfully in `outputs/dashboard_tables/`.

| expected_table | status | rows | ready_for_dashboard |
|---|---:|---:|---|
| `kpi_summary.csv` | Created | 8 | Yes |
| `national_enrollment_trend.csv` | Created | 86 | Yes |
| `national_applications_determinations_trend.csv` | Created | 86 | Yes |
| `state_latest_snapshot.csv` | Created | 51 | Yes |
| `state_enrollment_change.csv` | Created | 51 | Yes |
| `state_eligibility_operations_summary.csv` | Created | 51 | Yes |
| `data_quality_by_field.csv` | Created | 27 | Yes |
| `data_quality_by_state.csv` | Created | 51 | Yes |
| `data_quality_by_month.csv` | Created | 86 | Yes |
| `dashboard_notes.csv` | Created | 7 | Yes |

Static figures were also created in `outputs/figures/` for documentation and design reference.

## 2. Dashboard Sections Ready To Build

| section | readiness | notes |
|---|---|---|
| National overview | Ready | National enrollment, Medicaid enrollment, CHIP enrollment, applications, and determinations tables are available. |
| State comparison | Ready | Latest state snapshot and state enrollment change tables are available for table or chart views. |
| Eligibility operations | Ready with caveats | Applications and determinations are available and suitable as descriptive operational indicators. |
| Data quality/missingness | Ready | Field, state, and month quality tables are available. |
| Policy interpretation | Ready | `dashboard_notes.csv`, source notes, EDA findings, and limitations provide plain-language content. |

## 3. Recommended Top KPI Cards

Use reliable, clearly documented fields for the first dashboard version:

1. Latest reporting month
2. Latest month preliminary status
3. States/DC included
4. Latest total Medicaid/CHIP enrollment
5. Change since January 2019
6. Latest applications submitted or latest total determinations

The first version should keep KPI cards simple and pair the preliminary-status KPI with visible caution text.

## 4. Fields Not Recommended As Headline KPIs

These fields should not be used as headline KPIs in Version 1 because of missingness, interpretation limits, or unavailable source fields:

- Adult Medicaid enrollment: high missingness, 76.74%.
- Call center volume, wait time, and abandonment rate: high missingness around 59%.
- Application processing-time fields: missingness around 31.40%.
- Renewals/redeterminations: not available as a clean dedicated numeric field.
- Pending applications: not available in the preserved source fields.
- State-Based Marketplace applications: many zero values; useful only with careful state-specific context.

These fields may appear in a data quality or supplemental operations section if clearly labeled with caveats.

## 5. Recommended Version 1 Dashboard Layout

Version 1 should be a simple combined enrollment + eligibility operations dashboard:

1. KPI cards: latest reporting month, preliminary status, states/DC included, latest total Medicaid/CHIP enrollment, enrollment change since January 2019, and latest applications or determinations.
2. National enrollment trend chart: total Medicaid/CHIP, Medicaid, and CHIP enrollment over time.
3. Applications/determinations trend chart: national applications submitted and Medicaid/CHIP determinations over time.
4. State comparison table or chart: latest enrollment, rank, change since January 2019, and last-12-month change.
5. Data quality section: missingness by field, state, and month; latest-month preliminary status.
6. Policy notes section: source, interpretation, missingness caveats, and dashboard limitations.

## 6. Items To Defer

| item | recommendation | reason |
|---|---|---|
| Forecasting | Defer | Forecasting should be a later extension after the descriptive dashboard is stable. |
| Call center analysis | Defer or supplemental only | High missingness makes call center fields weak headline indicators. |
| Processing-time analysis | Defer or supplemental only | Processing-time fields have substantial missingness and need careful caveats. |
| Causal claims | Defer/avoid | The dataset supports descriptive monitoring, not causal policy effects. |
| Medicaid expansion comparison | Defer | Expansion status exists, but meaningful comparison needs careful policy context and may distract from Version 1. |

## 7. Dashboard Limitations To State Clearly

The dashboard should clearly say it cannot show:

- beneficiary-level outcomes
- claims, utilization, cost, diagnosis, or encounter patterns
- causal effects of Medicaid policy changes
- complete operational performance across all fields
- clean standalone renewal/redetermination volumes
- pending application volume
- final interpretation of the latest month without noting preliminary reporting

The latest reporting month, February 2026, is preliminary for all 50 states plus DC in the current dashboard-ready tables.

## 8. Final Recommendation

Readiness: Yes.

The project is ready for Plotly Dash development. The required dashboard-ready tables exist, the main dashboard sections are supported, and the most important limitations are documented.

Next exact task: Build the Plotly Dash app using the dashboard-ready tables.
