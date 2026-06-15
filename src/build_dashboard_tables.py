"""Build dashboard-ready tables and static EDA figures."""

from __future__ import annotations

import os
import tempfile

os.environ.setdefault(
    "MPLCONFIGDIR",
    str((tempfile.gettempdir())),
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from eda_medicaid import (
    FIGURES_DIR,
    OUTPUT_TABLE_DIR,
    dashboard_notes,
    data_quality_by_field,
    data_quality_by_month,
    data_quality_by_state,
    kpi_summary,
    load_clean_data,
    national_applications_determinations_trend,
    national_enrollment_trend,
    state_eligibility_operations_summary,
    state_enrollment_change,
    state_latest_snapshot,
    top_state_increases,
)


plt.style.use("seaborn-v0_8-whitegrid")


def save_dashboard_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Create and save dashboard-ready CSV tables."""
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    tables = {
        "kpi_summary": kpi_summary(df),
        "national_enrollment_trend": national_enrollment_trend(df),
        "national_applications_determinations_trend": national_applications_determinations_trend(df),
        "state_latest_snapshot": state_latest_snapshot(df),
        "state_enrollment_change": state_enrollment_change(df),
        "state_eligibility_operations_summary": state_eligibility_operations_summary(df),
        "data_quality_by_field": data_quality_by_field(df),
        "data_quality_by_state": data_quality_by_state(df),
        "data_quality_by_month": data_quality_by_month(df),
        "dashboard_notes": dashboard_notes(df),
    }
    for name, table in tables.items():
        table.to_csv(OUTPUT_TABLE_DIR / f"{name}.csv", index=False)
    return tables


def save_figures(tables: dict[str, pd.DataFrame]) -> None:
    """Create static exploratory PNG figures for README and documentation."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    national = tables["national_enrollment_trend"].copy()
    national["reporting_month"] = pd.to_datetime(national["reporting_month"])
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(
        national["reporting_month"],
        national["total_medicaid_and_chip_enrollment"],
        label="Total Medicaid/CHIP",
        linewidth=2.4,
    )
    ax.plot(
        national["reporting_month"],
        national["total_medicaid_enrollment"],
        label="Medicaid",
        linewidth=1.8,
    )
    ax.plot(
        national["reporting_month"],
        national["total_chip_enrollment"],
        label="CHIP",
        linewidth=1.8,
    )
    ax.set_title("National Medicaid/CHIP Enrollment Trend")
    ax.set_xlabel("Reporting month")
    ax.set_ylabel("Enrollment")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "national_enrollment_trend.png", dpi=160)
    plt.close(fig)

    ops = tables["national_applications_determinations_trend"].copy()
    ops["reporting_month"] = pd.to_datetime(ops["reporting_month"])
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(
        ops["reporting_month"],
        ops["applications_submitted"],
        label="Applications submitted",
        linewidth=2.2,
    )
    ax.plot(
        ops["reporting_month"],
        ops["total_medicaid_and_chip_determinations"],
        label="Eligibility determinations",
        linewidth=2.2,
    )
    ax.set_title("National Applications And Eligibility Determinations")
    ax.set_xlabel("Reporting month")
    ax.set_ylabel("Monthly count")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "applications_determinations_trend.png", dpi=160)
    plt.close(fig)

    changes = top_state_increases(tables["state_enrollment_change"], 10).sort_values(
        "change_since_baseline"
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(changes["state_abbreviation"], changes["change_since_baseline"])
    ax.set_title("Top State Medicaid/CHIP Enrollment Increases Since Jan 2019")
    ax.set_xlabel("Enrollment change")
    ax.set_ylabel("State")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "top_state_enrollment_changes.png", dpi=160)
    plt.close(fig)

    quality = tables["data_quality_by_field"].head(10).sort_values("missing_percent")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(quality["field_name"], quality["missing_percent"])
    ax.set_title("Highest Missingness By Field")
    ax.set_xlabel("Missing percent")
    ax.set_ylabel("Field")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "data_quality_missingness.png", dpi=160)
    plt.close(fig)


def main() -> None:
    """Build all dashboard tables and figures."""
    df = load_clean_data()
    tables = save_dashboard_tables(df)
    save_figures(tables)
    print(f"Dashboard tables saved to {OUTPUT_TABLE_DIR}")
    print(f"Figures saved to {FIGURES_DIR}")
    for name, table in tables.items():
        print(f"{name}: {len(table):,} rows")


if __name__ == "__main__":
    main()
