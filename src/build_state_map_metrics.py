"""Build state-level metrics for the future State Map Explorer."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_TABLE_DIR = PROJECT_ROOT / "outputs" / "dashboard_tables"
OUTPUT_PATH = DASHBOARD_TABLE_DIR / "state_map_metrics.csv"

USPS_STATES_DC = {
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


def read_table(name: str) -> pd.DataFrame:
    """Read a dashboard-ready table by base file name."""
    return pd.read_csv(DASHBOARD_TABLE_DIR / f"{name}.csv")


def build_state_map_metrics() -> pd.DataFrame:
    """Create one state/DC row with map-ready enrollment, operations, and quality fields."""
    latest = read_table("state_latest_snapshot")
    change = read_table("state_enrollment_change")
    ops = read_table("state_eligibility_operations_summary")
    quality = read_table("data_quality_by_state")

    latest_cols = [
        "state_abbreviation",
        "state_name",
        "reporting_month",
        "preliminary_or_updated",
        "final_report",
        "total_medicaid_and_chip_enrollment",
        "total_medicaid_enrollment",
        "total_chip_enrollment",
        "total_applications_for_financial_assistance_submitted_at_state_level",
        "total_medicaid_and_chip_determinations",
        "national_enrollment_rank",
    ]
    change_cols = [
        "state_abbreviation",
        "change_since_baseline",
        "percent_change_since_baseline",
        "change_last_12_months",
        "percent_change_last_12_months",
    ]
    ops_cols = [
        "state_abbreviation",
        "determinations_per_application",
        "applications_per_1000_average_enrollees",
        "determinations_per_1000_average_enrollees",
    ]
    quality_cols = [
        "state_abbreviation",
        "missing_value_percent",
        "preliminary_records",
    ]

    df = (
        latest[latest_cols]
        .merge(change[change_cols], on="state_abbreviation", how="left")
        .merge(ops[ops_cols], on="state_abbreviation", how="left")
        .merge(quality[quality_cols], on="state_abbreviation", how="left")
    )

    df = df.rename(
        columns={
            "reporting_month": "latest_reporting_month",
            "total_medicaid_and_chip_enrollment": "latest_total_medicaid_chip_enrollment",
            "total_medicaid_enrollment": "latest_medicaid_enrollment",
            "total_chip_enrollment": "latest_chip_enrollment",
            "change_since_baseline": "change_since_january_2019",
            "percent_change_since_baseline": "percent_change_since_january_2019",
            "change_last_12_months": "last_12_month_change",
            "percent_change_last_12_months": "last_12_month_percent_change",
            "total_applications_for_financial_assistance_submitted_at_state_level": "latest_applications_submitted",
            "total_medicaid_and_chip_determinations": "latest_total_determinations",
            "applications_per_1000_average_enrollees": "applications_per_1000_enrollees",
            "determinations_per_1000_average_enrollees": "determinations_per_1000_enrollees",
            "missing_value_percent": "missingness_percent",
        }
    )

    df["latest_month_preliminary_status"] = np.where(
        df["final_report"].eq("Y"), "Final/updated", "Preliminary"
    )
    df["missingness_rank"] = df["missingness_percent"].rank(
        ascending=False, method="min"
    )
    df["caution_flag"] = (
        df["latest_month_preliminary_status"].eq("Preliminary")
        | df["missingness_percent"].gt(10)
    )
    df["data_quality_note"] = np.where(
        df["latest_month_preliminary_status"].eq("Preliminary"),
        "Latest month is preliminary; interpret current values cautiously.",
        "Latest month is final/updated in the current table.",
    )
    df.loc[df["missingness_percent"].gt(10), "data_quality_note"] = (
        df["data_quality_note"]
        + " State has elevated missingness across preserved fields."
    )

    df["map_latest_enrollment"] = df["latest_total_medicaid_chip_enrollment"]
    df["map_percent_change_since_2019"] = df["percent_change_since_january_2019"]
    df["map_last_12_month_change"] = df["last_12_month_change"]
    df["map_applications_per_1000_enrollees"] = df["applications_per_1000_enrollees"]
    df["map_determinations_per_1000_enrollees"] = df[
        "determinations_per_1000_enrollees"
    ]
    df["map_missingness_percent"] = df["missingness_percent"]

    ordered_columns = [
        "state_abbreviation",
        "state_name",
        "latest_reporting_month",
        "latest_total_medicaid_chip_enrollment",
        "latest_medicaid_enrollment",
        "latest_chip_enrollment",
        "national_enrollment_rank",
        "change_since_january_2019",
        "percent_change_since_january_2019",
        "last_12_month_change",
        "last_12_month_percent_change",
        "latest_applications_submitted",
        "latest_total_determinations",
        "determinations_per_application",
        "applications_per_1000_enrollees",
        "determinations_per_1000_enrollees",
        "missingness_percent",
        "missingness_rank",
        "latest_month_preliminary_status",
        "caution_flag",
        "data_quality_note",
        "map_latest_enrollment",
        "map_percent_change_since_2019",
        "map_last_12_month_change",
        "map_applications_per_1000_enrollees",
        "map_determinations_per_1000_enrollees",
        "map_missingness_percent",
    ]
    return df[ordered_columns].sort_values("state_abbreviation").reset_index(drop=True)


def validate_state_map_metrics(df: pd.DataFrame) -> dict[str, object]:
    """Validate state-map table structure and metric conventions."""
    map_metric_fields = [
        "map_latest_enrollment",
        "map_percent_change_since_2019",
        "map_last_12_month_change",
        "map_applications_per_1000_enrollees",
        "map_determinations_per_1000_enrollees",
        "map_missingness_percent",
    ]
    percent_fields = [
        "percent_change_since_january_2019",
        "last_12_month_percent_change",
        "missingness_percent",
        "map_percent_change_since_2019",
        "map_missingness_percent",
    ]
    allowed_negative_fields = {
        "change_since_january_2019",
        "percent_change_since_january_2019",
        "last_12_month_change",
        "last_12_month_percent_change",
        "map_percent_change_since_2019",
        "map_last_12_month_change",
    }

    numeric_columns = df.select_dtypes(include="number").columns
    unexpected_negative_fields = [
        column
        for column in numeric_columns
        if column not in allowed_negative_fields and (df[column] < 0).any()
    ]
    results = {
        "row_count": len(df),
        "expected_row_count": 51,
        "one_row_per_state_dc": len(df) == 51,
        "duplicate_state_abbreviation_count": int(df["state_abbreviation"].duplicated().sum()),
        "invalid_state_abbreviations": sorted(set(df["state_abbreviation"]) - USPS_STATES_DC),
        "latest_reporting_month_missing_count": int(df["latest_reporting_month"].isna().sum()),
        "map_metric_fields_numeric": {
            field: pd.api.types.is_numeric_dtype(df[field]) for field in map_metric_fields
        },
        "percent_convention": "Percent fields are represented on a 0-100 scale.",
        "infinite_value_count": int(np.isinf(df[numeric_columns]).sum().sum()),
        "unexpected_negative_fields": unexpected_negative_fields,
        "allowed_negative_fields": sorted(allowed_negative_fields),
    }
    return results


def main() -> None:
    """Build, validate, and save state map metrics."""
    df = build_state_map_metrics()
    validation = validate_state_map_metrics(df)
    if validation["row_count"] != validation["expected_row_count"]:
        raise ValueError(f"Expected 51 rows, found {validation['row_count']}")
    if validation["duplicate_state_abbreviation_count"]:
        raise ValueError("Duplicate state_abbreviation values found")
    if validation["invalid_state_abbreviations"]:
        raise ValueError(
            f"Invalid state abbreviations: {validation['invalid_state_abbreviations']}"
        )
    if validation["latest_reporting_month_missing_count"]:
        raise ValueError("latest_reporting_month contains missing values")
    if validation["infinite_value_count"]:
        raise ValueError("Infinite values found in numeric fields")
    if validation["unexpected_negative_fields"]:
        raise ValueError(
            f"Unexpected negative values found in {validation['unexpected_negative_fields']}"
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {OUTPUT_PATH}")
    print(validation)


if __name__ == "__main__":
    main()
