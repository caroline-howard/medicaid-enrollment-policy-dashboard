# Medicaid Enrollment & Eligibility Operations Dashboard Project Tasks

This checklist tracks planned project work in a GitHub issue-style format. It is intended to keep the portfolio project organized across data ingestion, data quality, analytics, dashboard development, documentation, and career-facing outputs.

## 1. Project Setup

- [x] Confirm repo structure: Verify the repository has clear folders for data, notebooks, source code, outputs, and documentation.
- [x] Confirm `requirements.txt`: Confirm core Python, dashboard, notebook, and environment packages are listed.
- [x] Confirm `.gitignore`: Confirm virtual environments, caches, notebook checkpoints, environment files, OS files, and large raw data files are excluded.
- [x] Confirm README project framing: Confirm the README explains the project goal, target roles, planned data sources, planned outputs, and current status.
- [x] Confirm docs folder and data dictionary placeholders: Confirm documentation files and the data dictionary are ready for source validation updates.

## 2. Data Ingestion

- [ ] Identify official CMS/Medicaid data source: Select the authoritative public source for Medicaid/CHIP enrollment and eligibility operations data.
- [ ] Download or access public Medicaid/CHIP enrollment and eligibility operations data: Use the official source without modifying raw values.
- [ ] Document source URL, access date, update date, and dataset description: Record enough metadata for reproducibility and policy context.
- [ ] Save raw data or document download instructions if raw files are too large: Preserve raw data when practical, or document a repeatable access method.

## 3. Data Cleaning

- [ ] Standardize column names: Convert source fields into consistent, readable snake_case names.
- [ ] Parse reporting dates: Convert reporting periods into validated date fields suitable for state-month analysis.
- [ ] Standardize state names/abbreviations: Ensure state identifiers are consistent across source files and outputs.
- [ ] Preserve enrollment and eligibility operations fields: Keep policy-relevant source fields needed for dashboard reporting and data quality review.
- [ ] Create cleaned state-month dataset: Produce a validated state-month table for downstream analysis.
- [ ] Create dashboard sample dataset: Create a small, documented sample for development only after real data is validated.

## 4. Data Quality Checks

- [ ] Check missingness by field: Summarize missing values across source and cleaned fields.
- [ ] Check missingness by state/month: Identify gaps that affect trend reporting or state comparisons.
- [ ] Check duplicate state-month records: Confirm whether records are unique at the intended reporting grain.
- [ ] Check suspicious zero or negative values: Flag values that may require source review or interpretation notes.
- [ ] Identify incomplete months: Determine whether recent reporting periods are partial, preliminary, or otherwise incomplete.
- [ ] Document state reporting variation and limitations: Capture differences in state reporting practices and known caveats.

## 5. Exploratory Data Analysis

- [ ] Summarize national enrollment trends: Create descriptive summaries of national Medicaid/CHIP enrollment patterns.
- [ ] Compare state-level enrollment changes: Identify state-level increases, decreases, and variation over time.
- [ ] Analyze applications and eligibility determinations if available: Describe eligibility operations trends where source fields support it.
- [ ] Identify states/months with unusual changes: Flag changes for further review without making unsupported causal claims.
- [ ] Create dashboard-ready summary tables: Prepare EDA outputs that can feed the final dashboard structure.

## 6. Dashboard Tables

- [ ] Create KPI summary table: Prepare high-level indicators for dashboard cards.
- [ ] Create national trend table: Prepare national monthly trend data.
- [ ] Create state comparison table: Prepare state-level comparison and ranking outputs.
- [ ] Create eligibility operations table: Prepare applications, determinations, and related operations fields where available.
- [ ] Create data quality summary table: Prepare missingness, completeness, duplicate, and caution-flag summaries.

## 7. Plotly Dash App

- [ ] Build dashboard layout: Create the overall application structure after validated dashboard tables exist.
- [ ] Add KPI cards: Display high-level enrollment and operations indicators.
- [ ] Add national trend chart: Show national enrollment or operations trends over time.
- [ ] Add state comparison chart/map: Support state-level comparison and exploration.
- [ ] Add eligibility operations section: Present applications, determinations, and related fields where valid.
- [ ] Add data quality section: Show completeness, missingness, and reporting caveats.
- [ ] Add policy interpretation notes: Include plain-language notes for healthcare reporting and Medicaid program monitoring.

## 8. README Screenshots And Polish

- [ ] Add dashboard screenshot: Include a current screenshot after the dashboard is built.
- [ ] Add workflow diagram: Show the data flow from public source to cleaned outputs, dashboard tables, and reporting.
- [ ] Add live dashboard link: Add the deployed dashboard URL after deployment.
- [ ] Add GitHub repo structure: Keep the repository map current as files are added.
- [ ] Add "What this project demonstrates" section: Explain the project skills for healthcare analytics and policy audiences.
- [ ] Add resume bullet: Include a concise role-aligned portfolio bullet.

## 9. Policy Brief

- [ ] Create a short project brief: Write a polished brief suitable for job applications and interviews.
- [ ] Summarize data source, key findings, dashboard use case, and limitations: Keep the brief concise, source-aware, and policy-facing.
- [ ] Write in healthcare policy/business analyst language: Emphasize reporting, operations, data quality, and stakeholder interpretation.

## 10. Resume And LinkedIn Outputs

- [ ] Create resume bullet: Draft a clear, evidence-based bullet aligned with healthcare analytics roles.
- [ ] Create LinkedIn project description: Write a short public-facing project summary.
- [ ] Create short interview explanation: Prepare a concise explanation of the project purpose, workflow, and value.
