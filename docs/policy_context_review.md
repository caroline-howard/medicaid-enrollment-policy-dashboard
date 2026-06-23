# State Policy Context Review

Third-pass research artifact. This is for review only; do not add any row to the dashboard until approved.

## Research approach

- Added stricter approval fields: `source_type`, `scraped_text_excerpt`, `verification_status`, `app_candidate`, and `approval_recommendation`.
- Official state or CMS/Medicaid.gov sources are required for `app_candidate = yes`.
- KFF rows are retained for background/discovery but are not app-ready unless separately verified through an official source.
- Scrape failures and blocked pages are recorded in `data/raw/state_policy_source_scrape_log.csv`.

## Summary

- State/DC units covered: 51
- Total rows in CSV: 249
- App-ready candidates pending your review: 5 states/DC
- States/DC still needing deeper official-source research: 46
- Scrape log rows: 54
- KFF-only rows downgraded from primary/use: 46

## States ready for review as app candidates

Arkansas (AR), Georgia (GA), North Carolina (NC), Nebraska (NE), Utah (UT)

## States with only background or non-app context

Alaska (AK), Alabama (AL), Arizona (AZ), California (CA), Colorado (CO), Connecticut (CT), District of Columbia (DC), Delaware (DE), Florida (FL), Hawaii (HI), Iowa (IA), Idaho (ID), Illinois (IL), Indiana (IN), Kansas (KS), Kentucky (KY), Louisiana (LA), Massachusetts (MA), Maryland (MD), Maine (ME), Michigan (MI), Minnesota (MN), Missouri (MO), Mississippi (MS), Montana (MT), North Dakota (ND), New Hampshire (NH), New Jersey (NJ), New Mexico (NM), Nevada (NV), New York (NY), Ohio (OH), Oklahoma (OK), Oregon (OR), Pennsylvania (PA), Rhode Island (RI), South Carolina (SC), South Dakota (SD), Tennessee (TN), Texas (TX), Virginia (VA), Vermont (VT), Washington (WA), Wisconsin (WI), West Virginia (WV), Wyoming (WY)

## States still needing deeper manual research

Alaska (AK), Alabama (AL), Arizona (AZ), California (CA), Colorado (CO), Connecticut (CT), District of Columbia (DC), Delaware (DE), Florida (FL), Hawaii (HI), Iowa (IA), Idaho (ID), Illinois (IL), Indiana (IN), Kansas (KS), Kentucky (KY), Louisiana (LA), Massachusetts (MA), Maryland (MD), Maine (ME), Michigan (MI), Minnesota (MN), Missouri (MO), Mississippi (MS), Montana (MT), North Dakota (ND), New Hampshire (NH), New Jersey (NJ), New Mexico (NM), Nevada (NV), New York (NY), Ohio (OH), Oklahoma (OK), Oregon (OR), Pennsylvania (PA), Rhode Island (RI), South Carolina (SC), South Dakota (SD), Tennessee (TN), Texas (TX), Virginia (VA), Vermont (VT), Washington (WA), Wisconsin (WI), West Virginia (WV), Wyoming (WY)

## Sources scraped

- **All states (ALL)**: [Medicaid.gov State Waivers List](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `success`; broad official waiver-list scrape used for discovery, but many result blocks have waiver titles/dates rather than enough feature detail for app-ready blurbs.
- **Arkansas (AR)**: [Arkansas DHS ARHOME](https://humanservices.arkansas.gov/divisions-shared-services/medical-services/healthcare-programs/arhome/) — `success`.
- **Arkansas (AR)**: [Arkansas DHS Cover Arkansas](https://humanservices.arkansas.gov/divisions-shared-services/medical-services/update-arkansas-2/if-you-have-lost-health-care-coverage/) — `success`.
- **Arkansas (AR)**: [Arkansas DHS ARHOME work requirement](https://humanservices.arkansas.gov/divisions-shared-services/medical-services/healthcare-programs/arhome/arhome-community-engagement-requirement/) — `success`.
- **California (CA)**: [California DHCS Adult Expansion](https://www.dhcs.ca.gov/services/medi-cal/eligibility/Pages/Adult-Expansion.aspx) — `partial`; very limited text extracted.
- **North Carolina (NC)**: [NC Medicaid expansion](https://medicaid.ncdhhs.gov/north-carolina-expands-medicaid) — `success`.
- **Georgia (GA)**: [Georgia Pathways About](https://pathways.georgia.gov/about-pathways) — `success`.
- **Georgia (GA)**: [Georgia Pathways Qualifying Activities](https://pathways.georgia.gov/qualifying-activities) — `success`.
- **Nebraska (NE)**: [Nebraska DHHS Medicaid Expansion](https://dhhs.ne.gov/Pages/Medicaid-Expansion.aspx) — `success`.
- **Utah (UT)**: [Utah DHHS Medicaid Expansion](https://medicaid.utah.gov/expansion/) — `success`.
- **Idaho (ID)**: [Idaho H&W Adult Medicaid](https://healthandwelfare.idaho.gov/services-programs/medicaid-health/adult-medicaid) — `failed`; page returned 404/error content or no policy text.
- **South Dakota (SD)**: [South Dakota DSS Medicaid expansion](https://dss.sd.gov/medicaid/generalinfo/expansion.aspx) — `failed`; page returned 404/error content or no policy text.
- **Missouri (MO)**: [Missouri DSS Adult Expansion](https://mydss.mo.gov/healthcare/apply/adult-expansion) — `failed`; page returned 404/error content or no policy text.
- **Oklahoma (OK)**: [Oklahoma OHCA SoonerCare Expansion](https://oklahoma.gov/ohca/individuals/mysoonercare/sooner-care-expansion.html) — `failed`; page returned 404/error content or no policy text.
- **Alabama (AL)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Alaska (AK)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Arizona (AZ)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Colorado (CO)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Connecticut (CT)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Delaware (DE)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **District of Columbia (DC)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Florida (FL)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Hawaii (HI)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Illinois (IL)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Indiana (IN)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Iowa (IA)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Kansas (KS)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Kentucky (KY)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Louisiana (LA)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Maine (ME)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Maryland (MD)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Massachusetts (MA)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Michigan (MI)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Minnesota (MN)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Mississippi (MS)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Montana (MT)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Nevada (NV)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **New Hampshire (NH)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **New Jersey (NJ)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **New Mexico (NM)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **New York (NY)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **North Dakota (ND)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Ohio (OH)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Oregon (OR)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Pennsylvania (PA)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Rhode Island (RI)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **South Carolina (SC)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Tennessee (TN)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Texas (TX)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Vermont (VT)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Virginia (VA)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Washington (WA)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **West Virginia (WV)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Wisconsin (WI)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.
- **Wyoming (WY)**: [Medicaid.gov Section 1115 demonstration list](https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/index.html) — `not_attempted`; manual official-source search still needed.

## Facts downgraded or not ready

- KFF expansion/postpartum rows are kept as `background_context` or `needs_second_pass`, not app-ready visible blurbs.
- KFF Section 1115 waiver tracker rows are kept as discovery/background unless an official state/CMS source verifies the actual feature and source text.
- California adult expansion remains important but is marked `app_candidate = no` in this file because automated scraping of DHCS returned an Incapsula challenge; manual verification is needed before app use.
- Future-dated Arkansas work/community engagement rollout is marked `do_not_use_yet` for the current dashboard window.

## Alaska (AK)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Alabama (AL)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion not adopted as of May 2026 (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Arkansas (AR)

### App candidate

- **ARHOME replaced Arkansas Works** (2022-01-01)
  - Source: [Arkansas Department of Human Services: ARHOME](https://humanservices.arkansas.gov/divisions-shared-services/medical-services/healthcare-programs/arhome/)
  - Proposed blurb: Arkansas policy context includes ARHOME, which replaced Arkansas Works on January 1, 2022. This state-specific waiver structure may help contextualize Arkansas enrollment and operations trends, but the dashboard does not estimate its causal effect.
  - Excerpt: questions about eligibility  should contact the Division of County Operations . On January 1, 2022, Arkansas Works was replaced by the Arkansas Health and Opportunity for Me program, or ARHOME . The ARHOME program uses Medicaid dollars to buy private health insurance for you. You’re still covered by Medicaid, but your coverage is provided by one of

### Review notes

- Review wording for brevity and confirm the blurb should be shown in the app.

## Arizona (AZ)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## California (CA)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Colorado (CO)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Connecticut (CT)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## District of Columbia (DC)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Delaware (DE)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Florida (FL)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion not adopted as of May 2026 (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Georgia (GA)

### App candidate

- **Georgia Pathways to Coverage with qualifying activities** (2023-07-01)
  - Source: [Georgia Pathways to Coverage: About Pathways](https://pathways.georgia.gov/about-pathways)
  - Proposed blurb: Georgia policy context includes Pathways to Coverage, a limited Medicaid coverage pathway for some adults up to 100% FPL with qualifying activity requirements. This may help contextualize Georgia trends, but it should not be treated as full ACA expansion.
  - Excerpt: promote members’ transition from Pathways into private coverage.  This program offers Medicaid coverage to eligible Georgians ages 19-64 who have a household income of up to 100% of the Federal Poverty Level (FPL). For example, in 2026, this equals $15,960 per year or $1,330 on average per month for one person, and $27,320 per year or $2,277 on ave

### Review notes

- Review wording for brevity and confirm the blurb should be shown in the app.

## Hawaii (HI)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Iowa (IA)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Idaho (ID)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Illinois (IL)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Indiana (IN)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Kansas (KS)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion not adopted as of May 2026 (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Kentucky (KY)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Louisiana (LA)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Massachusetts (MA)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Maryland (MD)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Maine (ME)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Michigan (MI)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Minnesota (MN)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Missouri (MO)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Mississippi (MS)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion not adopted as of May 2026 (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Montana (MT)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## North Carolina (NC)

### App candidate

- **North Carolina Medicaid expansion implemented** (2023-12-01)
  - Source: [NC Medicaid: North Carolina Expands Medicaid](https://medicaid.ncdhhs.gov/north-carolina-expands-medicaid)
  - Proposed blurb: North Carolina expanded Medicaid on December 1, 2023, covering adults ages 19 through 64 up to 138% of the federal poverty line. This may help contextualize North Carolina enrollment and application patterns after late 2023 without implying causality.
  - Excerpt: erage to more people. Versión en español Video in American Sign Language (ASL)  On December 1, 2023, NC Medicaid expanded to cover people ages 19 through 64 up to 138% of the federal poverty line. That’s about $1,800/month for singles and $3,065/month for families of three. NC Medicaid covers most health services. It includes doctor visits, check-u

### Review notes

- Review wording for brevity and confirm the blurb should be shown in the app.

## North Dakota (ND)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Nebraska (NE)

### App candidate

- **Nebraska Medicaid expansion / Heritage Health Adult benefits** (2021-10-01)
  - Source: [Nebraska DHHS: Medicaid Expansion in Nebraska](https://dhhs.ne.gov/Pages/Medicaid-Expansion.aspx)
  - Proposed blurb: Nebraska expansion context includes Heritage Health Adult coverage for adults ages 19-64 up to 138% FPL and equal expansion benefits effective October 1, 2021. This may help contextualize Nebraska enrollment and program-mix interpretation.
  - Excerpt: ved equal benefits, including dental, vision, and over-the-counter medications, effective October 1, 2021. Prior to this date, receipt of dental, vision, and over-the-counter medications was subject to specific criteria​.​ ​ For copies of previously published items on this page, please contact Medicaid at  DHHS.MedicaidExpansionQuestions@Nebraska.g

### Review notes

- Review wording for brevity and confirm the blurb should be shown in the app.

## New Hampshire (NH)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## New Jersey (NJ)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## New Mexico (NM)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Nevada (NV)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## New York (NY)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Ohio (OH)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Oklahoma (OK)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Oregon (OR)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Pennsylvania (PA)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Rhode Island (RI)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## South Carolina (SC)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion not adopted as of May 2026 (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## South Dakota (SD)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Tennessee (TN)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion not adopted as of May 2026 (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Texas (TX)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion not adopted as of May 2026 (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Utah (UT)

### App candidate

- **Utah full Medicaid expansion authorized** (2019-12-23)
  - Source: [Utah DHHS Medicaid: Medicaid Expansion](https://medicaid.utah.gov/expansion/)
  - Proposed blurb: Utah policy context includes CMS authorization of full Medicaid expansion in December 2019 and later withdrawal of the community engagement requirement. This may help contextualize Utah trends during the dashboard period without implying a causal estimate.
  - Excerpt: required by federal or state statute to remain on our website. Program History On December 23, 2019, the Centers for Medicare and Medicaid Services (CMS) authorized the Utah Department of Health (UDOH) to implement a full Medicaid expansion in the state. The expansion extends Medicaid eligibility to Utah adults whose annual income is up to 138% of 

### Review notes

- Review wording for brevity and confirm the blurb should be shown in the app.

## Virginia (VA)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Vermont (VT)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Washington (WA)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Wisconsin (WI)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion not adopted as of May 2026 (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## West Virginia (WV)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion in effect during dashboard period (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Wyoming (WY)

### App candidate

- No app-ready official-source blurb candidate in this pass.

### Review notes

- Best available non-app context: ACA Medicaid expansion not adopted as of May 2026 (`background_only`, `kff`).
- Needs official state/CMS source verification before visible dashboard use.

## Recommended next implementation step

Review and approve one `app_candidate = yes` row per state where available. For states without an app-ready row, either leave policy context pending or run targeted manual searches against official state Medicaid and CMS waiver/source documents. Do not wire these facts into the app until approved.

## Fourth-Pass Batch 1 Official-Source Review

### States researched

California, Florida, Texas, New York, Pennsylvania, Illinois, Ohio, Michigan, New Jersey, Virginia.

### Newly app-ready candidates

- **Illinois (IL)** — Health Benefits for Immigrant Seniors redeterminations; official Illinois HFS page; `app_candidate = yes`.
- **New Jersey (NJ)** — Cover All Kids / NJ FamilyCare children regardless of immigration status; official New Jersey Cover All Kids page; `app_candidate = yes` pending date/wording review.
- **Virginia (VA)** — Adult Medicaid expansion population since January 1, 2019; official Virginia DMAS page; `app_candidate = yes`.

### Batch 1 manual follow-up queue

These states should stay in a targeted manual follow-up queue. They are not app-ready yet, but they should not block continuing to Batch 2 after the Batch 1 app-ready candidates are reviewed.

- **California (CA)** — Adult Expansion remains important, but the DHCS page returned an Incapsula challenge. Keep `app_candidate = no` until manually verified or sourced from another official accessible page/PDF.
- **Florida (FL)** — DCF/AHCA official page attempts returned 404 or no policy text. Needs another official source.
- **Texas (TX)** — Texas HHS postpartum pages returned shell content without body text. Needs manual review or alternate official source.
- **New York (NY)** — NY DOH page blocked with CloudFront 403; Medicaid.gov waiver list provides official waiver titles/dates but not enough feature detail for a dashboard blurb.
- **Pennsylvania (PA)** — PA.gov postpartum page found, but static scrape exposed limited body text. Needs alternate official source or manual review.
- **Ohio (OH)** — Ohio Medicaid Next Generation URL attempts returned 404. Needs alternate official source.
- **Michigan (MI)** — MDHHS pages returned permission denied. Needs alternate official source.

### Sources used

- Illinois HFS Health Benefits for Immigrants: https://hfs.illinois.gov/medicalclients/healthbenefitsforimmigrants.html
- New Jersey Cover All Kids: https://www.nj.gov/coverallkids/
- Virginia DMAS Adults Aged 19-64: https://www.dmas.virginia.gov/for-applicants/populations-served/for-adults/adults-aged-19-64/
- Medicaid.gov New York filtered State Waivers List: https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list?filter%5Bfield_state%5D%5Bin%5D%5B0%5D=786

### Blocked or failed scrape attempts

- California DHCS Adult Expansion: Incapsula challenge.
- New York Department of Health NYHER page: CloudFront 403.
- Michigan MDHHS pages: permission denied.
- Florida DCF/AHCA pages: 404 or no relevant policy text.
- Ohio Medicaid Next Generation page: 404.
- Texas HHS pages: site shell without article/body text.
- Pennsylvania PA.gov page: partial/static scrape only.

### Facts downgraded or not to use yet

- New York Medicaid Redesign Team waiver list context remains background-only because the visible source text did not describe a specific policy feature enough for a dashboard blurb.
- California, Texas, Pennsylvania, Ohio, Michigan, and Florida candidate facts should not be used in the app until stronger official source text is verified.

### Recommendation

Review the three Batch 1 app candidates first: Illinois, New Jersey, and Virginia. Keep California, Florida, Texas, New York, Pennsylvania, Ohio, and Michigan in a Batch 1 manual follow-up queue, but continue to Batch 2 when approved rather than stopping the broader research process.

## Fourth-Pass Batch 2 Official-Source Review

Date accessed: 2026-06-22

Batch 2 was limited to Arizona, Colorado, Massachusetts, Washington, Oregon, Tennessee, Wisconsin, South Carolina, Kentucky, and Louisiana. Dashboard app code was not modified. Batch 1 app candidates and the Batch 1 manual follow-up queue were preserved.

### Batch 2 app-ready candidates

These rows were marked `app_candidate = yes` because the fact was official-source verified, state-specific, and dashboard-ready pending your approval:

| State | Candidate fact | Source | Review note |
| --- | --- | --- | --- |
| Arizona | AHCCCS 1115 waiver extension approved October 14, 2022, including Targeted Investments 2.0 and Housing and Health Opportunities. | AHCCCS | Strong state-specific waiver context; avoid causal wording. |
| Massachusetts | MassHealth Section 1115 Demonstration extension approved through December 2027. | Mass.gov / MassHealth | Strong structural waiver context for MassHealth program interpretation. |
| Oregon | OHP Bridge launched July 1, 2024 for adults above traditional OHP Plus limits and up to 200% FPL. | Oregon Health Authority | Strong eligibility expansion context. |
| Washington | Apple Health Expansion is a limited-enrollment Apple Health pathway; official page notes enrollment cap status and immigration documentation context. | Washington HCA | Strong state-specific coverage-pathway context. |
| Wisconsin | ForwardHealth renewal process includes administrative renewal, renewal packets when needed, and late-renewal rules for most Medicaid programs. | Wisconsin DHS | Strong eligibility-operations context, not a new coverage expansion. |

### Batch 2 pending/manual follow-up

| State | Reason pending |
| --- | --- |
| Colorado | Official HCPF Cover All Coloradans page attempts were thin or did not expose usable policy text in this pass. Use Medicaid.gov/KFF only as eligibility-limit background for now. |
| Tennessee | Official TennCare eligibility categories page is useful background, but specific Katie Beckett/postpartum pages failed or returned unavailable pages. Needs a stronger event-specific official source. |
| South Carolina | Official SCDHHS eligibility and reporting dashboard links were found, but no strong 2019-2026 state-specific policy event was verified. |
| Kentucky | Official CHFS pages returned blocked/service-unavailable content. Needs manual official-source follow-up. |

### Background-only / not app-ready yet

| State | Fact | Why not app-ready yet |
| --- | --- | --- |
| Louisiana | LDH Reentry Demonstration 1115 waiver application submitted September 27, 2024; page describes pending/anticipated CMS approval and pre-release enrollment goals. | Official and state-specific, but source describes it as pending/anticipated. Use only as background until approval/implementation is verified. |

### Supporting sources added

- Medicaid.gov State Profiles were pulled as official state profile/eligibility background for Batch 2 states.
- KFF Medicaid State Fact Sheets were added as supporting eligibility-limit background only, per user suggestion. KFF was not used as a primary `verified_official` source for app-ready rows.

### Recommendation for Batch 3

Proceed to Batch 3 after reviewing the five Batch 2 app-ready candidates. Keep Colorado, Tennessee, South Carolina, Kentucky, and Louisiana in a Batch 2 manual follow-up queue, with Louisiana closest to app-ready once CMS approval/implementation status is verified.

