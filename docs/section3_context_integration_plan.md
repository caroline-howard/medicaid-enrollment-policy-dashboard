# Section 3 Context Integration Plan

## Purpose

This plan describes how the reviewed context CSVs could be integrated into Section 3 of the Medicaid Enrollment & Eligibility Operations Dashboard. This is an app-integration plan only. No dashboard app code should be updated until the data and wording are approved.

## Source Files Reviewed

| File | Rows | State/DC coverage | Review status |
|---|---:|---:|---|
| `data/manual/state_demographic_context_candidates.csv` | 816 | 51 | all `needs_review` |
| `data/manual/state_expenditure_context_candidates.csv` | 2,601 | 51 | all `needs_review` |
| `data/manual/state_policy_context_candidates.csv` | 269 | 51 | all `needs_review` |

## Important Interpretation Rules

- `state_demographic_context_candidates.csv` should **not** be labeled as true demographics in the app. It contains enrollment/profile context and MAGI eligibility thresholds, not full enrollee demographic distributions.
- The app tab using that file should be labeled **Eligibility & enrollment context**.
- `state_expenditure_context_candidates.csv` contains fiscal-year MBES/CBES financial reporting values. It should be clearly labeled as fiscal-year expenditure context, not monthly enrollment data.
- `state_policy_context_candidates.csv` should remain review-only until rows have `app_candidate = yes`, `approval_recommendation = approve_candidate`, and `review_status = approved`.

## Recommended Section 3 Tabs

1. Enrollment history
2. Eligibility & enrollment context
3. Operations & program mix
4. Expenditure context
5. Policy context

## Tab 1: Enrollment History

### Data File Used

- Existing processed/dashboard enrollment data already used by the app.

### Fields Required

- `state_abbreviation` or equivalent state key
- `state_name`
- `reporting_month`
- `total_medicaid_chip_enrollment`
- Peak month/value fields if already available
- Selected reporting month from the app state

### Filtering Logic for State A and State B

- Filter the monthly enrollment table to `state_abbreviation == state_a`.
- Filter the monthly enrollment table to `state_abbreviation == state_b`.
- Use the selected month only for highlighting the reporting month cell; the heatmap should continue to show the full available monthly history.

### Visual Layout

- Keep the current raw monthly enrollment heatmaps.
- Show State A and State B side by side.
- Each heatmap should use raw monthly Medicaid/CHIP enrollment counts, not indexed values.
- The heatmap should fill most of each state card.
- Keep only compact summary values above the heatmap: selected-month enrollment, January 2019 baseline enrollment, and observed peak enrollment.
- Use a state-specific low-to-high legend because raw enrollment scales differ substantially across states.

### Caveat Text

“Monthly enrollment values are public aggregate state-level counts. They do not show beneficiary-level records, utilization, cost, or reasons for enrollment change.”

### Readiness

Ready for implementation using existing dashboard data, subject to final visual QA.

## Tab 2: Eligibility & Enrollment Context

### Data File Used

- `data/manual/state_demographic_context_candidates.csv`

### Fields Required

Common keys:

- `state`
- `state_abbr`
- `reporting_period`
- `demographic_category`
- `demographic_subcategory`
- `value`
- `value_type`
- `denominator`
- `notes`
- `review_status`

Enrollment/profile context fields:

- `total_medicaid_chip_enrollment_current_month`
- `total_medicaid_chip_enrollment_previous_month`
- `month_to_month_percent_change`
- `pre_open_enrollment_monthly_average_july_sept_2013`
- `net_change_pre_open_enrollment_to_current_month`
- `percent_change_pre_open_enrollment_to_current_month`
- `medicaid_expansion_status`
- `marketplace_type`

MAGI eligibility threshold fields:

- `children_medicaid_ages_0_1`
- `children_medicaid_ages_1_5`
- `children_medicaid_ages_6_18`
- `separate_chip`
- `pregnant_women_medicaid`
- `pregnant_women_chip`
- `parents`
- `other_adults`

### Filtering Logic for State A and State B

- Filter to `state_abbr in [state_a, state_b]`.
- Keep rows with `review_status = needs_review` out of the production app until approved, or show only in a development/review build.
- Pivot rows by `demographic_subcategory` so each selected state has one enrollment/profile object and one eligibility-threshold object.
- Preserve `reporting_period` by source because enrollment/profile fields and eligibility thresholds use different reporting periods.

### Visual Layout

- State A and State B side by side.
- Top metric cards for enrollment/profile context:
  - current Medicaid/CHIP enrollment
  - previous month enrollment
  - month-to-month percent change
  - change from July-September 2013 baseline
  - Medicaid expansion status
  - marketplace type
- Below the metric cards, show a compact MAGI eligibility-threshold table or horizontal bars.
- Keep labels plain, for example “Children 0-1”, “Children 1-5”, “Children 6-18”, “Pregnant women”, “Parents”, and “Other adults”.

### Caveat Text

“Eligibility thresholds are policy context, not observed enrollee demographic shares.”

Additional note:

“This tab uses Medicaid.gov State Profile context and MAGI eligibility thresholds. It does not provide full state-level enrollee demographic distributions by age, disability, dual eligibility, or eligibility group.”

### Readiness

Partially ready. The structure is standardized for all 51 state/DC units, but app implementation should wait for review approval and final naming decisions because the source file is not true demographic composition.

## Tab 3: Operations & Program Mix

### Data File Used

- Existing dashboard data already used by the app.

### Fields Required

- `state_abbreviation`
- `state_name`
- `reporting_month`
- `applications_submitted`
- `eligibility_determinations`
- `application_determination_balance`
- `determination_coverage_rate`
- `medicaid_enrollment`
- `chip_enrollment`
- `total_medicaid_chip_enrollment`
- Medicaid share
- CHIP share
- Population denominator year, if already available

### Filtering Logic for State A and State B

- Filter the selected-month state table to State A and State B.
- Use the month selected for the direct comparison workflow.
- Calculate Medicaid share and CHIP share from already-validated dashboard fields.

### Visual Layout

- State A and State B side by side.
- Compact operations flow:
  - “Applications submitted -> Determinations completed”
  - selected-month applications
  - selected-month determinations
  - application-determination balance
  - determination coverage rate
- Compact program mix block:
  - thin 100% stacked bar
  - Medicaid share
  - CHIP share
  - population denominator year

### Caveat Text

“Applications and determinations are descriptive operations indicators. They are not approval rates, timeliness measures, or complete performance scores.”

### Readiness

Ready for implementation using existing dashboard data, subject to final visual QA.

## Tab 4: Expenditure Context

### Data File Used

- `data/manual/state_expenditure_context_candidates.csv`

### Fields Required

- `state`
- `state_abbr`
- `fiscal_year`
- `program_category`
- `expenditure_category`
- `expenditure_amount`
- `federal_share`
- `state_share`
- `total_computable_expenditure`
- `source_file`
- `source_url`
- `source_type`
- `notes`
- `review_status`

Primary expenditure rows:

- `program_category = Medicaid Program`, `expenditure_category = Total Net Expenditures`
- `program_category = Medicaid Administration`, `expenditure_category = Total Net Expenditures`
- `program_category = CHIP`, `expenditure_category = Total`

Optional supplemental rows:

- `Total Newly Eligible`
- `Total VIII Group`
- `Total COVID19 Section 6004`
- `Total COVID19 Section 6008`
- `Total COVID19 Expenditures Sec 6004 and 6008`

### Filtering Logic for State A and State B

- Filter to `state_abbr in [state_a, state_b]`.
- Filter fiscal years to FY 2019-FY 2024.
- For default view, keep only the primary expenditure rows listed above.
- Put optional supplemental rows behind a selector or disclosure control.
- Keep `review_status = needs_review` out of the production app until approved, or show only in a development/review build.

### Visual Layout

- State A and State B side by side or in a shared two-state trend panel.
- Show fiscal-year trend from FY 2019 to FY 2024.
- Default series:
  - Medicaid Program Total Net Expenditures
  - Medicaid Administration Total Net Expenditures
  - CHIP Total
- Optional toggle:
  - federal share vs state share
  - supplemental rows for newly eligible, VIII group, and COVID expenditure totals
- Use dollars with compact formatting and clear fiscal-year labels.

### Caveat Text

“Expenditure values are fiscal-year financial reporting values from MBES/CBES, not monthly enrollment values.”

Additional note:

“States may report expenditures based on date of payment rather than date of service, and prior-period adjustments may change reported values.”

### Readiness

Partially ready. The file is standardized and covers all states/DC for FY 2019-FY 2024, but implementation should wait for review approval and a decision on whether to show only top-line totals or optional supplemental rows.

## Tab 5: Policy Context

### Data File Used

- `data/manual/state_policy_context_candidates.csv`

### Fields Required

- `state`
- `state_abbr`
- `event_title`
- `event_start_date`
- `event_end_date`
- `event_type`
- `summary`
- `dashboard_relevance`
- `source_name`
- `source_url`
- `confidence`
- `proposed_blurb`
- `review_status`
- `context_priority`
- `state_specificity`
- `verification_status`
- `app_candidate`
- `approval_recommendation`

### Filtering Logic for State A and State B

Production filter:

- `state_abbr in [state_a, state_b]`
- `app_candidate = yes`
- `approval_recommendation = approve_candidate`
- `review_status = approved`

Current review-only behavior:

- Because all current rows have `review_status = needs_review`, the app should not display any proposed policy blurbs yet.

### Visual Layout

- State A and State B side by side.
- If an approved row exists for a state, show:
  - short state-specific policy blurb
  - event title
  - date or period
  - source link
  - confidence label only if useful
- If no approved row exists:
  - “Policy context pending review for this state.”
- If no approved rows exist for either selected state:
  - “Policy context pending review.”

### Caveat Text

“Policy context is source-reviewed narrative context. It should be interpreted alongside dashboard metrics and should not be read as a causal explanation of enrollment changes.”

### Readiness

Not ready for app implementation. The file has 13 rows marked `app_candidate = yes` and `approval_recommendation = approve_candidate`, but all policy rows are still `review_status = needs_review`. This tab should remain placeholder-only until facts and blurbs are approved.

## Cross-Tab Implementation Notes

- Keep Section 3 state cards mirrored for State A and State B.
- Do not merge monthly enrollment, eligibility thresholds, fiscal-year expenditures, and policy blurbs into one crowded overview card.
- Use the selected State A and State B values as the shared state filters across all Section 3 tabs.
- Use the selected month only where the underlying data are monthly. Do not use selected month to filter fiscal-year expenditure context.
- Use fiscal-year controls or latest fiscal year labels for expenditure views.
- Keep source/caveat notes visible but compact.
- Preserve reviewed source URLs in hover, expandable detail, or source-note areas.

## Recommended Implementation Sequence

1. Keep the current Enrollment history tab as the default Section 3 view.
2. Add Eligibility & enrollment context after review approval of field names and caveat wording.
3. Add Expenditure context after deciding the default expenditure rows and whether supplemental rows should be behind a selector.
4. Keep Operations & program mix on existing validated dashboard data.
5. Keep Policy context as a placeholder until selected rows are approved.

## Overall Readiness

| Tab | Ready status | Reason |
|---|---|---|
| Enrollment history | Ready | Uses existing validated monthly enrollment data. |
| Eligibility & enrollment context | Partial | Standardized file exists, but it needs approval and careful labeling because it is not true demographics. |
| Operations & program mix | Ready | Uses existing validated dashboard data. |
| Expenditure context | Partial | Standardized file exists, but app-ready rollup choices need approval. |
| Policy context | Not ready | Rows are review-only until `review_status = approved`. |

