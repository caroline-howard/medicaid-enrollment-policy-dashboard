# Policy Context

This project uses official public Medicaid/CHIP state-month aggregate data for descriptive monitoring. The dashboard should be read as a source-aware reporting tool, not a causal policy evaluation.

## Policy Context For Interpreting Enrollment Trends

Dashboard metrics and visuals are based on CMS/Data.Medicaid.gov Medicaid and CHIP enrollment and eligibility operations data. The sources below are used only for policy interpretation context; they are not KPI metric sources.

### A. Medicaid Scale And State Variation

KFF describes Medicaid as a major public coverage program and emphasizes its role for children, low-income adults, people with disabilities, and people needing long-term services and supports. KFF also notes that Medicaid is administered by states within federal rules, which is why eligibility rules, administrative processes, delivery systems, and reporting practices can differ across states.

This context matters for the dashboard because a state-vs-national indexed trend can show how one state's enrollment moved relative to the national pattern, but it cannot explain by itself why the state differs.

Source:

- [KFF: 10 Things to Know About Medicaid](https://www.kff.org/medicaid/10-things-to-know-about-medicaid/)

### B. Medicaid Unwinding, Churn, And Net Enrollment Change

McIntyre et al. (2025), "US Coverage Changes During Medicaid Unwinding in 2023," in *JAMA Health Forum*, provides context for interpreting enrollment declines after the observed enrollment peak. The article is useful here because it distinguishes between administrative terminations and net enrollment change. Those concepts are not the same: net enrollment change can differ from total terminations because people may re-enroll, experience churn, or transition to other forms of coverage.

The dashboard does not directly measure churn, uninsured status, coverage transitions, or reasons for disenrollment. It can show aggregate enrollment change over time and state variation, but additional data and a separate research design would be needed to evaluate coverage transitions or causal effects.

Source:

- McIntyre et al. (2025), "US Coverage Changes During Medicaid Unwinding in 2023," *JAMA Health Forum*.

### C. CHIP And Children's Coverage Context

MACPAC describes Medicaid and CHIP as important coverage sources for low-income children and children with disabilities. This context helps explain why the dashboard shows combined Medicaid/CHIP enrollment and also separates Medicaid and CHIP components.

Enrollment data alone cannot show whether children accessed medical care, dental care, prescriptions, or other services. The dashboard should not be interpreted as measuring children's access, healthcare utilization, service quality, or health outcomes.

Source:

- [MACPAC: Access in Brief: Children's Experiences in Accessing Medical Care](https://www.macpac.gov/wp-content/uploads/2025/04/Access-in-Brief-Childrens-Experiences-in-Accessing-Medical-Care.pdf)

### D. What The Dashboard Can And Cannot Show

Can show:

- aggregate Medicaid/CHIP enrollment trends
- state-level variation
- selected state vs national indexed trends
- Medicaid vs CHIP component patterns
- applications and eligibility determinations
- population-adjusted context
- reporting and data quality caveats

Cannot show:

- individual coverage transitions
- uninsured status
- churn directly
- access to care
- healthcare utilization
- claims
- costs
- diagnoses
- health outcomes
- causal policy effects

## 1. Medicaid And CHIP Basics

Medicaid and the Children's Health Insurance Program (CHIP) are state-federal coverage programs. They are funded by states and the federal government, and states administer the programs within federal requirements.

CHIP provides coverage for eligible children through Medicaid and separate CHIP programs. Medicaid.gov describes CHIP as covering eligible children in families with incomes too high to qualify for Medicaid but too low to afford private coverage. CHIP is managed by states according to federal requirements, which means CHIP program structure and reporting can vary by state.

Sources:

- [Medicaid.gov: Children's Health Insurance Program (CHIP)](https://www.medicaid.gov/chip)
- [Medicaid.gov: Medicaid and CHIP Enrollment Data](https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-chip-enrollment-data)

## 2. State Variation

States administer Medicaid and CHIP within federal rules, but eligibility rules, program structure, reporting practices, waiver choices, IT systems, and administrative processes vary by state. Medicaid.gov notes that federal law requires coverage of certain mandatory eligibility groups and allows states to cover additional optional groups.

Because of this variation, state comparisons should be interpreted as descriptive context. Differences across states may reflect policy design, eligibility pathways, economic conditions, administrative operations, reporting practices, or population size.

Sources:

- [Medicaid.gov: Eligibility Policy](https://www.medicaid.gov/medicaid/eligibility-policy)
- [Medicaid.gov: State Overviews](https://www.medicaid.gov/state-overviews)

## 3. Eligibility And MAGI

Modified Adjusted Gross Income (MAGI) is used to determine financial eligibility for Medicaid, CHIP, and Marketplace premium tax credits and cost-sharing reductions for many applicants. Medicaid.gov explains that MAGI applies to most children, pregnant women, parents, and adults, while some groups, including people whose eligibility is based on age, blindness, or disability, are exempt from MAGI-based rules.

Applications and determinations in the dashboard may reflect different eligibility pathways, state systems, and administrative workflows. They should be treated as descriptive operations indicators, not complete measures of eligibility performance.

Source:

- [Medicaid.gov: Eligibility Policy](https://www.medicaid.gov/medicaid/eligibility-policy)

## 4. Medicaid Expansion Context

Medicaid expansion status can affect enrollment levels and population-adjusted comparisons. KFF tracks state Medicaid expansion decisions and reports that the ACA Medicaid expansion covers nearly all adults with incomes up to 138 percent of the Federal Poverty Level in states that have adopted expansion.

The dashboard can show expansion status as context if an official or reputable state expansion source is added later. It should not claim that expansion caused a specific enrollment pattern without a separate causal research design.

Source:

- [KFF: Status of State Medicaid Expansion Decisions](https://www.kff.org/medicaid/status-of-state-medicaid-expansion-decisions/)

## 5. COVID Continuous Enrollment And Unwinding Context

Pandemic-era Medicaid continuous enrollment affected enrollment trends. KFF explains that during the continuous enrollment period, states paused Medicaid disenrollments. KFF also notes that when the continuous enrollment provision ended in March 2023, national Medicaid/CHIP enrollment had reached a record high.

States resumed renewals and disenrollments during the unwinding period beginning in 2023. Post-2023 enrollment changes should be interpreted in the context of unwinding, renewal operations, and the return to regular eligibility processes. This dashboard does not estimate the causal effect of unwinding.

Source:

- [KFF: Medicaid Enrollment and Unwinding Tracker](https://www.kff.org/medicaid/medicaid-enrollment-and-unwinding-tracker/)

## 6. Applications And Determinations

Applications submitted and eligibility determinations are descriptive operations indicators. They can help monitor application volume and determination activity, but they are not approval rates, timeliness measures, pending workload measures, or complete performance scores.

Applications and determinations may not have identical operational definitions. A monthly count of applications is a flow measure, while enrollment is a point-in-time measure. Determinations may reflect application-stage eligibility activity and should not be treated as a complete picture of renewals, procedural outcomes, or pending work.

Source:

- [Data.Medicaid.gov: State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data](https://data.medicaid.gov/dataset/6165f45b-ca93-5bb5-9d06-db29c692a360/data)

## 7. Population Denominators

Raw enrollment counts are affected by state population size. Population-adjusted metrics, such as enrollment per 1,000 residents and applications or determinations per 100,000 residents, provide better context for comparing states of different sizes.

These metrics should be described as population-adjusted context or enrollment relative to state population. Do not call them usage rates. Medicaid enrollment is coverage enrollment, not healthcare utilization.

Source:

- [U.S. Census Bureau: NST-EST2024-POP state resident population estimates](https://www2.census.gov/programs-surveys/popest/tables/2020-2024/state/totals/NST-EST2024-POP.xlsx)

## 8. Dataset Limitations

The dashboard uses public aggregate state-month data. It does not include beneficiary-level records, claims, utilization, cost, diagnosis, hospital use, county-level data, managed care plan data, or individual outcomes.

The dashboard supports descriptive monitoring and policy context. It does not support causal inference, individual-level outcome analysis, claims analysis, utilization analysis, cost analysis, or complete operations performance measurement.

Important interpretation limits:

- Latest-month data may be preliminary.
- State reporting practices can vary.
- High-missingness fields should not be used as headline metrics.
- Review flags identify records that may warrant context review; they are not errors or performance labels.
- Population-adjusted metrics are approximate descriptive context because population denominators are annual while Medicaid reporting is monthly.
