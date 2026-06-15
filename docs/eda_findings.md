# EDA Findings

This document summarizes exploratory findings from the cleaned CMS/Data.Medicaid.gov Medicaid/CHIP state-month dataset. Findings are descriptive and should not be interpreted as causal policy effects.

## Key Enrollment Findings

- The cleaned dataset includes 4,386 state-month records for all 50 states plus DC from January 2019 through February 2026.
- National Medicaid/CHIP enrollment was relatively flat in 2019, rose through the early pandemic-era period, peaked in April 2023, and then declined through the latest available reporting month.
- National total Medicaid/CHIP enrollment was 72,165,928 in January 2019 and 74,877,742 in February 2026, a descriptive increase of 2,711,814.
- The latest month, February 2026, is preliminary for all 51 geographies and should be labeled cautiously.
- The largest enrollment increases since January 2019 are in North Carolina, California, Virginia, Missouri, and Oregon.
- The largest enrollment decreases since January 2019 are in Texas, Louisiana, Michigan, Florida, and Colorado.

## Key Eligibility Operations Findings

- Applications submitted and Medicaid/CHIP eligibility determinations are available and suitable for descriptive operations analysis.
- The February 2026 national table reports 2,460,804 applications submitted and 1,601,892 Medicaid/CHIP determinations.
- National applications peak in January 2024 in the dashboard-ready table.
- National Medicaid/CHIP determinations peak in December 2023 in the dashboard-ready table.
- Derived ratios such as determinations per application, applications per 1,000 enrollees, and determinations per 1,000 enrollees are useful descriptive indicators, but they should not be treated as complete performance metrics.

## Key Data Quality Findings

- The cleaned dataset has zero duplicate state-month records.
- The original source includes preliminary and updated/final rows for many state-months; the cleaning workflow keeps one state-month row and prefers updated/final records when available.
- No negative numeric values were found.
- The dataset contains zero values in several numeric fields. Some zeros may be valid, especially for fields that are not applicable to every state/month, but they require context.
- Core enrollment, application, and determination fields have no missing values in the cleaned panel.
- Adult Medicaid enrollment, call center fields, and application processing-time fields have substantial missingness and should not be used as headline KPIs without caveats.

## Recommended Dashboard Sections

- National overview: total Medicaid/CHIP enrollment, Medicaid enrollment, CHIP enrollment, applications, and determinations.
- State comparison: latest state enrollment, state ranks, change since January 2019, and last-12-month change.
- Eligibility operations: applications, determinations, descriptive ratios, and state-level operations summaries.
- Data quality/missingness: missingness by field, state, and month; latest-month preliminary status; source reporting caveats.
- Policy interpretation: plain-language notes that explain observed patterns and caution against unsupported claims.

## Limitations

- Public aggregate data does not support individual-level conclusions.
- The data does not include claims, utilization, cost, diagnosis, or beneficiary-level eligibility detail.
- Renewals/redeterminations and pending applications are not available as dedicated preserved numeric fields.
- Operational fields with high missingness should be presented as supplemental context, not complete performance measures.
- Descriptive trends should not be framed as causal policy effects.
- February 2026 is preliminary for all states/DC in the current source extract.

## Next Steps Before Dashboard Development

1. Review dashboard-ready tables in `outputs/dashboard_tables/`.
2. Confirm final KPI choices for the first dashboard version.
3. Decide which data quality warnings should be visible in the dashboard UI.
4. Use `dashboard_notes.csv` as the starting point for policy-facing dashboard notes.
5. Build the Plotly Dash app after confirming the dashboard table structure.
