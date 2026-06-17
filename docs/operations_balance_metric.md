# Application-Determination Balance

## Metric Definition

Application-Determination Balance is a descriptive eligibility operations metric:

```text
Application-Determination Balance = applications submitted - Medicaid/CHIP determinations
```

Population-adjusted version:

```text
Application-Determination Balance per 100,000 residents =
(applications submitted - Medicaid/CHIP determinations) / state population * 100,000
```

## Source Fields Used

- Applications submitted: `total_applications_for_financial_assistance_submitted_at_state_level`
- Medicaid/CHIP determinations: `total_medicaid_and_chip_determinations`
- State population denominator: official Census state resident population estimates in `state_population_denominators.csv`

## Numerator And Denominator

For the raw balance, the numerator is the same-month difference between applications submitted and Medicaid/CHIP determinations. There is no denominator.

For the population-adjusted balance, the numerator is the same balance and the denominator is the state resident population estimate. The multiplier is 100,000 residents.

## Why This Is Useful

This metric helps monitor whether same-month application volume and determination activity are moving together or diverging in the public aggregate data. It can help identify state/month records that may warrant context review alongside source notes, reporting status, and data quality findings.

## Interpretation

A positive balance means applications submitted exceeded same-month Medicaid/CHIP determinations in the public aggregate data. This may warrant context review, but it does not directly measure pending applications, processing delays, approval rates, or state performance.

A negative balance means same-month determinations exceeded applications submitted. This can happen because applications and determinations are monthly flow measures and do not necessarily refer to the same set of individuals or applications.

## What This Metric Is Not

Application-Determination Balance is not:

- a backlog metric
- an approval rate
- a timeliness measure
- a pending workload measure
- a performance score
- a measure of individual-level eligibility outcomes

Pending applications are not available in the preserved source fields, so this metric cannot measure backlog or delays.

## Limitations Of Monthly Flow Measures

Applications and determinations are monthly aggregate flow measures. They may reflect different cohorts, reporting systems, administrative timing, transfers, and eligibility pathways. A determination in one month may relate to an application submitted in an earlier month.

Because of those limits, this metric should be interpreted as a descriptive monitoring indicator only. It should be shown with plain-language caveats and should not be used to rank state performance.

## Dashboard Use

In the dashboard, this metric should appear in eligibility operations views as a context indicator. Recommended labels:

- Application-Determination Balance
- Balance per 100,000 residents
- Descriptive operations indicator
- Warrants context review

Avoid labels such as backlog, delay, failure, bad performance, or problem state.
