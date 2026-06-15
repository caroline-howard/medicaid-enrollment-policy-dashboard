"""Clean and validate Medicaid/CHIP enrollment and operations data."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from load_data import RAW_CSV_PATH, download_source_csv, load_raw_data, save_source_metadata


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

FULL_CLEAN_PATH = PROCESSED_DIR / "medicaid_enrollment_clean.csv"
STATE_MONTH_SUMMARY_PATH = PROCESSED_DIR / "medicaid_state_month_summary.csv"
SAMPLE_PATH = PROCESSED_DIR / "medicaid_sample_for_dashboard.csv"
QUALITY_SUMMARY_PATH = PROCESSED_DIR / "data_quality_summary.csv"

STATE_ABBREVIATIONS = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
}

KEY_COLUMNS = [
    "state_abbreviation",
    "state_name",
    "reporting_period",
    "reporting_month",
    "reporting_year",
    "state_expanded_medicaid",
    "preliminary_or_updated",
    "final_report",
    "new_applications_submitted_to_medicaid_and_chip_agencies",
    "applications_for_financial_assistance_submitted_to_the_state_based_marketplace",
    "total_applications_for_financial_assistance_submitted_at_state_level",
    "individuals_determined_eligible_for_medicaid_at_application",
    "individuals_determined_eligible_for_chip_at_application",
    "total_medicaid_and_chip_determinations",
    "medicaid_and_chip_child_enrollment",
    "total_medicaid_and_chip_enrollment",
    "total_medicaid_enrollment",
    "total_chip_enrollment",
    "total_adult_medicaid_enrollment",
    "total_medicaid_and_chip_determinations_processed_in_less_than_24_hours",
    "total_medicaid_and_chip_determinations_processed_between_24_hours_and_7_days",
    "total_medicaid_and_chip_determinations_processed_between_8_days_and_30_days",
    "total_medicaid_and_chip_determinations_processed_between_31_days_and_45_days",
    "total_medicaid_and_chip_determinations_processed_in_more_than_45_days",
    "total_call_center_volume_number_of_calls",
    "average_call_center_wait_time_minutes",
    "average_call_center_abandonment_rate",
]

NUMERIC_COLUMNS = [
    column
    for column in KEY_COLUMNS
    if column
    not in {
        "state_abbreviation",
        "state_name",
        "reporting_period",
        "reporting_month",
        "state_expanded_medicaid",
        "preliminary_or_updated",
        "final_report",
    }
]


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize source column names to snake_case."""
    cleaned = df.copy()
    cleaned.columns = (
        cleaned.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return cleaned


def parse_reporting_period(value: object) -> pd.Timestamp:
    """Parse CMS reporting period values into month-start timestamps."""
    if pd.isna(value):
        return pd.NaT

    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]

    for date_format in ("%Y%m", "%Y-%m-%d", "%Y-%m", "%m/%d/%Y", "%m/%Y"):
        parsed = pd.to_datetime(text, format=date_format, errors="coerce")
        if not pd.isna(parsed):
            return parsed.to_period("M").to_timestamp()

    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return pd.NaT
    return parsed.to_period("M").to_timestamp()


def clean_data(df: pd.DataFrame, start_year: int = 2019) -> pd.DataFrame:
    """Create a cleaned all-state monthly dataset from the CMS source data."""
    cleaned = standardize_column_names(df)
    cleaned["state_abbreviation"] = cleaned["state_abbreviation"].astype(str).str.strip().str.upper()
    cleaned["state_name"] = cleaned["state_name"].astype(str).str.strip()
    cleaned["reporting_month"] = cleaned["reporting_period"].apply(parse_reporting_period)
    cleaned["reporting_year"] = cleaned["reporting_month"].dt.year

    for column in NUMERIC_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    available_columns = [column for column in KEY_COLUMNS if column in cleaned.columns]
    cleaned = cleaned[available_columns].copy()
    cleaned = cleaned[
        cleaned["state_abbreviation"].isin(STATE_ABBREVIATIONS)
        & (cleaned["reporting_year"] >= start_year)
    ].copy()
    cleaned["final_report_sort"] = cleaned["final_report"].eq("Y").astype(int)
    cleaned = (
        cleaned.sort_values(
            ["state_abbreviation", "reporting_month", "final_report_sort"],
            ascending=[True, True, False],
        )
        .drop_duplicates(["state_abbreviation", "reporting_month"], keep="first")
        .drop(columns=["final_report_sort"])
    )
    cleaned = cleaned.sort_values(["state_abbreviation", "reporting_month"]).reset_index(drop=True)
    return cleaned


def create_state_month_summary(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Create a compact state-month table for trend analysis."""
    preferred_order = [
        "state_abbreviation",
        "state_name",
        "reporting_month",
        "reporting_year",
        "preliminary_or_updated",
        "final_report",
        "total_medicaid_and_chip_enrollment",
        "total_medicaid_enrollment",
        "total_chip_enrollment",
        "medicaid_and_chip_child_enrollment",
        "total_adult_medicaid_enrollment",
        "new_applications_submitted_to_medicaid_and_chip_agencies",
        "total_applications_for_financial_assistance_submitted_at_state_level",
        "individuals_determined_eligible_for_medicaid_at_application",
        "individuals_determined_eligible_for_chip_at_application",
        "total_medicaid_and_chip_determinations",
    ]
    columns = [column for column in preferred_order if column in cleaned.columns]
    return cleaned[columns].copy()


def create_dashboard_sample(summary: pd.DataFrame, recent_months: int = 12) -> pd.DataFrame:
    """Create a small all-state sample from the most recent reporting months."""
    latest_months = (
        summary["reporting_month"]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .tail(recent_months)
    )
    return summary[summary["reporting_month"].isin(latest_months)].copy()


def create_data_quality_summary(
    cleaned: pd.DataFrame,
    raw_row_count: int,
    source_duplicate_count: int,
) -> pd.DataFrame:
    """Create field-level and dataset-level data quality checks."""
    duplicate_count = int(cleaned.duplicated(["state_abbreviation", "reporting_month"]).sum())
    numeric_columns = [column for column in NUMERIC_COLUMNS if column in cleaned.columns]
    negative_count = int((cleaned[numeric_columns] < 0).sum().sum()) if numeric_columns else 0
    zero_count = int((cleaned[numeric_columns] == 0).sum().sum()) if numeric_columns else 0

    field_rows = []
    for column in cleaned.columns:
        missing_count = int(cleaned[column].isna().sum())
        field_rows.append(
            {
                "check_type": "field_missingness",
                "field_name": column,
                "value": missing_count,
                "percent": round(missing_count / len(cleaned) * 100, 2) if len(cleaned) else np.nan,
                "notes": "Missing values counted after filtering to 2019-present and 50 states plus DC.",
            }
        )

    dataset_rows = [
        {
            "check_type": "dataset_summary",
            "field_name": "raw_row_count",
            "value": raw_row_count,
            "percent": np.nan,
            "notes": "Rows in the downloaded CMS source CSV before filtering.",
        },
        {
            "check_type": "dataset_summary",
            "field_name": "cleaned_row_count",
            "value": len(cleaned),
            "percent": np.nan,
            "notes": "Rows after filtering to 2019-present and 50 states plus DC.",
        },
        {
            "check_type": "duplicate_check",
            "field_name": "source_state_abbreviation_reporting_month",
            "value": source_duplicate_count,
            "percent": np.nan,
            "notes": "Duplicate state-month records in the source extract before preferring final/updated reports.",
        },
        {
            "check_type": "duplicate_check",
            "field_name": "cleaned_state_abbreviation_reporting_month",
            "value": duplicate_count,
            "percent": round(duplicate_count / len(cleaned) * 100, 2) if len(cleaned) else np.nan,
            "notes": "Duplicate count at the state-month grain after cleaning.",
        },
        {
            "check_type": "value_check",
            "field_name": "negative_numeric_values",
            "value": negative_count,
            "percent": np.nan,
            "notes": "Negative values across preserved numeric enrollment and operations fields.",
        },
        {
            "check_type": "value_check",
            "field_name": "zero_numeric_values",
            "value": zero_count,
            "percent": np.nan,
            "notes": "Zero values across preserved numeric fields; zeros may be valid or may require source review.",
        },
    ]
    state_month_rows = []
    completeness_fields = [column for column in cleaned.columns if column not in {"reporting_period"}]
    for _, row in cleaned.iterrows():
        missing_count = int(row[completeness_fields].isna().sum())
        state_month_rows.append(
            {
                "check_type": "state_month_missingness",
                "field_name": f"{row['state_abbreviation']}_{row['reporting_month'].date()}",
                "value": missing_count,
                "percent": round(missing_count / len(completeness_fields) * 100, 2),
                "notes": "Missing preserved fields for one state-month record.",
            }
        )

    month_rows = []
    for month, group in cleaned.groupby("reporting_month"):
        state_count = int(group["state_abbreviation"].nunique())
        preliminary_count = int(group["final_report"].ne("Y").sum()) if "final_report" in group else 0
        month_rows.append(
            {
                "check_type": "monthly_completeness",
                "field_name": str(month.date()),
                "value": state_count,
                "percent": round(state_count / len(STATE_ABBREVIATIONS) * 100, 2),
                "notes": (
                    f"State/DC records present for month; preliminary records selected: "
                    f"{preliminary_count}."
                ),
            }
        )

    return pd.DataFrame(dataset_rows + field_rows + month_rows + state_month_rows)


def save_outputs(
    cleaned: pd.DataFrame,
    raw_row_count: int,
    source_duplicate_count: int,
) -> dict[str, Path]:
    """Save cleaned datasets and quality summary outputs."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    summary = create_state_month_summary(cleaned)
    sample = create_dashboard_sample(summary)
    quality = create_data_quality_summary(cleaned, raw_row_count, source_duplicate_count)

    cleaned.to_csv(FULL_CLEAN_PATH, index=False)
    summary.to_csv(STATE_MONTH_SUMMARY_PATH, index=False)
    sample.to_csv(SAMPLE_PATH, index=False)
    quality.to_csv(QUALITY_SUMMARY_PATH, index=False)

    return {
        "cleaned": FULL_CLEAN_PATH,
        "summary": STATE_MONTH_SUMMARY_PATH,
        "sample": SAMPLE_PATH,
        "quality": QUALITY_SUMMARY_PATH,
    }


def main() -> None:
    """Run source download, cleaning, validation, and output creation."""
    save_source_metadata()
    download_source_csv(RAW_CSV_PATH)
    raw = load_raw_data(RAW_CSV_PATH)
    standardized_raw = standardize_column_names(raw)
    standardized_raw["state_abbreviation"] = (
        standardized_raw["state_abbreviation"].astype(str).str.strip().str.upper()
    )
    standardized_raw["reporting_month"] = standardized_raw["reporting_period"].apply(
        parse_reporting_period
    )
    standardized_raw["reporting_year"] = standardized_raw["reporting_month"].dt.year
    filtered_raw = standardized_raw[
        standardized_raw["state_abbreviation"].isin(STATE_ABBREVIATIONS)
        & (standardized_raw["reporting_year"] >= 2019)
    ]
    source_duplicate_count = int(
        filtered_raw.duplicated(["state_abbreviation", "reporting_month"]).sum()
    )
    cleaned = clean_data(raw)
    paths = save_outputs(
        cleaned,
        raw_row_count=len(raw),
        source_duplicate_count=source_duplicate_count,
    )

    print(f"Raw rows: {len(raw):,}")
    print(f"Cleaned rows: {len(cleaned):,}")
    print(f"Date range: {cleaned['reporting_month'].min().date()} to {cleaned['reporting_month'].max().date()}")
    print(f"States/DC: {cleaned['state_abbreviation'].nunique()}")
    for label, path in paths.items():
        print(f"{label}: {path}")


if __name__ == "__main__":
    main()
