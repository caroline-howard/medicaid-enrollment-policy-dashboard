# Diagnostic Monitoring Plan

This plan describes descriptive indicators used to monitor Medicaid/CHIP enrollment, eligibility operations, population context, and source quality. The project uses neutral review flags to identify state/month records that may warrant follow-up review. Review flags are not problem labels, performance scores, or causal findings.

## A. Enrollment Change Indicators

- Change since January 2019
- Percent change since January 2019
- Last 12-month change
- Last 12-month percent change
- Change from state peak enrollment to latest month
- Percent change from state peak enrollment to latest month

These indicators help compare longer-run and recent enrollment movement. They do not explain why enrollment changed.

## B. Population-Adjusted Context

- Total Medicaid/CHIP enrollment per 1,000 residents
- Medicaid enrollment per 1,000 residents
- CHIP enrollment per 1,000 residents
- Applications submitted per 100,000 residents
- Eligibility determinations per 100,000 residents

Population-adjusted measures provide descriptive state-size context. They should not be called usage rates and do not measure healthcare utilization.

## C. Eligibility Operations Indicators

- Applications submitted
- Total Medicaid/CHIP determinations
- Determinations per application
- Applications per 1,000 enrollees
- Determinations per 1,000 enrollees
- Application-Determination Balance
- Application-Determination Balance per 100,000 residents

These are descriptive operational indicators, not performance scores. Applications and determinations are monthly flow measures and should be interpreted alongside enrollment, reporting status, and source limitations.

Application-Determination Balance compares same-month applications submitted with Medicaid/CHIP determinations. It is useful for monitoring divergence between application volume and determination activity, but it is not a backlog metric, approval rate, timeliness measure, or state performance score.

## D. Review Flags, Not Problem Labels

The monitoring workflow creates neutral review flags for records that may warrant closer review:

- Large month-over-month enrollment change
- Large applications spike compared with recent state average
- Large determinations spike compared with recent state average
- Latest-month preliminary reporting caution
- High missingness caution

The workflow uses "review flag" or "monitoring flag" language. It does not label states as failures, bad performers, or problems.

## Flag Logic

- Enrollment month-over-month review flag: absolute monthly enrollment change is greater than two standard deviations from that state’s average monthly change.
- Applications review flag: monthly applications submitted are greater than two standard deviations above the previous 12-month state average, requiring at least six prior observations.
- Determinations review flag: monthly determinations are greater than two standard deviations above the previous 12-month state average, requiring at least six prior observations.
- Latest-month preliminary reporting caution: latest state/month record is not marked final.
- High missingness caution: state missingness is greater than 10 percent in the dashboard-ready state quality summary.

If a metric cannot be calculated because there are too few observations or missing values, the workflow does not force a flag.

## Forecasting Extension, Deferred

Forecasting could be added later for short-term operational planning. Good exploratory targets would include national enrollment, selected-state enrollment, applications, and determinations.

Forecasts should be exploratory only. They should not be used for budget, eligibility, utilization, or causal policy claims without additional validation, governance, and domain review.
