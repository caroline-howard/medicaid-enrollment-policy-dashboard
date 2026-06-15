# Data Viability And Next Steps

This report summarizes whether the validated Medicaid/CHIP source data is strong enough to support the next project phase. It is intended to guide the decision before exploratory analysis, dashboard table creation, or dashboard development.

## 1. Dataset Identity

- Exact dataset name: State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data
- Official source URL: https://data.medicaid.gov/dataset/6165f45b-ca93-5bb5-9d06-db29c692a360/data
- Access method: public HTTPS CSV download from CMS/Data.Medicaid.gov, with metadata and data dictionary endpoints used for validation
- Date accessed: 2026-06-15
- Last updated date available from source metadata: 2026-05-29
- Official CMS/Medicaid data: Yes. The dataset is published by CMS/Data.Medicaid.gov and uses public aggregate Medicaid/CHIP performance indicator data.

## 2. Coverage Summary

- Row count: 4,386 cleaned state-month records
- Years/months available after project filtering: January 2019 through February 2026
- Earliest reporting month: 2019-01
- Latest reporting month: 2026-02
- Number of states included: 51 geographies, representing all 50 states plus DC
- DC included: Yes
- Territories included: No
- Reporting frequency: Monthly state-level aggregate data

## 3. Field Availability

| field_needed | available_yes_no | source_column_name | notes |
|---|---|---|---|
| state | Yes | State Abbreviation; State Name | Includes all 50 states plus DC. |
| reporting month/date | Yes | Reporting Period | Parsed into `reporting_month` for state-month trend analysis. |
| Medicaid enrollment | Yes | Total Medicaid Enrollment | Core enrollment trend field. |
| CHIP enrollment | Yes | Total CHIP Enrollment | Core enrollment trend field; CHIP may include adults in some states. |
| total Medicaid/CHIP enrollment | Yes | Total Medicaid and CHIP Enrollment | Strongest field for combined enrollment trend analysis. |
| applications submitted | Yes | New Applications Submitted to Medicaid and CHIP Agencies; Total Applications for Financial Assistance Submitted at State Level | Supports application volume analysis. |
| eligibility determinations | Yes | Individuals Determined Eligible for Medicaid at Application; Individuals Determined Eligible for CHIP at Application; Total Medicaid and CHIP Determinations | Supports eligibility operations analysis. |
| renewals/redeterminations | Partial | Footnotes mention renewals/redeterminations in some cases | Not available as a clean dedicated preserved numeric field. Do not report renewal counts as a standalone metric. |
| pending applications | No | Not available in preserved source fields | Do not invent or infer pending application volume. |
| reporting status or data quality flag | Yes | Preliminary or Updated; Final Report | Used to prefer final/updated records when both preliminary and final records exist. |
| source update date | Yes | Source metadata modified date | Dataset metadata reports 2026-05-29 as the modified date. |

## 4. Data Quality Findings

### Missingness By Field

Most core fields needed for enrollment, application, and determination analysis have no missing values in the cleaned 2019-present all-state/DC panel. The largest missingness concerns are:

| field | missing_count | missing_percent |
|---|---:|---:|
| total_adult_medicaid_enrollment | 3,366 | 76.74% |
| average_call_center_abandonment_rate | 2,590 | 59.05% |
| total_call_center_volume_number_of_calls | 2,590 | 59.05% |
| average_call_center_wait_time_minutes | 2,589 | 59.03% |
| application processing timing fields | 1,377 each | 31.40% |

### Missingness By State

The states with the highest total missingness across preserved fields are South Dakota, Rhode Island, Arizona, Nevada, Arkansas, Colorado, Connecticut, DC, California, and Florida. Much of this is driven by missing adult enrollment, call center, and processing-time fields rather than the core enrollment and application/determination fields.

### Duplicate State-Month Records

- Source duplicate state-month records before cleaning: 4,335
- Cleaned duplicate state-month records: 0

The source includes preliminary and updated/final rows for many state-months. The cleaning logic keeps one row per state-month and prefers final/updated records when available.

### State Names And Date Formats

No inconsistent state abbreviations or date formats were found after cleaning. Reporting periods were parsed into standardized month-start dates.

### Suspicious Zeros

The cleaned numeric fields contain 5,244 zero values. Some zeros may be legitimate, especially for State-Based Marketplace applications, CHIP determinations, or fields that do not apply to a state/month. These should be reviewed by field during EDA before being interpreted as operational performance.

### Negative Values

No negative numeric values were found.

### Incomplete Months

Every month in the cleaned 2019-01 through 2026-02 panel has 51 state/DC records. The latest month, February 2026, contains preliminary records for all 51 geographies and should be labeled cautiously.

### Major Limitations

- Public aggregate data does not support beneficiary-level conclusions.
- The dataset does not include claims, utilization, cost, diagnosis, or individual eligibility detail.
- Renewals/redeterminations and pending applications are not available as dedicated preserved numeric fields.
- Some operational fields have high missingness and should not be treated as complete all-state performance indicators.
- Descriptive trends should not be described as causal policy effects.

## 5. Feasibility Assessment

| question | answer | explanation |
|---|---|---|
| Can this dataset support Medicaid/CHIP enrollment trend analysis? | Yes | Total Medicaid/CHIP, Medicaid, and CHIP enrollment fields are available monthly for all 50 states plus DC from 2019-01 through 2026-02. |
| Can this dataset support eligibility operations analysis? | Yes | Applications submitted and eligibility determinations are available. Some operational subfields, such as processing timing and call center fields, have missingness and need caveats. |
| Can this dataset support state-by-state comparison? | Yes | The cleaned panel includes all 50 states plus DC with one row per state-month and no duplicate cleaned state-months. |
| Can this dataset support a Plotly/Dash dashboard? | Yes | The data is clean, monthly, state-level, and already split into full, summary, sample, and quality outputs. |
| Can this dataset support forecasting? | Partial | Enrollment fields have enough monthly history for a light forecasting extension, but forecasting should be framed as exploratory operational planning, not high-stakes eligibility or budget prediction. |
| Can this dataset support policy interpretation? | Yes | It supports policy-facing descriptive interpretation, reporting context, and data quality caveats. It does not support causal policy claims by itself. |
| What would be misleading or unsupported to claim? | Warning | Unsupported claims include individual outcomes, causal effects, renewal volumes, pending application volumes, claims/utilization patterns, and complete operational performance across all fields. |

## 6. Recommended Project Direction

Recommended option: Option C, Combined enrollment + eligibility dashboard.

This is the strongest scope because the dataset has complete monthly state-level coverage for enrollment, applications, and eligibility determinations. A combined dashboard fits the project goal across healthcare analytics, Medicaid policy, and operations roles. It can show enrollment trends while also demonstrating operational reporting through applications and determinations.

Secondary emphasis: Option D, Data quality/reporting dashboard.

Data quality should be a visible section inside the combined dashboard because the source has preliminary/final reporting behavior, field-level missingness, zero values that require interpretation, and incomplete availability for some operational fields.

Options not recommended as the main first build:

- Option A, Enrollment trend dashboard: Feasible, but narrower than the available data.
- Option B, Eligibility operations dashboard: Feasible, but would miss the strongest and cleanest enrollment fields.
- Option E, Forecasting extension: Useful later, but should not be the next phase.
- Option F, Need another dataset: Not needed for the first dashboard version.

## 7. Recommended Dashboard Sections

- National overview: Build. Use total Medicaid/CHIP enrollment, Medicaid enrollment, CHIP enrollment, applications, and determinations.
- State comparison: Build. Use state-month trends and state-level comparison tables.
- Eligibility operations: Build. Use applications submitted and eligibility determinations. Use processing-time fields only with missingness caveats.
- Data quality/missingness: Build. Show missingness, preliminary/latest-month status, duplicate handling, and field completeness.
- Policy interpretation: Build. Include plain-language notes about what changed, what needs caution, and what the public aggregate data cannot show.
- Forecasting: Defer. Consider only after EDA and dashboard-ready tables are complete.

## 8. Role-Fit Assessment

### Healthcare Business Analyst

Most useful outputs: dashboard-ready summary tables, state comparisons, KPI-style enrollment/application summaries, and policy-facing notes. This project shows reporting structure, stakeholder-friendly documentation, and operational monitoring.

### Healthcare Data Analyst

Most useful outputs: reproducible ingestion scripts, cleaned state-month dataset, data quality summary, missingness checks, and exploratory trend analysis. This project demonstrates Python, validation, documentation, and dashboard preparation.

### Medicaid Policy/Research Associate

Most useful outputs: source notes, limitations, data dictionary, state trend comparisons, and written interpretation. This project supports Medicaid-specific policy monitoring without overstating causal claims.

### Healthcare Operations Analyst

Most useful outputs: applications submitted, eligibility determinations, processing-time fields where available, data quality flags, and state/month variation. This project can support operations-style monitoring while clearly labeling missingness.

### Public-Sector Data Analyst

Most useful outputs: official public data pipeline, transparent source documentation, clean aggregate datasets, reproducible notebook, and limitations reporting. This project fits public reporting and government data quality workflows.

## 9. Next Steps

1. Create an exploratory analysis notebook focused on enrollment trends, applications, determinations, missingness, and preliminary/final reporting behavior.
2. Build dashboard-ready tables in `outputs/dashboard_tables/` for national overview, state comparison, eligibility operations, and data quality sections.
3. Draft policy interpretation notes that explain trend findings without making causal claims.
4. Update README with EDA findings and a brief "What this project demonstrates" section.
5. Begin Plotly Dash dashboard development only after the dashboard-ready summary tables are created and reviewed.
