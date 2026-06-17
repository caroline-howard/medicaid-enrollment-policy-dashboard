"""Build Application-Determination Balance operations metrics."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DASHBOARD_TABLE_DIR = PROJECT_ROOT / "outputs" / "dashboard_tables"

STATE_MONTH_PATH = PROCESSED_DIR / "medicaid_state_month_summary.csv"
POPULATION_PATH = PROCESSED_DIR / "state_population_denominators.csv"
POP_ADJUSTED_PATH = DASHBOARD_TABLE_DIR / "state_population_adjusted_metrics.csv"

BALANCE_OUTPUT = DASHBOARD_TABLE_DIR / "application_determination_balance.csv"
LATEST_OUTPUT = DASHBOARD_TABLE_DIR / "application_determination_balance_latest.csv"
SUMMARY_OUTPUT = DASHBOARD_TABLE_DIR / "application_determination_balance_summary.csv"
NATIONAL_OUTPUT = DASHBOARD_TABLE_DIR / "national_application_determination_balance_trend.csv"
TOP_STATES_OUTPUT = DASHBOARD_TABLE_DIR / "top_application_determination_balance_states.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def number(value: float | None) -> str:
    if value is None or math.isnan(value) or math.isinf(value):
        return ""
    return f"{value:.6f}"


def population_lookup(population_rows: list[dict[str, str]]) -> dict[tuple[str, int], dict[str, str]]:
    return {
        (row["state_abbreviation"], int(row["population_year"])): row
        for row in population_rows
    }


def select_population(
    lookup: dict[tuple[str, int], dict[str, str]],
    state: str,
    reporting_year: int,
) -> dict[str, str] | None:
    available_years = sorted(year for state_code, year in lookup if state_code == state)
    if not available_years:
        return None
    eligible_years = [year for year in available_years if year <= reporting_year]
    selected_year = eligible_years[-1] if eligible_years else available_years[0]
    return lookup[(state, selected_year)]


def safe_rate(numerator: float | None, denominator: float | None, multiplier: int) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return numerator / denominator * multiplier


def build_balance_rows() -> list[dict[str, object]]:
    state_month_rows = read_csv(STATE_MONTH_PATH)
    population_rows = read_csv(POPULATION_PATH)
    pop_lookup = population_lookup(population_rows)

    output: list[dict[str, object]] = []
    for row in state_month_rows:
        applications = to_float(
            row["total_applications_for_financial_assistance_submitted_at_state_level"]
        )
        determinations = to_float(row["total_medicaid_and_chip_determinations"])
        enrollment = to_float(row["total_medicaid_and_chip_enrollment"])
        balance = (
            applications - determinations
            if applications is not None and determinations is not None
            else None
        )
        population = select_population(
            pop_lookup,
            row["state_abbreviation"],
            int(row["reporting_year"]),
        )
        state_population = to_float(population["state_population"]) if population else None
        determinations_per_application = safe_rate(determinations, applications, 1)
        applications_per_1000_enrollees = safe_rate(applications, enrollment, 1000)
        determinations_per_1000_enrollees = safe_rate(determinations, enrollment, 1000)

        output.append(
            {
                "state_abbreviation": row["state_abbreviation"],
                "state_name": row["state_name"],
                "reporting_month": row["reporting_month"],
                "applications_submitted": number(applications),
                "total_medicaid_chip_determinations": number(determinations),
                "application_determination_balance": number(balance),
                "state_population": population["state_population"] if population else "",
                "population_year": population["population_year"] if population else "",
                "application_determination_balance_per_100000_residents": number(
                    safe_rate(balance, state_population, 100000)
                ),
                "determinations_per_application": number(determinations_per_application),
                "applications_per_1000_enrollees": number(applications_per_1000_enrollees),
                "determinations_per_1000_enrollees": number(determinations_per_1000_enrollees),
                "latest_month_preliminary_status": "Final/updated"
                if row["final_report"] == "Y"
                else "Preliminary",
            }
        )
    return output


def latest_rows(balance_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    latest_month = max(str(row["reporting_month"]) for row in balance_rows)
    pop_adjusted = {
        row["state_abbreviation"]: row for row in read_csv(POP_ADJUSTED_PATH)
    }
    output = []
    for row in balance_rows:
        if row["reporting_month"] != latest_month:
            continue
        quality = pop_adjusted.get(str(row["state_abbreviation"]), {})
        output.append(
            {
                "state_abbreviation": row["state_abbreviation"],
                "state_name": row["state_name"],
                "latest_reporting_month": row["reporting_month"],
                "applications_submitted": row["applications_submitted"],
                "total_medicaid_chip_determinations": row[
                    "total_medicaid_chip_determinations"
                ],
                "application_determination_balance": row[
                    "application_determination_balance"
                ],
                "application_determination_balance_per_100000_residents": row[
                    "application_determination_balance_per_100000_residents"
                ],
                "determinations_per_application": row["determinations_per_application"],
                "data_quality_note": quality.get("data_quality_note", ""),
            }
        )
    return sorted(output, key=lambda item: item["state_abbreviation"])


def national_trend(balance_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in balance_rows:
        grouped[str(row["reporting_month"])].append(row)

    output = []
    for month, rows in sorted(grouped.items()):
        applications = sum(to_float(str(row["applications_submitted"])) or 0 for row in rows)
        determinations = sum(
            to_float(str(row["total_medicaid_chip_determinations"])) or 0 for row in rows
        )
        balance = applications - determinations
        population = sum(to_float(str(row["state_population"])) or 0 for row in rows)
        output.append(
            {
                "reporting_month": month,
                "applications_submitted": number(applications),
                "total_medicaid_chip_determinations": number(determinations),
                "application_determination_balance": number(balance),
                "national_population_denominator": number(population),
                "application_determination_balance_per_100000_residents": number(
                    safe_rate(balance, population, 100000)
                ),
                "state_records": len(rows),
            }
        )
    return output


def top_states(latest: list[dict[str, object]]) -> list[dict[str, object]]:
    ranked = sorted(
        latest,
        key=lambda row: to_float(str(row["application_determination_balance_per_100000_residents"]))
        or 0,
        reverse=True,
    )
    output = []
    for direction, rows in [
        ("highest_positive_balance_per_100000_residents", ranked[:10]),
        ("highest_negative_balance_per_100000_residents", list(reversed(ranked[-10:]))),
    ]:
        for rank, row in enumerate(rows, start=1):
            output.append(
                {
                    "direction": direction,
                    "rank": rank,
                    "state_abbreviation": row["state_abbreviation"],
                    "state_name": row["state_name"],
                    "latest_reporting_month": row["latest_reporting_month"],
                    "application_determination_balance": row[
                        "application_determination_balance"
                    ],
                    "application_determination_balance_per_100000_residents": row[
                        "application_determination_balance_per_100000_residents"
                    ],
                }
            )
    return output


def summary_rows(
    balance_rows: list[dict[str, object]],
    latest: list[dict[str, object]],
    national: list[dict[str, object]],
) -> list[dict[str, object]]:
    latest_values = [
        to_float(str(row["application_determination_balance_per_100000_residents"]))
        for row in latest
        if to_float(str(row["application_determination_balance_per_100000_residents"])) is not None
    ]
    all_balances = [
        to_float(str(row["application_determination_balance"]))
        for row in balance_rows
        if to_float(str(row["application_determination_balance"])) is not None
    ]
    latest_national = national[-1]
    return [
        {
            "state_month_rows": len(balance_rows),
            "latest_state_rows": len(latest),
            "national_month_rows": len(national),
            "latest_reporting_month": latest_national["reporting_month"],
            "latest_national_application_determination_balance": latest_national[
                "application_determination_balance"
            ],
            "latest_national_balance_per_100000_residents": latest_national[
                "application_determination_balance_per_100000_residents"
            ],
            "latest_state_balance_per_100000_min": number(min(latest_values)),
            "latest_state_balance_per_100000_median": number(median(latest_values)),
            "latest_state_balance_per_100000_max": number(max(latest_values)),
            "all_state_month_balance_min": number(min(all_balances)),
            "all_state_month_balance_median": number(median(all_balances)),
            "all_state_month_balance_max": number(max(all_balances)),
            "interpretation_note": (
                "Application-Determination Balance is descriptive and should not be interpreted "
                "as backlog, timeliness, approval rate, or performance."
            ),
        }
    ]


def validate(balance_rows: list[dict[str, object]], latest: list[dict[str, object]]) -> None:
    if len(balance_rows) != 4386:
        raise ValueError(f"Expected 4,386 state-month rows, found {len(balance_rows)}")
    if len(latest) != 51:
        raise ValueError(f"Expected 51 latest state rows, found {len(latest)}")
    numeric_fields = [
        "application_determination_balance",
        "application_determination_balance_per_100000_residents",
        "determinations_per_application",
        "applications_per_1000_enrollees",
        "determinations_per_1000_enrollees",
    ]
    for row in balance_rows:
        for field in numeric_fields:
            value = to_float(str(row[field]))
            if value is not None and (math.isnan(value) or math.isinf(value)):
                raise ValueError(f"Invalid numeric value in {field}")


def main() -> None:
    balance = build_balance_rows()
    latest = latest_rows(balance)
    national = national_trend(balance)
    top = top_states(latest)
    summary = summary_rows(balance, latest, national)
    validate(balance, latest)

    write_csv(BALANCE_OUTPUT, balance, list(balance[0].keys()))
    write_csv(LATEST_OUTPUT, latest, list(latest[0].keys()))
    write_csv(NATIONAL_OUTPUT, national, list(national[0].keys()))
    write_csv(TOP_STATES_OUTPUT, top, list(top[0].keys()))
    write_csv(SUMMARY_OUTPUT, summary, list(summary[0].keys()))

    print(f"Saved {len(balance):,} rows to {BALANCE_OUTPUT}")
    print(f"Saved {len(latest):,} rows to {LATEST_OUTPUT}")
    print(f"Saved {len(national):,} rows to {NATIONAL_OUTPUT}")
    print(f"Saved {len(top):,} rows to {TOP_STATES_OUTPUT}")
    print(f"Saved {len(summary):,} row to {SUMMARY_OUTPUT}")


if __name__ == "__main__":
    main()
