# State Map Metrics Notes

## Purpose

`outputs/dashboard_tables/state_map_metrics.csv` is a single state-level table for the future Plotly Dash State Map Explorer and selected state profile cards. It combines validated state-level enrollment, eligibility operations, and data quality fields into one row per state/DC.

This file does not add new source data, county-level geography, shapefiles, causal metrics, or unsupported fields.

## Source Tables Used

- `outputs/dashboard_tables/state_latest_snapshot.csv`
- `outputs/dashboard_tables/state_enrollment_change.csv`
- `outputs/dashboard_tables/state_eligibility_operations_summary.csv`
- `outputs/dashboard_tables/data_quality_by_state.csv`

## Fields Included

Identifiers:

- `state_abbreviation`
- `state_name`
- `latest_reporting_month`

Enrollment fields:

- `latest_total_medicaid_chip_enrollment`
- `latest_medicaid_enrollment`
- `latest_chip_enrollment`
- `national_enrollment_rank`
- `change_since_january_2019`
- `percent_change_since_january_2019`
- `last_12_month_change`
- `last_12_month_percent_change`

Eligibility operations fields:

- `latest_applications_submitted`
- `latest_total_determinations`
- `determinations_per_application`
- `applications_per_1000_enrollees`
- `determinations_per_1000_enrollees`

Data quality fields:

- `missingness_percent`
- `missingness_rank`
- `latest_month_preliminary_status`
- `caution_flag`
- `data_quality_note`

Map-ready fields:

- `map_latest_enrollment`
- `map_percent_change_since_2019`
- `map_last_12_month_change`
- `map_applications_per_1000_enrollees`
- `map_determinations_per_1000_enrollees`
- `map_missingness_percent`

## Metric Definitions

- Latest total Medicaid/CHIP enrollment: latest state-level point-in-time total Medicaid/CHIP enrollment.
- Percent change since January 2019: state-level percentage change from January 2019 enrollment to latest enrollment.
- Last 12-month enrollment change: state-level change from the same month 12 months before the latest month.
- Applications per 1,000 enrollees: total applications submitted over the study period, normalized by average monthly enrollment.
- Determinations per 1,000 enrollees: total Medicaid/CHIP determinations over the study period, normalized by average monthly enrollment.
- Missingness percent: percent of preserved state-level data cells missing across the cleaned dashboard fields.

Percent fields are represented on a 0-100 scale, not a 0-1 scale.

## Validation Results

- Expected row count: 51
- Actual row count: 51
- One row per state/DC: Yes
- Duplicate `state_abbreviation` values: 0
- Invalid state abbreviations: 0
- DC included: Yes
- Territories included: No
- `latest_reporting_month` populated for all rows: Yes
- Map metric fields numeric: Yes
- Infinite values from division by zero: 0
- Unexpected negative values: 0

Negative values are allowed for enrollment change metrics because enrollment can decline.

## Safe Choropleth Fields For Version 1

These fields are safe for Version 1 map color selection:

- `map_latest_enrollment`
- `map_percent_change_since_2019`
- `map_last_12_month_change`
- `map_applications_per_1000_enrollees`
- `map_determinations_per_1000_enrollees`
- `map_missingness_percent`

## Fields Not Recommended For Version 1 Mapping

Do not create Version 1 map metrics from:

- adult Medicaid enrollment
- call center volume
- call center wait time
- call center abandonment rate
- application processing-time fields
- renewals/redeterminations
- pending applications

These fields are either high-missingness, unsupported as clean standalone measures, or not available in the preserved source tables.

## Limitations

- The table is state-level only and does not include county-level geography.
- The table does not include shapefiles or GeoJSON.
- The latest reporting month is preliminary for all 50 states plus DC.
- Applications and determinations are descriptive operational indicators, not complete performance measures.
- The table does not support causal policy claims.
- Missingness percentages summarize preserved fields and do not explain why data are missing.
