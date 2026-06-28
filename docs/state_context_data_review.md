# State Context Data Review

## Purpose

This document reviews standardized official-source context data prepared for the Medicaid/CHIP enrollment divergence after unwinding project. The goal is to support a future Section 3 design that is more data-driven and less dependent on custom state policy blurbs.

No dashboard code, callbacks, layout, CSS, or data pipeline files were changed for this review step.

## Official Sources Used

1. [Medicaid.gov State Profiles](https://www.medicaid.gov/state-overviews/state-profiles)
   - State enrollment/profile JSON: [https://www.medicaid.gov/sites/default/files/2026-05/May2026-enrollment-by-state888_4.json](https://www.medicaid.gov/sites/default/files/2026-05/May2026-enrollment-by-state888_4.json)
   - MAGI Medicaid/CHIP income eligibility JSON: [https://www.medicaid.gov/sites/default/files/2024-12/dec-2023-medicaid-income-eligibility888-updated.json](https://www.medicaid.gov/sites/default/files/2024-12/dec-2023-medicaid-income-eligibility888-updated.json)

2. [Medicaid.gov MBES/CBES Expenditure Reports](https://www.medicaid.gov/medicaid/financial-management/state-budget-expenditure-reporting-for-medicaid-and-chip/expenditure-reports-mbes/cbes)
   - Annual Financial Management Report zip files for FY 2019 through FY 2024.
   - Extracted standardized state-level total rows from CMS-64/CMS-21-style worksheets for Medicaid Program, Medicaid Administration, and CHIP.

## Review Files Created

- `data/manual/state_demographic_context_candidates.csv`
- `data/manual/state_expenditure_context_candidates.csv`
- `data/raw/medicaid_expenditure_download_log.csv`

All review rows are marked `review_status = needs_review`.

## State Coverage

- Demographic/enrollment/eligibility context states covered: 51 state/DC units.
- Expenditure context states covered: 51 state/DC units.
- Missing demographic context states: None.
- Missing expenditure context states: None.

Territories and national total sheets were excluded so the review files align with the dashboard's 50 states plus DC scope.

## Demographic and Enrollee Context Availability

The Medicaid.gov State Profiles source provides standardized state-level enrollment/profile context, but it does **not** provide a full state-by-state enrollee demographic distribution in the files reviewed here. The child-enrollment JSON linked from the State Profile page appeared to contain national child-enrollment summary fields rather than state-by-state child rows, so it was not used to create state rows.

Fields captured in `state_demographic_context_candidates.csv` include:

- Current and previous total Medicaid/CHIP enrollment from the May 2026 State Profile release.
- Month-to-month enrollment percent change.
- Pre-open-enrollment monthly average enrollment from July-September 2013 and change from that historical baseline.
- Marketplace type and Medicaid expansion flag.
- MAGI income eligibility limits or source notes for children, separate CHIP, pregnant women, parents, and other adults.

Category counts in the review file:

| demographic_category | rows |
|---|---:|
| eligibility_income_limit | 408 |
| enrollment_context | 306 |
| marketplace_context | 51 |
| structural_context | 51 |


Eligibility rows are useful for **benefits population / eligibility context**, but they should not be described as observed enrollee demographics. They identify state eligibility thresholds or source notes, not counts of enrolled children, adults, aged, blind/disabled, dual eligible beneficiaries, or expansion adults.

## Expenditure Fields Available

The MBES/CBES Financial Management Report workbooks were successfully downloaded and parsed for FY 2019-FY 2024. The final review file intentionally keeps standardized summary rows rather than all detailed service-category rows so the candidate dataset remains reviewable and lightweight.

Extracted fields include:

- Fiscal year.
- State and state abbreviation.
- Program category: CHIP, Medicaid Administration, Medicaid Program.
- Expenditure category from standardized total rows.
- Total computable expenditure.
- Federal share.
- State share.
- Source file and source URL.

Rows retained by program category:

| program_category | rows |
|---|---:|
| CHIP | 306 |
| Medicaid Administration | 306 |
| Medicaid Program | 1989 |

Rows retained by expenditure category:

| program_category | expenditure_category | rows |
|---|---|---:|
| CHIP | Total | 306 |
| Medicaid Administration | Total Net Expenditures | 306 |
| Medicaid Program | Total COVID19 Expenditures Sec 6004 and 6008 | 255 |
| Medicaid Program | Total COVID19 Section 6004 | 255 |
| Medicaid Program | Total COVID19 Section 6008 | 255 |
| Medicaid Program | Total Net Expenditures | 306 |
| Medicaid Program | Total Newly Eligible | 306 |
| Medicaid Program | Total Not Newly | 306 |
| Medicaid Program | Total VIII Group | 306 |


The raw official workbooks contain more detailed service categories. Those raw files are retained under `data/raw/standardized_context_sources/mbes_cbes/` for review, but the candidate CSV focuses on top-line categories likely to support dashboard context.

## Fiscal Years Covered

Fiscal years covered in the expenditure review file: 2019, 2020, 2021, 2022, 2023, 2024.

## Major Data Caveats

- MBES/CBES values are fiscal-year financial reporting values, not monthly enrollment values.
- These expenditure values should not be directly compared to monthly enrollment without clear time-basis labeling.
- CMS notes that expenditures are reported based on the date of payment rather than the date of service.
- Prior-period adjustments may alter reported values.
- Program/service categories differ from monthly enrollment dashboard measures and should be presented as contextual financial reporting information.
- The State Profiles data reviewed here do not provide complete state-level demographic enrollee distributions. Do not invent age, disability, dual-eligible, or expansion-adult shares without a source-backed file.

## Readiness for App Implementation

Status: **review-ready, not app-ready until approved**.

The files are suitable for review because they use standardized CMS/Medicaid.gov sources and cover all 50 states plus DC. Before adding to the app, review should confirm:

- Which State Profile fields should appear in a future Benefits Population tab.
- Whether eligibility limits should be framed as eligibility context rather than demographic composition.
- Which MBES/CBES expenditure totals should be used for a clean Expenditure Context tab.
- Whether supplemental rows such as `Total VIII Group`, `Total Newly Eligible`, or COVID-related totals should be shown by default or kept as optional context.

## Recommended Section 3 Direction

A future app update could shift Section 3 toward these data-driven tabs:

1. **Enrollment history**: existing monthly enrollment heatmap.
2. **Benefits population / eligibility context**: State Profile enrollment totals, Medicaid expansion flag, marketplace type, and MAGI eligibility thresholds. Use cautious labels because these are not full enrollee demographic distributions.
3. **Expenditure context**: fiscal-year Medicaid Program, Medicaid Administration, and CHIP expenditure summaries from MBES/CBES. Label fiscal year clearly and separate expenditure context from monthly enrollment trends.
4. **Policy context**: optional later tab only for reviewed, approved state-specific policy facts.

## Extraction Notes

The expenditure extraction first inspected the official detailed worksheets, then retained standardized total rows for the review CSV. This keeps the candidate file practical for review while preserving source traceability through `source_file`, `source_url`, and the raw downloaded MBES/CBES workbooks.
