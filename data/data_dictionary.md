# Data Dictionary

This data dictionary describes fields preserved in the cleaned 2019-present state-month dataset created from the official CMS/Data.Medicaid.gov State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data source.

| field_name | plain_language_definition | source_field_name | data_type | notes |
|---|---|---|---|---|
| state_abbreviation | Two-letter state or DC abbreviation. | State Abbreviation | string | Includes all 50 states plus DC. |
| state_name | Full state or DC name. | State Name | string | Standardized by trimming whitespace. |
| reporting_period | Source reporting period in YYYYMM format. | Reporting Period | integer | Retained from source for traceability. |
| reporting_month | Month-start date parsed from reporting period. | Reporting Period | date | Used for monthly trend analysis. |
| reporting_year | Calendar year derived from reporting month. | Reporting Period | integer | Derived field for filtering and grouping. |
| state_expanded_medicaid | Whether the state had expanded Medicaid as of the reporting period. | State Expanded Medicaid | string | Source uses Y/N values. |
| preliminary_or_updated | Whether the source record is preliminary or updated. | Preliminary or Updated | string | Source uses P for preliminary and U for updated. |
| final_report | Whether the source record is final. | Final Report | string | Source uses Y/N. Cleaning prefers final/updated records when duplicates exist. |
| new_applications_submitted_to_medicaid_and_chip_agencies | Applications received by Medicaid and CHIP agencies during the month, excluding FFM transfers. | New Applications Submitted to Medicaid and CHIP Agencies | numeric | Application volume measure. |
| applications_for_financial_assistance_submitted_to_the_state_based_marketplace | Applications requesting financial assistance received by a State-Based Marketplace during the month. | Applications for Financial Assistance Submitted to the State Based Marketplace | numeric | May be zero or not applicable for some states/months. |
| total_applications_for_financial_assistance_submitted_at_state_level | Total state-level applications for financial assistance received by Medicaid, CHIP, and State-Based Marketplace agencies where applicable. | Total Applications for Financial Assistance Submitted at State Level | numeric | Application volume measure. |
| individuals_determined_eligible_for_medicaid_at_application | Individuals determined eligible for Medicaid at application during the month. | Individuals Determined Eligible for Medicaid at Application | numeric | Eligibility operations measure. |
| individuals_determined_eligible_for_chip_at_application | Individuals determined eligible for CHIP at application during the month. | Individuals Determined Eligible for CHIP at Application | numeric | Eligibility operations measure. |
| total_medicaid_and_chip_determinations | Total Medicaid and CHIP eligible determinations at application during the month. | Total Medicaid and CHIP Determinations | numeric | Sum of Medicaid and CHIP determinations in the source. |
| medicaid_and_chip_child_enrollment | Point-in-time child Medicaid plus CHIP enrollment count at month end. | Medicaid and CHIP Child Enrollment | numeric | CHIP may include adults in some states, so this is not strictly children in every state. |
| total_medicaid_and_chip_enrollment | Point-in-time total Medicaid or CHIP enrollment at month end. | Total Medicaid and CHIP Enrollment | numeric | Core enrollment trend measure. |
| total_medicaid_enrollment | Point-in-time total Medicaid enrollment at month end. | Total Medicaid Enrollment | numeric | Core enrollment trend measure. |
| total_chip_enrollment | Point-in-time total CHIP enrollment at month end. | Total CHIP Enrollment | numeric | CHIP may include adults in some states. |
| total_adult_medicaid_enrollment | Point-in-time adult Medicaid enrollment at month end. | Total Adult Medicaid Enrollment | numeric | Substantial missingness; use with caution. |
| total_medicaid_and_chip_determinations_processed_in_less_than_24_hours | MAGI application determinations processed in less than 24 hours. | Total Medicaid and CHIP Determinations Processed in Less than 24 Hours | numeric | Processing-time field; substantial missingness. |
| total_medicaid_and_chip_determinations_processed_between_24_hours_and_7_days | MAGI application determinations processed between 24 hours and 7 days. | Total Medicaid and CHIP Determinations Processed Between 24 Hours and 7 Days | numeric | Processing-time field; substantial missingness. |
| total_medicaid_and_chip_determinations_processed_between_8_days_and_30_days | MAGI application determinations processed between 8 and 30 days. | Total Medicaid and CHIP Determinations Processed Between 8 Days and 30 Days | numeric | Processing-time field; substantial missingness. |
| total_medicaid_and_chip_determinations_processed_between_31_days_and_45_days | MAGI application determinations processed between 31 and 45 days. | Total Medicaid and CHIP Determinations Processed between 31 days and 45 days | numeric | Processing-time field; substantial missingness. |
| total_medicaid_and_chip_determinations_processed_in_more_than_45_days | MAGI application determinations processed in more than 45 days. | Total Medicaid and CHIP Determinations Processed in More than 45 Days | numeric | Processing-time field; substantial missingness. |
| total_call_center_volume_number_of_calls | Total calls received by Medicaid/CHIP-serving call centers or hotlines. | Total Call Center Volume (Number of Calls) | numeric | Substantial missingness; call centers may serve other state human services programs. |
| average_call_center_wait_time_minutes | Average call center wait time in whole minutes. | Average Call Center Wait Time (Minutes) | numeric | Substantial missingness; rounded according to source rules. |
| average_call_center_abandonment_rate | Average call center abandonment rate. | Average Call Center Abandonment Rate | numeric | Substantial missingness; source-defined ratio. |
