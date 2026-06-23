# Dashboard User Guide

This guide explains the current Plotly Dash app structure and intended interpretation. The dashboard is a descriptive public-data monitoring tool, not a causal evaluation or beneficiary-level analysis.

## National Snapshot

The National Snapshot summarizes the national Medicaid/CHIP enrollment story from January 2019 through the latest available reporting month.

Use this section to review:

- baseline, observed peak, latest enrollment, and change from reference points
- selected-state vs national indexed enrollment trend
- state map context for enrollment change
- policy/reporting timeline context for interpreting major trend periods

The indexed trend starts the selected state and national trend at 100 in January 2019. This makes trend shape comparable even though raw enrollment counts differ greatly.

## State Comparison Explorer

The State Comparison Explorer is a two-state workflow.

Use this section to:

- choose State A and State B
- view where selected states rank nationally
- compare the selected states on key measures
- review trend-over-time differences
- explore within-state context through profile tabs

Current within-state tabs:

- Enrollment trend
- Eligibility context
- Fiscal profile

Eligibility context uses Medicaid.gov State Profiles enrollment/context fields and MAGI eligibility thresholds. It should not be interpreted as full observed enrollee demographic composition.

Fiscal profile uses MBES/CBES fiscal-year expenditure values. These are financial reporting values, not monthly enrollment values.

## Interpretation Guardrails

- State rankings are descriptive context, not performance ratings.
- Applications and determinations are operations indicators, not approval rates or backlog measures.
- Population-adjusted metrics are comparison context, not healthcare utilization rates.
- Latest-month values may be preliminary.
- The app does not show individual outcomes, claims, utilization, diagnoses, managed care plan performance, or county-level variation.
- The app does not estimate causal effects of policy changes.

## Deployment Notes

The app entry point is `app.py`, and the WSGI server object is `server`.

Cloud start command:

```bash
gunicorn app:server --workers 2 --threads 4 --timeout 120
```
