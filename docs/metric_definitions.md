# Metric Definitions

This file defines the Version 1 dashboard KPIs and dashboard metrics in plain language. Metrics are descriptive and should not be interpreted as causal effects or complete operational performance scores.

## KPI Cards

| metric | plain_language_definition | numerator | denominator | source_field | interpretation | limitations |
|---|---|---|---|---|---|---|
| Latest reporting month | Most recent month available in the dashboard-ready tables. | Latest `reporting_month` | Not applicable | `reporting_month` | Shows the currency of the dashboard data. | The latest month may be preliminary and should not be treated as final without checking reporting status. |
| Latest month preliminary status | Whether the latest reporting month includes preliminary records. | Count of latest-month records where `final_report != "Y"` | Total latest-month state/DC records | `final_report`; `preliminary_or_updated` | Warns users when the latest data may be revised later. | Does not quantify the size or direction of future revisions. |
| States/DC included | Number of state/DC geographies included in the cleaned dashboard data. | Count of unique `state_abbreviation` values | Not applicable | `state_abbreviation` | Confirms geographic coverage for state comparison. | Territories are not included. |
| Latest total Medicaid/CHIP enrollment | National sum of total Medicaid/CHIP enrollment in the latest reporting month. | Sum of `total_medicaid_and_chip_enrollment` across all state/DC records in latest month | Not applicable | `total_medicaid_and_chip_enrollment` | Shows current aggregate Medicaid/CHIP enrollment in the public source. | Latest month is preliminary; this is an aggregate count and does not show individual-level eligibility experiences. |
| Change since January 2019 | Difference between latest national Medicaid/CHIP enrollment and January 2019 national Medicaid/CHIP enrollment. | Latest national `total_medicaid_and_chip_enrollment` minus January 2019 national `total_medicaid_and_chip_enrollment` | January 2019 national `total_medicaid_and_chip_enrollment` only if showing percent change | `total_medicaid_and_chip_enrollment`; `reporting_month` | Provides a descriptive long-run enrollment change from the project baseline. | Not a causal estimate and should not be attributed to a policy without further analysis. |
| Latest applications submitted | National total applications for financial assistance submitted at state level in the latest reporting month. | Sum of `total_applications_for_financial_assistance_submitted_at_state_level` across state/DC records in latest month | Not applicable | `total_applications_for_financial_assistance_submitted_at_state_level` | Shows current application volume as a descriptive operations indicator. | Not a complete measure of workload, pending applications, renewals, timeliness, or applicant experience. |
| Latest total determinations | National total Medicaid/CHIP determinations at application in the latest reporting month. | Sum of `total_medicaid_and_chip_determinations` across state/DC records in latest month | Not applicable | `total_medicaid_and_chip_determinations` | Shows current eligibility determination activity as a descriptive operations indicator. | Does not measure determination quality, timeliness, pending workload, renewals, or final eligibility outcomes beyond the source definition. |

## Enrollment Metrics

| metric | plain_language_definition | numerator | denominator | source_field | interpretation | limitations |
|---|---|---|---|---|---|---|
| Total Medicaid/CHIP enrollment | Point-in-time count of individuals enrolled in Medicaid or CHIP at month end. | `total_medicaid_and_chip_enrollment` | Not applicable | `total_medicaid_and_chip_enrollment` | Main combined enrollment trend measure. | Aggregate state-reported count; does not show individual demographics, eligibility pathways, or reasons for change. |
| Total Medicaid enrollment | Point-in-time count of individuals enrolled in Medicaid at month end. | `total_medicaid_enrollment` | Not applicable | `total_medicaid_enrollment` | Shows Medicaid enrollment trend separately from CHIP. | Aggregate count only; not causal and not beneficiary-level. |
| Total CHIP enrollment | Point-in-time count of individuals enrolled in CHIP at month end. | `total_chip_enrollment` | Not applicable | `total_chip_enrollment` | Shows CHIP enrollment trend separately from Medicaid. | CHIP may include adults in some states; use source caveats. |
| Monthly enrollment change | Change in national or state Medicaid/CHIP enrollment from the previous reporting month. | Current month enrollment minus prior month enrollment | Prior month enrollment if calculating percent monthly change | `total_medicaid_and_chip_enrollment`; `reporting_month` | Shows short-term direction and size of change. | Month-to-month changes can reflect reporting updates, seasonality, or administrative timing; not causal. |
| Percent monthly enrollment change | Monthly enrollment change as a percent of prior month enrollment. | Current month enrollment minus prior month enrollment | Prior month enrollment | `total_medicaid_and_chip_enrollment`; `reporting_month` | Allows comparison across states of different sizes. | Sensitive to small denominators and reporting revisions. |
| Year-over-year enrollment change | Change from the same reporting month in the prior year. | Current month enrollment minus same-month-prior-year enrollment | Same-month-prior-year enrollment if calculating percent year-over-year change | `total_medicaid_and_chip_enrollment`; `reporting_month` | Helps reduce some seasonality compared with month-to-month change. | Requires at least 12 months of history; still descriptive and not causal. |
| Latest state enrollment rank | State rank by latest total Medicaid/CHIP enrollment. | Latest state `total_medicaid_and_chip_enrollment` | Not applicable | `total_medicaid_and_chip_enrollment`; `state_abbreviation` | Shows relative state size in the latest month. | Large states naturally rank higher; rank is not a performance measure. |

## Eligibility Operations Metrics

| metric | plain_language_definition | numerator | denominator | source_field | interpretation | limitations |
|---|---|---|---|---|---|---|
| Applications submitted | Applications for financial assistance submitted at state level during the month. | `total_applications_for_financial_assistance_submitted_at_state_level` | Not applicable | `total_applications_for_financial_assistance_submitted_at_state_level` | Descriptive indicator of application volume. | Does not show pending applications, renewals, processing time, or application complexity. |
| Medicaid/CHIP agency applications | Applications received by Medicaid and CHIP agencies during the month, excluding Federally-facilitated Marketplace transfers. | `new_applications_submitted_to_medicaid_and_chip_agencies` | Not applicable | `new_applications_submitted_to_medicaid_and_chip_agencies` | Alternative application volume field focused on Medicaid/CHIP agencies. | Not the same as all state-level financial assistance applications. |
| Total Medicaid/CHIP determinations | Total Medicaid and CHIP eligible determinations made at application during the month. | `total_medicaid_and_chip_determinations` | Not applicable | `total_medicaid_and_chip_determinations` | Descriptive indicator of eligibility determination activity. | Does not measure accuracy, timeliness, pending workload, or renewal determinations. |
| Medicaid determinations | Individuals determined eligible for Medicaid at application during the month. | `individuals_determined_eligible_for_medicaid_at_application` | Not applicable | `individuals_determined_eligible_for_medicaid_at_application` | Shows Medicaid component of determination activity. | Application-stage determinations only; not a complete eligibility operations measure. |
| CHIP determinations | Individuals determined eligible for CHIP at application during the month. | `individuals_determined_eligible_for_chip_at_application` | Not applicable | `individuals_determined_eligible_for_chip_at_application` | Shows CHIP component of determination activity. | Some states may report zeros depending on program structure and applicability. |
| Determinations per application | Ratio of Medicaid/CHIP determinations to applications submitted. | `total_medicaid_and_chip_determinations` | `total_applications_for_financial_assistance_submitted_at_state_level` | Derived from applications and determinations fields | Descriptive relationship between determination activity and application volume. | Not an approval rate, not a timeliness measure, and not a performance score. Numerator and denominator are not identical operational concepts. |
| Applications per 1,000 enrollees | Applications submitted per 1,000 Medicaid/CHIP enrollees. | `total_applications_for_financial_assistance_submitted_at_state_level` * 1,000 | `total_medicaid_and_chip_enrollment` | Derived from applications and enrollment fields | Normalizes application volume by enrollment scale. | Descriptive workload context only; enrollment denominator is point-in-time while applications are monthly flow. |
| Determinations per 1,000 enrollees | Medicaid/CHIP determinations per 1,000 Medicaid/CHIP enrollees. | `total_medicaid_and_chip_determinations` * 1,000 | `total_medicaid_and_chip_enrollment` | Derived from determinations and enrollment fields | Normalizes determination activity by enrollment scale. | Descriptive operations context only; not a quality, timeliness, or outcome measure. |

## Data Quality Metrics

| metric | plain_language_definition | numerator | denominator | source_field | interpretation | limitations |
|---|---|---|---|---|---|---|
| Field missing count | Number of missing values for a field in the cleaned dataset. | Count of null values for a field | Total records | Dashboard table `data_quality_by_field.csv` | Identifies fields that need caution. | Missingness does not explain why a value is missing. |
| Field missing percent | Percent of records missing a field. | Missing count for field | Total records | Dashboard table `data_quality_by_field.csv` | Helps compare field completeness. | High missingness should limit dashboard prominence. |
| State missing percent | Percent of preserved cells missing for each state/DC. | Missing values across preserved fields for a state | Total preserved state cells | Dashboard table `data_quality_by_state.csv` | Identifies states with more missing operational fields. | Not all fields are equally important; high missingness may be driven by supplemental fields. |
| Month missing percent | Percent of preserved cells missing for each reporting month. | Missing values across preserved fields for a month | Total preserved month cells | Dashboard table `data_quality_by_month.csv` | Identifies reporting months with more missing data. | Does not explain source reporting reasons. |
| Preliminary records | Number of records in a month where final report status is not final. | Count where `final_report != "Y"` | Total records in month | `final_report`; dashboard table `data_quality_by_month.csv` | Flags months that should be interpreted cautiously. | Does not show the likely size or direction of later revisions. |
| Zero count | Number of zero values for a numeric field. | Count of values equal to zero | Total records | Dashboard table `data_quality_by_field.csv` | Helps identify values that may need interpretation. | Zeros can be valid, not applicable, or reporting artifacts depending on field and state. |

## Metrics Excluded From Headline KPIs

| field_or_metric | reason_excluded |
|---|---|
| Adult Medicaid enrollment | High missingness; use only with strong caveats. |
| Call center volume | High missingness and possible differences in state call center reporting. |
| Average call center wait time | High missingness; not complete enough for a headline KPI. |
| Average call center abandonment rate | High missingness and reporting variation. |
| Processing-time categories | Substantial missingness; useful only as supplemental analysis later. |
| Renewals/redeterminations | Not available as a clean dedicated numeric field. |
| Pending applications | Not available in the preserved source fields. |
| Causal policy impact | Not a metric supported by this descriptive aggregate dataset. |
