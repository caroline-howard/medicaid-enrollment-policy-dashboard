"""Build diagnostic monitoring indicators from validated Medicaid dashboard data."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DASHBOARD_TABLE_DIR = PROJECT_ROOT / "outputs" / "dashboard_tables"

STATE_MONTH_PATH = PROCESSED_DIR / "medicaid_state_month_summary.csv"
POP_ADJUSTED_PATH = DASHBOARD_TABLE_DIR / "state_population_adjusted_metrics.csv"
NATIONAL_ENROLLMENT_PATH = DASHBOARD_TABLE_DIR / "national_enrollment_trend.csv"
NATIONAL_OPS_PATH = DASHBOARD_TABLE_DIR / "national_applications_determinations_trend.csv"
QUALITY_STATE_PATH = DASHBOARD_TABLE_DIR / "data_quality_by_state.csv"

PEAK_OUTPUT = DASHBOARD_TABLE_DIR / "enrollment_change_from_peak.csv"
POP_CONTEXT_OUTPUT = DASHBOARD_TABLE_DIR / "state_population_adjusted_context.csv"
FLAGS_OUTPUT = DASHBOARD_TABLE_DIR / "monitoring_review_flags.csv"
STATE_SUMMARY_OUTPUT = DASHBOARD_TABLE_DIR / "state_monitoring_summary.csv"
NATIONAL_SUMMARY_OUTPUT = DASHBOARD_TABLE_DIR / "national_monitoring_summary.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def number(value: float | None) -> str:
    if value is None or math.isnan(value) or math.isinf(value):
        return ""
    return f"{value:.6f}"


def parse_month(value: str) -> datetime:
    return datetime.strptime(value[:10], "%Y-%m-%d")


def group_state_months(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["state_abbreviation"]].append(row)
    for state_rows in grouped.values():
        state_rows.sort(key=lambda row: parse_month(row["reporting_month"]))
    return grouped


def build_peak_table(grouped: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for state, rows in grouped.items():
        valid_rows = [
            row for row in rows if to_float(row["total_medicaid_and_chip_enrollment"]) is not None
        ]
        peak = max(valid_rows, key=lambda row: to_float(row["total_medicaid_and_chip_enrollment"]) or -math.inf)
        latest = valid_rows[-1]
        peak_value = to_float(peak["total_medicaid_and_chip_enrollment"])
        latest_value = to_float(latest["total_medicaid_and_chip_enrollment"])
        change = latest_value - peak_value if peak_value is not None and latest_value is not None else None
        percent_change = change / peak_value * 100 if peak_value and change is not None else None
        output.append(
            {
                "state_abbreviation": state,
                "state_name": latest["state_name"],
                "peak_enrollment_month": peak["reporting_month"],
                "peak_total_medicaid_chip_enrollment": number(peak_value),
                "latest_reporting_month": latest["reporting_month"],
                "latest_total_medicaid_chip_enrollment": number(latest_value),
                "change_from_peak": number(change),
                "percent_change_from_peak": number(percent_change),
            }
        )
    return sorted(output, key=lambda row: row["state_abbreviation"])


def build_population_context(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output = []
    for row in rows:
        output.append(
            {
                "state_abbreviation": row["state_abbreviation"],
                "state_name": row["state_name"],
                "latest_reporting_month": row["latest_reporting_month"],
                "state_population": row["state_population"],
                "population_year": row["population_denominator_year"],
                "total_medicaid_chip_enrollment_per_1000_residents": row[
                    "medicaid_chip_enrollment_per_1000_residents"
                ],
                "medicaid_enrollment_per_1000_residents": row[
                    "medicaid_enrollment_per_1000_residents"
                ],
                "chip_enrollment_per_1000_residents": row[
                    "chip_enrollment_per_1000_residents"
                ],
                "applications_per_100000_residents": row[
                    "applications_submitted_per_100000_residents"
                ],
                "determinations_per_100000_residents": row[
                    "eligibility_determinations_per_100000_residents"
                ],
            }
        )
    return sorted(output, key=lambda row: row["state_abbreviation"])


def rolling_prior(values: list[float], index: int, window: int = 12) -> list[float]:
    start = max(0, index - window)
    return values[start:index]


def add_flag(
    flags: list[dict[str, object]],
    row: dict[str, str],
    flag_type: str,
    description: str,
    metric_name: str,
    metric_value: float | None,
    comparison_value: float | None,
    note: str,
) -> None:
    flags.append(
        {
            "state_abbreviation": row["state_abbreviation"],
            "state_name": row["state_name"],
            "reporting_month": row["reporting_month"],
            "flag_type": flag_type,
            "flag_description": description,
            "metric_name": metric_name,
            "metric_value": number(metric_value),
            "comparison_value": number(comparison_value),
            "interpretation_note": note,
        }
    )


def build_review_flags(
    grouped: dict[str, list[dict[str, str]]],
    pop_adjusted_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    flags: list[dict[str, object]] = []

    for rows in grouped.values():
        enrollments = [to_float(row["total_medicaid_and_chip_enrollment"]) for row in rows]
        monthly_changes: list[float] = []
        for idx in range(1, len(rows)):
            if enrollments[idx] is None or enrollments[idx - 1] is None:
                monthly_changes.append(math.nan)
            else:
                monthly_changes.append(enrollments[idx] - enrollments[idx - 1])

        valid_changes = [value for value in monthly_changes if not math.isnan(value)]
        if len(valid_changes) >= 3:
            avg_change = mean(valid_changes)
            threshold = 2 * stdev(valid_changes)
            for idx, change in enumerate(monthly_changes, start=1):
                if math.isnan(change):
                    continue
                if abs(change - avg_change) > threshold:
                    add_flag(
                        flags,
                        rows[idx],
                        "large_month_over_month_enrollment_change",
                        "Monthly enrollment change differs from this state's historical monthly pattern.",
                        "monthly_total_medicaid_chip_enrollment_change",
                        change,
                        avg_change,
                        "Review flag only; this does not identify a cause or indicate performance.",
                    )

        applications = [
            to_float(row["total_applications_for_financial_assistance_submitted_at_state_level"])
            for row in rows
        ]
        determinations = [to_float(row["total_medicaid_and_chip_determinations"]) for row in rows]
        for idx, row in enumerate(rows):
            prior_apps = [
                value for value in rolling_prior(applications, idx) if value is not None
            ]
            current_apps = applications[idx]
            if current_apps is not None and len(prior_apps) >= 6 and stdev(prior_apps) > 0:
                comparison = mean(prior_apps)
                if current_apps > comparison + 2 * stdev(prior_apps):
                    add_flag(
                        flags,
                        row,
                        "large_applications_spike",
                        "Applications submitted are above this state's recent monthly pattern.",
                        "total_applications_for_financial_assistance_submitted_at_state_level",
                        current_apps,
                        comparison,
                        "Review flag only; applications are descriptive operational indicators, not performance scores.",
                    )

            prior_dets = [
                value for value in rolling_prior(determinations, idx) if value is not None
            ]
            current_dets = determinations[idx]
            if current_dets is not None and len(prior_dets) >= 6 and stdev(prior_dets) > 0:
                comparison = mean(prior_dets)
                if current_dets > comparison + 2 * stdev(prior_dets):
                    add_flag(
                        flags,
                        row,
                        "large_determinations_spike",
                        "Eligibility determinations are above this state's recent monthly pattern.",
                        "total_medicaid_and_chip_determinations",
                        current_dets,
                        comparison,
                        "Review flag only; determinations are descriptive operational indicators, not performance scores.",
                    )

    latest_month = max(row["latest_reporting_month"] for row in pop_adjusted_rows)
    for row in pop_adjusted_rows:
        latest_row = {
            "state_abbreviation": row["state_abbreviation"],
            "state_name": row["state_name"],
            "reporting_month": row["latest_reporting_month"],
        }
        if row["latest_reporting_month"] == latest_month and row["latest_month_preliminary_status"] != "Final/updated":
            add_flag(
                flags,
                latest_row,
                "latest_month_preliminary_reporting_caution",
                "Latest month is preliminary and may be revised in later source updates.",
                "latest_month_preliminary_status",
                None,
                None,
                "Review flag only; preliminary reporting affects interpretation of the latest month.",
            )
        missingness = to_float(row["missingness_percent"])
        if missingness is not None and missingness > 10:
            add_flag(
                flags,
                latest_row,
                "high_missingness_caution",
                "State has elevated missingness across preserved dashboard fields.",
                "missingness_percent",
                missingness,
                10,
                "Review flag only; missingness should guide caution, not state performance labeling.",
            )

    return sorted(
        flags,
        key=lambda row: (
            row["state_abbreviation"],
            row["reporting_month"],
            row["flag_type"],
        ),
    )


def build_state_summary(
    pop_rows: list[dict[str, str]],
    peak_rows: list[dict[str, object]],
    flags: list[dict[str, object]],
) -> list[dict[str, object]]:
    peak_lookup = {row["state_abbreviation"]: row for row in peak_rows}
    flag_counts: dict[str, int] = defaultdict(int)
    for flag in flags:
        flag_counts[flag["state_abbreviation"]] += 1

    output = []
    for row in pop_rows:
        peak = peak_lookup[row["state_abbreviation"]]
        output.append(
            {
                "state_abbreviation": row["state_abbreviation"],
                "state_name": row["state_name"],
                "latest_reporting_month": row["latest_reporting_month"],
                "latest_total_medicaid_chip_enrollment": row[
                    "latest_total_medicaid_chip_enrollment"
                ],
                "change_since_january_2019": row["change_since_january_2019"],
                "percent_change_since_january_2019": row[
                    "percent_change_since_january_2019"
                ],
                "last_12_month_change": row["last_12_month_change"],
                "last_12_month_percent_change": row["last_12_month_percent_change"],
                "peak_enrollment_month": peak["peak_enrollment_month"],
                "change_from_peak": peak["change_from_peak"],
                "percent_change_from_peak": peak["percent_change_from_peak"],
                "total_medicaid_chip_enrollment_per_1000_residents": row[
                    "medicaid_chip_enrollment_per_1000_residents"
                ],
                "applications_per_100000_residents": row[
                    "applications_submitted_per_100000_residents"
                ],
                "determinations_per_100000_residents": row[
                    "eligibility_determinations_per_100000_residents"
                ],
                "review_flag_count": flag_counts[row["state_abbreviation"]],
                "latest_month_preliminary_status": row[
                    "latest_month_preliminary_status"
                ],
                "missingness_percent": row["missingness_percent"],
            }
        )
    return sorted(output, key=lambda row: row["state_abbreviation"])


def build_national_summary(
    national_enrollment: list[dict[str, str]],
    national_ops: list[dict[str, str]],
    flags: list[dict[str, object]],
) -> list[dict[str, object]]:
    latest_enrollment = national_enrollment[-1]
    latest_ops = national_ops[-1]
    peak = max(
        national_enrollment,
        key=lambda row: to_float(row["total_medicaid_and_chip_enrollment"]) or -math.inf,
    )
    latest_value = to_float(latest_enrollment["total_medicaid_and_chip_enrollment"])
    peak_value = to_float(peak["total_medicaid_and_chip_enrollment"])
    change_from_peak = latest_value - peak_value if latest_value is not None and peak_value is not None else None
    percent_change_from_peak = (
        change_from_peak / peak_value * 100 if change_from_peak is not None and peak_value else None
    )
    flag_counts: dict[str, int] = defaultdict(int)
    for flag in flags:
        flag_counts[flag["flag_type"]] += 1

    return [
        {
            "latest_reporting_month": latest_enrollment["reporting_month"],
            "latest_total_medicaid_chip_enrollment": latest_enrollment[
                "total_medicaid_and_chip_enrollment"
            ],
            "latest_medicaid_enrollment": latest_enrollment[
                "total_medicaid_enrollment"
            ],
            "latest_chip_enrollment": latest_enrollment["total_chip_enrollment"],
            "peak_enrollment_month": peak["reporting_month"],
            "peak_total_medicaid_chip_enrollment": peak[
                "total_medicaid_and_chip_enrollment"
            ],
            "change_from_peak": number(change_from_peak),
            "percent_change_from_peak": number(percent_change_from_peak),
            "latest_applications_submitted": latest_ops["applications_submitted"],
            "latest_total_determinations": latest_ops[
                "total_medicaid_and_chip_determinations"
            ],
            "state_dc_count": latest_enrollment["state_records"],
            "total_review_flags": len(flags),
            "enrollment_change_flag_count": flag_counts[
                "large_month_over_month_enrollment_change"
            ],
            "applications_spike_flag_count": flag_counts["large_applications_spike"],
            "determinations_spike_flag_count": flag_counts[
                "large_determinations_spike"
            ],
            "latest_month_preliminary_flag_count": flag_counts[
                "latest_month_preliminary_reporting_caution"
            ],
            "high_missingness_flag_count": flag_counts["high_missingness_caution"],
            "interpretation_note": "National monitoring summary is descriptive and does not identify causal policy effects.",
        }
    ]


def main() -> None:
    state_month_rows = read_csv(STATE_MONTH_PATH)
    pop_rows = read_csv(POP_ADJUSTED_PATH)
    national_enrollment = read_csv(NATIONAL_ENROLLMENT_PATH)
    national_ops = read_csv(NATIONAL_OPS_PATH)

    grouped = group_state_months(state_month_rows)
    peak_rows = build_peak_table(grouped)
    population_context = build_population_context(pop_rows)
    flags = build_review_flags(grouped, pop_rows)
    state_summary = build_state_summary(pop_rows, peak_rows, flags)
    national_summary = build_national_summary(national_enrollment, national_ops, flags)

    write_csv(
        PEAK_OUTPUT,
        peak_rows,
        [
            "state_abbreviation",
            "state_name",
            "peak_enrollment_month",
            "peak_total_medicaid_chip_enrollment",
            "latest_reporting_month",
            "latest_total_medicaid_chip_enrollment",
            "change_from_peak",
            "percent_change_from_peak",
        ],
    )
    write_csv(
        POP_CONTEXT_OUTPUT,
        population_context,
        [
            "state_abbreviation",
            "state_name",
            "latest_reporting_month",
            "state_population",
            "population_year",
            "total_medicaid_chip_enrollment_per_1000_residents",
            "medicaid_enrollment_per_1000_residents",
            "chip_enrollment_per_1000_residents",
            "applications_per_100000_residents",
            "determinations_per_100000_residents",
        ],
    )
    write_csv(
        FLAGS_OUTPUT,
        flags,
        [
            "state_abbreviation",
            "state_name",
            "reporting_month",
            "flag_type",
            "flag_description",
            "metric_name",
            "metric_value",
            "comparison_value",
            "interpretation_note",
        ],
    )
    write_csv(
        STATE_SUMMARY_OUTPUT,
        state_summary,
        list(state_summary[0].keys()),
    )
    write_csv(
        NATIONAL_SUMMARY_OUTPUT,
        national_summary,
        list(national_summary[0].keys()),
    )

    print(f"Saved {len(peak_rows)} rows to {PEAK_OUTPUT}")
    print(f"Saved {len(population_context)} rows to {POP_CONTEXT_OUTPUT}")
    print(f"Saved {len(flags)} rows to {FLAGS_OUTPUT}")
    print(f"Saved {len(state_summary)} rows to {STATE_SUMMARY_OUTPUT}")
    print(f"Saved {len(national_summary)} row to {NATIONAL_SUMMARY_OUTPUT}")


if __name__ == "__main__":
    main()
