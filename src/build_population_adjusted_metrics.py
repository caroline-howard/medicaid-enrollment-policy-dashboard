"""Build state population-adjusted Medicaid dashboard metrics."""

from __future__ import annotations

import csv
import math
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_TABLE_DIR = PROJECT_ROOT / "outputs" / "dashboard_tables"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
POPULATION_PATH = PROCESSED_DIR / "state_population_denominators.csv"
STATE_MAP_PATH = DASHBOARD_TABLE_DIR / "state_map_metrics.csv"
OUTPUT_PATH = DASHBOARD_TABLE_DIR / "state_population_adjusted_metrics.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def to_float(value: str | None) -> float:
    if value is None or value == "":
        return math.nan
    return float(value)


def per_denominator(numerator: str, denominator: str, multiplier: int) -> float:
    numerator_value = to_float(numerator)
    denominator_value = to_float(denominator)
    if math.isnan(numerator_value) or math.isnan(denominator_value) or denominator_value <= 0:
        return math.nan
    return numerator_value / denominator_value * multiplier


def format_number(value: float) -> str:
    if math.isnan(value) or math.isinf(value):
        return ""
    return f"{value:.6f}"


def latest_population_by_state(population_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for row in population_rows:
        state = row["state_abbreviation"]
        year = int(row["population_year"])
        if state not in latest or year > int(latest[state]["population_year"]):
            latest[state] = row
    return latest


def build_population_adjusted_metrics() -> list[dict[str, str]]:
    state_rows = read_csv(STATE_MAP_PATH)
    population_lookup = latest_population_by_state(read_csv(POPULATION_PATH))
    output: list[dict[str, str]] = []

    for row in state_rows:
        state = row["state_abbreviation"]
        population = population_lookup.get(state)
        if population is None:
            raise ValueError(f"Missing population denominator for {state}")

        state_population = population["state_population"]
        adjusted = {
            "state_abbreviation": state,
            "state_name": row["state_name"],
            "latest_reporting_month": row["latest_reporting_month"],
            "latest_total_medicaid_chip_enrollment": row["latest_total_medicaid_chip_enrollment"],
            "latest_medicaid_enrollment": row["latest_medicaid_enrollment"],
            "latest_chip_enrollment": row["latest_chip_enrollment"],
            "state_population": state_population,
            "population_denominator_year": population["population_year"],
            "population_denominator_source": population["source_name"],
            "population_source_url": population["source_url"],
            "population_date_accessed": population["date_accessed"],
            "population_notes": population["population_notes"],
            "applications_per_1000_enrollees": row["applications_per_1000_enrollees"],
            "determinations_per_1000_enrollees": row["determinations_per_1000_enrollees"],
            "determinations_per_application": row["determinations_per_application"],
            "change_since_january_2019": row["change_since_january_2019"],
            "percent_change_since_january_2019": row["percent_change_since_january_2019"],
            "last_12_month_change": row["last_12_month_change"],
            "last_12_month_percent_change": row["last_12_month_percent_change"],
            "latest_applications_submitted": row["latest_applications_submitted"],
            "latest_total_determinations": row["latest_total_determinations"],
            "latest_month_preliminary_status": row["latest_month_preliminary_status"],
            "missingness_percent": row["missingness_percent"],
            "data_quality_note": row["data_quality_note"],
        }

        metrics = {
            "medicaid_chip_enrollment_per_1000_residents": per_denominator(
                row["latest_total_medicaid_chip_enrollment"], state_population, 1000
            ),
            "medicaid_enrollment_per_1000_residents": per_denominator(
                row["latest_medicaid_enrollment"], state_population, 1000
            ),
            "chip_enrollment_per_1000_residents": per_denominator(
                row["latest_chip_enrollment"], state_population, 1000
            ),
            "applications_submitted_per_100000_residents": per_denominator(
                row["latest_applications_submitted"], state_population, 100000
            ),
            "eligibility_determinations_per_100000_residents": per_denominator(
                row["latest_total_determinations"], state_population, 100000
            ),
        }
        for name, value in metrics.items():
            adjusted[name] = format_number(value)

        adjusted["map_medicaid_chip_enrollment_per_1000_residents"] = adjusted[
            "medicaid_chip_enrollment_per_1000_residents"
        ]
        adjusted["map_medicaid_enrollment_per_1000_residents"] = adjusted[
            "medicaid_enrollment_per_1000_residents"
        ]
        adjusted["map_chip_enrollment_per_1000_residents"] = adjusted[
            "chip_enrollment_per_1000_residents"
        ]
        adjusted["map_applications_per_100000_residents"] = adjusted[
            "applications_submitted_per_100000_residents"
        ]
        adjusted["map_determinations_per_100000_residents"] = adjusted[
            "eligibility_determinations_per_100000_residents"
        ]
        output.append(adjusted)

    if len(output) != 51:
        raise ValueError(f"Expected 51 state/DC rows, found {len(output)}")
    return sorted(output, key=lambda item: item["state_abbreviation"])


def main() -> None:
    output = build_population_adjusted_metrics()
    DASHBOARD_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(output[0].keys()))
        writer.writeheader()
        writer.writerows(output)
    print(f"Saved {len(output):,} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
