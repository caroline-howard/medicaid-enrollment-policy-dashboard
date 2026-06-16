# Population Denominator Notes

## Source

- Source name: U.S. Census Bureau Annual Estimates of the Resident Population for the United States, Regions, States, District of Columbia, and Puerto Rico: April 1, 2020 to July 1, 2024 (NST-EST2024-POP)
- Source URL: https://www2.census.gov/programs-surveys/popest/tables/2020-2024/state/totals/NST-EST2024-POP.xlsx
- Date accessed: 2026-06-16
- Population years available in processed file: 2020, 2021, 2022, 2023, 2024
- Latest denominator year used for Version 1 dashboard metrics: 2024

## Processing Logic

The source workbook is downloaded to `data/raw/`, which is excluded from Git. The script `src/load_population_data.py` parses the official Census workbook and writes `data/processed/state_population_denominators.csv`.

The script `src/build_population_adjusted_metrics.py` merges the latest available state population denominator to `outputs/dashboard_tables/state_map_metrics.csv` by `state_abbreviation`. Because the Medicaid dashboard source currently runs through February 2026 and exact 2026 state population estimates are not available in this Census workbook, Version 1 uses the latest available 2024 state resident population estimate and flags the denominator year.

## Fields Created

- `state_population`
- `population_denominator_year`
- `medicaid_chip_enrollment_per_1000_residents`
- `medicaid_enrollment_per_1000_residents`
- `chip_enrollment_per_1000_residents`
- `applications_submitted_per_100000_residents`
- `eligibility_determinations_per_100000_residents`

## Limitations

Population-adjusted enrollment metrics are descriptive context only. They should be described as enrollment relative to state population or enrollment per 1,000 residents. They are not healthcare utilization measures and should not be called usage rates.

Population denominators are annual state-level estimates, while Medicaid enrollment is monthly state-level aggregate reporting. The denominator year may not match the Medicaid reporting year exactly, especially for 2025 and 2026 Medicaid months.

These metrics do not control for state demographics, eligibility rules, program design, economic conditions, immigration rules, or reporting practices. They support descriptive comparison, not causal policy impact claims.
