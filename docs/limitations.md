# Limitations

This project uses official public aggregate Medicaid/CHIP reporting data. It is designed for descriptive monitoring, source-aware reporting, and portfolio demonstration. It should not be interpreted as beneficiary-level analysis, operational performance auditing, or causal policy evaluation.

## Public Aggregate Data Limitations

The dashboard uses state-level monthly aggregate records. It does not include individual enrollment spells, household characteristics, county-level geography, claims, utilization, diagnoses, provider access, managed care plan data, service use, spending outcomes, or individual coverage transitions.

Because the data are aggregate, the dashboard can show patterns such as enrollment levels, Medicaid vs CHIP composition, application volume, and eligibility determination counts. It cannot show why an individual gained or lost coverage.

## Preliminary And Updated Reporting

CMS monthly records can be preliminary, updated, or final. Preliminary months are useful for recent monitoring, but values may change in later releases. The dashboard should be interpreted with reporting status and source notes in mind, especially for the latest available month.

## Missingness

Core enrollment fields are generally more complete than operational detail fields. Applications and determinations support descriptive operations monitoring, but call center, processing-time, adult enrollment, and other supplemental fields can have high missingness or inconsistent availability.

Fields with high missingness should not be used as headline performance metrics. Missing values are not imputed.

## State Reporting Variation

States administer Medicaid and CHIP within federal rules, but eligibility rules, CHIP program design, reporting practices, administrative systems, renewal processes, and marketplace structures vary. State comparisons should be interpreted as descriptive comparisons, not rankings of program quality.

## Applications And Determinations

Applications submitted and eligibility determinations are operations indicators. They are not approval rates, backlog measures, complete workload measures, timeliness measures, or performance scores. Same-month applications and determinations do not necessarily refer to the same people or cases.

## Population-Adjusted Metrics

Population-adjusted measures, such as enrollment per 1,000 residents or applications per 100,000 residents, provide scale context across states. They should not be described as utilization or usage rates. They use state population denominators and do not adjust for eligibility, income distribution, age structure, immigration rules, or state policy differences.

## Fiscal-Year Expenditure Context

MBES/CBES expenditure values are fiscal-year financial reporting values. They are not monthly enrollment values and should not be directly compared to a single reporting month without clearly labeling the different time basis.

Expenditure reporting can include payment-basis timing and prior-period adjustments. The fiscal profile is context for financial scale and program categories, not a cost-per-beneficiary analysis.

## Non-Causal Framing

The dashboard does not estimate causal effects of Medicaid expansion, unwinding, waiver policy, CHIP structure, or administrative changes. Policy context is included to help users interpret timing and variation, not to claim that a policy caused a specific enrollment change.

Appropriate wording:

- "may help contextualize"
- "coincided with"
- "should be interpreted alongside"
- "descriptive monitoring"

Avoid wording that implies causal estimates, program performance scores, or beneficiary outcomes.
