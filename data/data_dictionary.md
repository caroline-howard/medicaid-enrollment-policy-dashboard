# Data Dictionary

This data dictionary summarizes the key source files, processed files, dashboard-ready tables, and important variables used in the Medicaid Enrollment & Eligibility Operations Analytics project.

## Key Source And Context Files

| file | purpose | notes |
|---|---|---|
| `data/raw/pi-dataset-may-2026-release.csv` | Raw CMS/Data.Medicaid.gov Medicaid/CHIP applications, determinations, and enrollment extract | Raw files are excluded from Git. The processed outputs are used by the app. |
| `data/processed/medicaid_enrollment_clean.csv` | Cleaned state-month CMS data | Core file for enrollment, applications, determinations, and reporting status. |
| `data/processed/medicaid_state_month_summary.csv` | State-month summary table | Used for analysis and dashboard table builds. |
| `data/processed/state_population_denominators.csv` | Census state population denominators | Used for descriptive population-adjusted metrics. |
| `data/manual/state_demographic_context_candidates.csv` | Medicaid.gov State Profiles context and MAGI eligibility thresholds | Labeled in the app as eligibility and enrollment context, not demographics. |
| `data/manual/state_expenditure_context_candidates.csv` | Medicaid.gov MBES/CBES fiscal-year expenditure context | Used for fiscal profile summaries. |
| `data/context/kff_medicaid_fmap_multiplier.csv` | KFF Medicaid FMAP and multiplier context | Retained as financing context. |
| `data/context/kff_chip_efmap.csv` | KFF CHIP enhanced FMAP context | Retained as financing context. |
| `data/context/chip_program_structure.csv` | Medicaid.gov CHIP program structure categories | Retained as CHIP structure context. |

## Core Cleaned Monthly Fields

| field_name | plain_language_definition | source_field_name | data_type | notes |
|---|---|---|---|---|
| `state_abbreviation` | Two-letter state or DC abbreviation. | State Abbreviation | string | Includes all 50 states plus DC. |
| `state_name` | Full state or DC name. | State Name | string | Standardized for dashboard display. |
| `reporting_period` | Source reporting period in YYYYMM format. | Reporting Period | integer | Retained for traceability. |
| `reporting_month` | Month-start date parsed from reporting period. | Reporting Period | date | Used for monthly trend analysis. |
| `reporting_year` | Calendar year derived from reporting month. | Reporting Period | integer | Derived field. |
| `state_expanded_medicaid` | Whether the state had expanded Medicaid as reported in the source. | State Expanded Medicaid | string | Source uses Y/N values. |
| `preliminary_or_updated` | Whether the source record is preliminary or updated. | Preliminary or Updated | string | Source uses P or U values. |
| `final_report` | Whether the source record is final. | Final Report | string | Used in source-quality interpretation. |
| `total_medicaid_and_chip_enrollment` | Total Medicaid/CHIP enrollment at month end. | Total Medicaid and CHIP Enrollment | numeric | Core enrollment trend measure. |
| `total_medicaid_enrollment` | Medicaid enrollment at month end. | Total Medicaid Enrollment | numeric | Used for Medicaid vs CHIP composition. |
| `total_chip_enrollment` | CHIP enrollment at month end. | Total CHIP Enrollment | numeric | CHIP program design varies by state. |
| `medicaid_and_chip_child_enrollment` | Child Medicaid plus CHIP enrollment count at month end. | Medicaid and CHIP Child Enrollment | numeric | CHIP may include different structures by state. |
| `total_adult_medicaid_enrollment` | Adult Medicaid enrollment at month end. | Total Adult Medicaid Enrollment | numeric | High missingness; not a headline KPI. |
| `new_applications_submitted_to_medicaid_and_chip_agencies` | New applications submitted to Medicaid and CHIP agencies during the month. | New Applications Submitted to Medicaid and CHIP Agencies | numeric | Descriptive operations indicator. |
| `total_applications_for_financial_assistance_submitted_at_state_level` | Total state-level applications for financial assistance. | Total Applications for Financial Assistance Submitted at State Level | numeric | May include state-based marketplace application activity where applicable. |
| `individuals_determined_eligible_for_medicaid_at_application` | Medicaid eligibility determinations at application. | Individuals Determined Eligible for Medicaid at Application | numeric | Descriptive operations indicator. |
| `individuals_determined_eligible_for_chip_at_application` | CHIP eligibility determinations at application. | Individuals Determined Eligible for CHIP at Application | numeric | Descriptive operations indicator. |
| `total_medicaid_and_chip_determinations` | Total Medicaid and CHIP eligibility determinations at application. | Total Medicaid and CHIP Determinations | numeric | Not an approval rate or timeliness metric. |

## Derived Dashboard Fields

| field_name | plain_language_definition | source_field_name | data_type | notes |
|---|---|---|---|---|
| `change_since_january_2019` | Change in total Medicaid/CHIP enrollment compared with January 2019. | Derived | numeric | Used for state and national descriptive trend context. |
| `percent_change_since_january_2019` | Percent change in total Medicaid/CHIP enrollment compared with January 2019. | Derived | numeric | Percent values are represented as 0-100 in dashboard tables. |
| `change_from_peak` | Change from a state's observed peak enrollment to the selected/latest month. | Derived | numeric | Declines from peak are descriptive, not causal. |
| `percent_change_from_peak` | Percent change from observed peak enrollment. | Derived | numeric | Used for comparison and profile context. |
| `medicaid_share` | Medicaid enrollment divided by total Medicaid/CHIP enrollment. | Derived | numeric | Program mix context. |
| `chip_share` | CHIP enrollment divided by total Medicaid/CHIP enrollment. | Derived | numeric | Program mix context. |
| `applications_per_100000_residents` | Applications submitted per 100,000 state residents. | Derived | numeric | Population-adjusted context, not a usage rate. |
| `eligibility_determinations_per_100000_residents` | Eligibility determinations per 100,000 state residents. | Derived | numeric | Population-adjusted context, not a performance score. |
| `determinations_per_application` | Determinations divided by applications. | Derived | numeric | Descriptive same-month ratio; not an approval rate. |
| `application_determination_balance` | Applications submitted minus determinations completed in the same month. | Derived | numeric | Descriptive workflow context; not a backlog metric. |

## Eligibility And Enrollment Context Fields

The file `data/manual/state_demographic_context_candidates.csv` contains standardized context rows from Medicaid.gov State Profiles and related source files. It should be labeled as eligibility and enrollment context in the dashboard.

Important row types include:

- current Medicaid/CHIP enrollment context
- previous-month enrollment context
- month-to-month change context
- change from July-September 2013 baseline where available
- Medicaid expansion status
- marketplace type
- MAGI eligibility thresholds for children, pregnant women, parents, and other adults

Eligibility thresholds describe program rules. They are not observed enrollee demographic shares.

## Fiscal Profile Fields

The file `data/manual/state_expenditure_context_candidates.csv` contains fiscal-year MBES/CBES financial reporting context.

Core rows used for fiscal profile summaries:

- Medicaid Program - Total Net Expenditures
- Medicaid Administration - Total Net Expenditures
- CHIP - Total

Important fields:

| field_name | plain_language_definition | notes |
|---|---|---|
| `fiscal_year` | Federal fiscal year for the expenditure record. | FY2019-FY2024 are used in current review files. |
| `program_category` | Medicaid Program, Medicaid Administration, CHIP, or supplemental categories. | Main fiscal profile uses only the three core categories. |
| `expenditure_category` | Source expenditure category. | Total Net Expenditures or Total for the main summary. |
| `expenditure_amount` | Extracted expenditure amount. | Fiscal-year financial reporting value, not monthly enrollment. |
| `source_file` | MBES/CBES report file used. | Retained for traceability. |

## High-Missingness Or Limited-Interpretability Fields

These source fields should not be used as headline dashboard KPIs without additional validation:

- adult Medicaid enrollment
- call center volume
- call center wait time
- call center abandonment rate
- application processing-time categories
- renewals/redeterminations, because dedicated fields are not available in the selected extract
- pending applications, because dedicated fields are not available in the selected extract

## Reporting Notes

- Preliminary records can change in later CMS releases.
- Updated/final reporting status varies by state and month.
- Public aggregate data support monitoring and context, not causal policy claims.
- Missing values are not fabricated or imputed.
