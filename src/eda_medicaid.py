"""Exploratory analysis helpers for Medicaid/CHIP dashboard tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "dashboard_tables"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

CLEAN_DATA_PATH = PROCESSED_DIR / "medicaid_enrollment_clean.csv"
QUALITY_SUMMARY_PATH = PROCESSED_DIR / "data_quality_summary.csv"

ENROLLMENT_COLUMNS = [
    "total_medicaid_and_chip_enrollment",
    "total_medicaid_enrollment",
    "total_chip_enrollment",
]

APPLICATION_COLUMN = "total_applications_for_financial_assistance_submitted_at_state_level"
AGENCY_APPLICATION_COLUMN = "new_applications_submitted_to_medicaid_and_chip_agencies"
DETERMINATION_COLUMN = "total_medicaid_and_chip_determinations"
MEDICAID_DETERMINATION_COLUMN = "individuals_determined_eligible_for_medicaid_at_application"
CHIP_DETERMINATION_COLUMN = "individuals_determined_eligible_for_chip_at_application"

HIGH_MISSINGNESS_FIELDS = [
    "total_adult_medicaid_enrollment",
    "total_call_center_volume_number_of_calls",
    "average_call_center_wait_time_minutes",
    "average_call_center_abandonment_rate",
    "total_medicaid_and_chip_determinations_processed_in_less_than_24_hours",
    "total_medicaid_and_chip_determinations_processed_between_24_hours_and_7_days",
    "total_medicaid_and_chip_determinations_processed_between_8_days_and_30_days",
    "total_medicaid_and_chip_determinations_processed_between_31_days_and_45_days",
    "total_medicaid_and_chip_determinations_processed_in_more_than_45_days",
]


def load_clean_data(path: Path = CLEAN_DATA_PATH) -> pd.DataFrame:
    """Load the cleaned state-month Medicaid/CHIP dataset."""
    df = pd.read_csv(path, parse_dates=["reporting_month"])
    return df.sort_values(["state_abbreviation", "reporting_month"]).reset_index(drop=True)


def load_quality_summary(path: Path = QUALITY_SUMMARY_PATH) -> pd.DataFrame:
    """Load the processed data quality summary."""
    return pd.read_csv(path)


def latest_month(df: pd.DataFrame) -> pd.Timestamp:
    """Return the most recent reporting month."""
    return df["reporting_month"].max()


def national_enrollment_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Create national monthly enrollment trend table."""
    trend = (
        df.groupby("reporting_month", as_index=False)
        .agg(
            total_medicaid_and_chip_enrollment=("total_medicaid_and_chip_enrollment", "sum"),
            total_medicaid_enrollment=("total_medicaid_enrollment", "sum"),
            total_chip_enrollment=("total_chip_enrollment", "sum"),
            state_records=("state_abbreviation", "nunique"),
            preliminary_records=("final_report", lambda s: int((s != "Y").sum())),
        )
        .sort_values("reporting_month")
    )
    trend["monthly_change"] = trend["total_medicaid_and_chip_enrollment"].diff()
    trend["percent_monthly_change"] = (
        trend["total_medicaid_and_chip_enrollment"].pct_change() * 100
    )
    trend["year_over_year_change"] = trend["total_medicaid_and_chip_enrollment"].diff(12)
    trend["percent_year_over_year_change"] = (
        trend["total_medicaid_and_chip_enrollment"].pct_change(12) * 100
    )
    return trend


def national_applications_determinations_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Create national monthly applications and determinations trend table."""
    trend = (
        df.groupby("reporting_month", as_index=False)
        .agg(
            applications_submitted=(APPLICATION_COLUMN, "sum"),
            medicaid_chip_agency_applications=(AGENCY_APPLICATION_COLUMN, "sum"),
            total_medicaid_and_chip_determinations=(DETERMINATION_COLUMN, "sum"),
            medicaid_determinations=(MEDICAID_DETERMINATION_COLUMN, "sum"),
            chip_determinations=(CHIP_DETERMINATION_COLUMN, "sum"),
            total_medicaid_and_chip_enrollment=("total_medicaid_and_chip_enrollment", "sum"),
            state_records=("state_abbreviation", "nunique"),
            preliminary_records=("final_report", lambda s: int((s != "Y").sum())),
        )
        .sort_values("reporting_month")
    )
    trend["determinations_per_application"] = (
        trend["total_medicaid_and_chip_determinations"] / trend["applications_submitted"]
    )
    trend["applications_per_1000_enrollees"] = (
        trend["applications_submitted"] / trend["total_medicaid_and_chip_enrollment"] * 1000
    )
    trend["determinations_per_1000_enrollees"] = (
        trend["total_medicaid_and_chip_determinations"]
        / trend["total_medicaid_and_chip_enrollment"]
        * 1000
    )
    return trend


def state_latest_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    """Create latest-month state snapshot table."""
    latest = latest_month(df)
    columns = [
        "state_abbreviation",
        "state_name",
        "reporting_month",
        "preliminary_or_updated",
        "final_report",
        "total_medicaid_and_chip_enrollment",
        "total_medicaid_enrollment",
        "total_chip_enrollment",
        APPLICATION_COLUMN,
        DETERMINATION_COLUMN,
    ]
    snapshot = df.loc[df["reporting_month"] == latest, columns].copy()
    snapshot["national_enrollment_rank"] = snapshot[
        "total_medicaid_and_chip_enrollment"
    ].rank(ascending=False, method="min")
    return snapshot.sort_values("national_enrollment_rank")


def state_enrollment_change(df: pd.DataFrame) -> pd.DataFrame:
    """Create state-level enrollment change table."""
    first_month = df["reporting_month"].min()
    last_month = df["reporting_month"].max()
    baseline = df[df["reporting_month"] == first_month][
        ["state_abbreviation", "state_name", "total_medicaid_and_chip_enrollment"]
    ].rename(columns={"total_medicaid_and_chip_enrollment": "baseline_enrollment"})
    latest = df[df["reporting_month"] == last_month][
        ["state_abbreviation", "total_medicaid_and_chip_enrollment"]
    ].rename(columns={"total_medicaid_and_chip_enrollment": "latest_enrollment"})
    one_year_prior_month = last_month - pd.DateOffset(months=12)
    prior = df[df["reporting_month"] == one_year_prior_month][
        ["state_abbreviation", "total_medicaid_and_chip_enrollment"]
    ].rename(columns={"total_medicaid_and_chip_enrollment": "enrollment_12_months_prior"})

    change = baseline.merge(latest, on="state_abbreviation", how="left").merge(
        prior, on="state_abbreviation", how="left"
    )
    change["baseline_month"] = first_month
    change["latest_month"] = last_month
    change["change_since_baseline"] = change["latest_enrollment"] - change["baseline_enrollment"]
    change["percent_change_since_baseline"] = (
        change["change_since_baseline"] / change["baseline_enrollment"] * 100
    )
    change["change_last_12_months"] = (
        change["latest_enrollment"] - change["enrollment_12_months_prior"]
    )
    change["percent_change_last_12_months"] = (
        change["change_last_12_months"] / change["enrollment_12_months_prior"] * 100
    )
    change["rank_by_latest_enrollment"] = change["latest_enrollment"].rank(
        ascending=False, method="min"
    )
    change["rank_by_change_since_baseline"] = change["change_since_baseline"].rank(
        ascending=False, method="min"
    )
    return change.sort_values("rank_by_latest_enrollment")


def state_eligibility_operations_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create state-level applications and determinations summary table."""
    grouped = (
        df.groupby(["state_abbreviation", "state_name"], as_index=False)
        .agg(
            total_applications_submitted=(APPLICATION_COLUMN, "sum"),
            medicaid_chip_agency_applications=(AGENCY_APPLICATION_COLUMN, "sum"),
            total_medicaid_and_chip_determinations=(DETERMINATION_COLUMN, "sum"),
            medicaid_determinations=(MEDICAID_DETERMINATION_COLUMN, "sum"),
            chip_determinations=(CHIP_DETERMINATION_COLUMN, "sum"),
            average_monthly_enrollment=("total_medicaid_and_chip_enrollment", "mean"),
            latest_month=("reporting_month", "max"),
        )
        .sort_values("total_applications_submitted", ascending=False)
    )
    grouped["determinations_per_application"] = (
        grouped["total_medicaid_and_chip_determinations"]
        / grouped["total_applications_submitted"]
    )
    grouped["applications_per_1000_average_enrollees"] = (
        grouped["total_applications_submitted"] / grouped["average_monthly_enrollment"] * 1000
    )
    grouped["determinations_per_1000_average_enrollees"] = (
        grouped["total_medicaid_and_chip_determinations"]
        / grouped["average_monthly_enrollment"]
        * 1000
    )
    return grouped


def data_quality_by_field(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize missingness and zero values by field."""
    rows = []
    for column in df.columns:
        missing_count = int(df[column].isna().sum())
        zero_count = int((df[column] == 0).sum()) if pd.api.types.is_numeric_dtype(df[column]) else 0
        rows.append(
            {
                "field_name": column,
                "missing_count": missing_count,
                "missing_percent": round(missing_count / len(df) * 100, 2),
                "zero_count": zero_count,
                "zero_percent": round(zero_count / len(df) * 100, 2),
                "use_caution": column in HIGH_MISSINGNESS_FIELDS or missing_count > 0,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["missing_percent", "zero_percent"], ascending=False
    )


def data_quality_by_state(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize missingness by state."""
    quality_fields = [column for column in df.columns if column != "reporting_period"]
    rows = []
    for (state_abbreviation, state_name), group in df.groupby(
        ["state_abbreviation", "state_name"]
    ):
        missing_count = int(group[quality_fields].isna().sum().sum())
        cell_count = int(group[quality_fields].shape[0] * group[quality_fields].shape[1])
        rows.append(
            {
                "state_abbreviation": state_abbreviation,
                "state_name": state_name,
                "record_count": len(group),
                "missing_value_count": missing_count,
                "missing_value_percent": round(missing_count / cell_count * 100, 2),
                "preliminary_records": int((group["final_report"] != "Y").sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("missing_value_percent", ascending=False)


def data_quality_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize missingness and reporting status by month."""
    quality_fields = [column for column in df.columns if column != "reporting_period"]
    rows = []
    for month, group in df.groupby("reporting_month"):
        missing_count = int(group[quality_fields].isna().sum().sum())
        cell_count = int(group[quality_fields].shape[0] * group[quality_fields].shape[1])
        rows.append(
            {
                "reporting_month": month,
                "state_records": int(group["state_abbreviation"].nunique()),
                "missing_value_count": missing_count,
                "missing_value_percent": round(missing_count / cell_count * 100, 2),
                "preliminary_records": int((group["final_report"] != "Y").sum()),
                "all_records_final": bool((group["final_report"] == "Y").all()),
            }
        )
    return pd.DataFrame(rows).sort_values("reporting_month")


def kpi_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create a compact KPI summary for the eventual dashboard."""
    national = national_enrollment_trend(df)
    ops = national_applications_determinations_trend(df)
    latest = latest_month(df)
    latest_national = national[national["reporting_month"] == latest].iloc[0]
    latest_ops = ops[ops["reporting_month"] == latest].iloc[0]
    baseline = national.iloc[0]
    prior_month = national.iloc[-2] if len(national) > 1 else latest_national
    return pd.DataFrame(
        [
            {
                "metric": "latest_reporting_month",
                "value": latest.strftime("%Y-%m"),
                "notes": "Latest available reporting month in cleaned data.",
            },
            {
                "metric": "latest_month_is_preliminary",
                "value": bool(latest_national["preliminary_records"] > 0),
                "notes": "Treat latest month cautiously when preliminary records are present.",
            },
            {
                "metric": "states_dc_included",
                "value": int(df["state_abbreviation"].nunique()),
                "notes": "All 50 states plus DC.",
            },
            {
                "metric": "latest_total_medicaid_chip_enrollment",
                "value": int(latest_national["total_medicaid_and_chip_enrollment"]),
                "notes": "National sum across state/DC records.",
            },
            {
                "metric": "monthly_enrollment_change",
                "value": int(
                    latest_national["total_medicaid_and_chip_enrollment"]
                    - prior_month["total_medicaid_and_chip_enrollment"]
                ),
                "notes": "Change from prior reporting month.",
            },
            {
                "metric": "change_since_january_2019",
                "value": int(
                    latest_national["total_medicaid_and_chip_enrollment"]
                    - baseline["total_medicaid_and_chip_enrollment"]
                ),
                "notes": "Descriptive change since first month in cleaned dataset.",
            },
            {
                "metric": "latest_applications_submitted",
                "value": int(latest_ops["applications_submitted"]),
                "notes": "National total applications for financial assistance submitted at state level.",
            },
            {
                "metric": "latest_total_determinations",
                "value": int(latest_ops["total_medicaid_and_chip_determinations"]),
                "notes": "National total Medicaid/CHIP eligibility determinations at application.",
            },
        ]
    )


def dashboard_notes(df: pd.DataFrame) -> pd.DataFrame:
    """Create plain-language notes for the eventual dashboard."""
    latest = latest_month(df)
    preliminary_count = int((df[df["reporting_month"] == latest]["final_report"] != "Y").sum())
    notes = [
        (
            "data_source",
            "Data source is the official CMS/Data.Medicaid.gov State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data.",
        ),
        (
            "latest_reporting_month_caution",
            f"The latest reporting month is {latest:%Y-%m}; {preliminary_count} state/DC records are preliminary and should be interpreted cautiously.",
        ),
        (
            "preliminary_final_reporting",
            "CMS source data can include preliminary and updated/final records. The cleaned dataset keeps one record per state-month and prefers final/updated records.",
        ),
        (
            "enrollment_interpretation",
            "Enrollment fields are point-in-time month-end aggregate counts and support descriptive trend monitoring.",
        ),
        (
            "application_determination_interpretation",
            "Applications and determinations are descriptive operational indicators, not complete performance scores.",
        ),
        (
            "missingness_caveats",
            "Adult enrollment, call center, and processing-time fields have substantial missingness and should not be headline KPIs without caveats.",
        ),
        (
            "dashboard_limits",
            "The dashboard cannot show individual outcomes, causal policy effects, claims/utilization patterns, pending applications, or clean standalone renewal volumes.",
        ),
    ]
    return pd.DataFrame(notes, columns=["note_type", "note_text"])


def top_state_increases(change: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return top states by enrollment increase since baseline."""
    return change.sort_values("change_since_baseline", ascending=False).head(n)


def top_state_decreases(change: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return top states by enrollment decrease since baseline."""
    return change.sort_values("change_since_baseline", ascending=True).head(n)
