#!/usr/bin/env python3
"""Create two-baseline enrollment sensitivity review outputs.

The analysis compares state Medicaid/CHIP enrollment changes using two
baselines:
- January 2019, the first month in the dashboard series
- February 2020, a pre-pandemic comparison month often used in public reporting

Outputs are review artifacts only and do not modify the dashboard or writing
sample.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_MONTH_CSV = ROOT / "data/processed/medicaid_state_month_summary.csv"
OUTPUT_DIR = ROOT / "data/outputs"

JAN_2019 = "2019-01-01"
FEB_2020 = "2020-02-01"
FEB_2026 = "2026-02-01"
FEB_2020_COMPARISON_LIST = {
    "AK",
    "AZ",
    "AR",
    "CO",
    "FL",
    "ID",
    "IA",
    "LA",
    "MA",
    "MI",
    "MT",
    "NH",
    "NM",
    "RI",
    "SC",
    "TN",
    "TX",
    "VT",
    "WV",
    "DC",
}


def parse_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def pct_change(start: float | None, end: float | None) -> float | None:
    if start in (None, 0) or end is None:
        return None
    return (end - start) / start * 100


def pct_decline(peak: float | None, current: float | None) -> float | None:
    if peak in (None, 0) or current is None:
        return None
    return (peak - current) / peak * 100


def fmt_count(value: float | None) -> str:
    return "" if value is None else f"{int(round(value)):,}"


def fmt_signed_count(value: float | None) -> str:
    if value is None:
        return ""
    sign = "+" if value >= 0 else "-"
    return f"{sign}{abs(int(round(value))):,}"


def fmt_pct(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.1f}%"


def fmt_signed_pct(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:+.1f}%"


def read_monthly_rows() -> list[dict]:
    rows = []
    with STATE_MONTH_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "state": row["state_name"],
                    "state_abbr": row["state_abbreviation"],
                    "month": row["reporting_month"],
                    "total": parse_float(row["total_medicaid_and_chip_enrollment"]),
                    "medicaid": parse_float(row["total_medicaid_enrollment"]),
                    "chip": parse_float(row["total_chip_enrollment"]),
                    "child": parse_float(row["medicaid_and_chip_child_enrollment"]),
                }
            )
    return rows


def rows_by_state(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["state_abbr"]].append(row)
    for values in grouped.values():
        values.sort(key=lambda item: item["month"])
    return grouped


def find_month(rows: list[dict], month: str) -> dict:
    match = next((row for row in rows if row["month"] == month), None)
    if match is None:
        raise ValueError(f"Missing month {month}")
    return match


def state_sensitivity_rows(grouped: dict[str, list[dict]]) -> list[dict]:
    output = []
    for abbr, rows in sorted(grouped.items(), key=lambda item: item[1][0]["state"]):
        jan = find_month(rows, JAN_2019)
        feb20 = find_month(rows, FEB_2020)
        feb26 = find_month(rows, FEB_2026)
        jan_raw = feb26["total"] - jan["total"]
        feb20_raw = feb26["total"] - feb20["total"]
        output.append(
            {
                "state": jan["state"],
                "state_abbr": abbr,
                "january_2019_total_medicaid_chip_enrollment": jan["total"],
                "february_2020_total_medicaid_chip_enrollment": feb20["total"],
                "february_2026_total_medicaid_chip_enrollment": feb26["total"],
                "raw_change_jan_2019_to_feb_2026": jan_raw,
                "percent_change_jan_2019_to_feb_2026": pct_change(
                    jan["total"], feb26["total"]
                ),
                "below_january_2019_baseline": "yes" if feb26["total"] < jan["total"] else "no",
                "raw_change_feb_2020_to_feb_2026": feb20_raw,
                "percent_change_feb_2020_to_feb_2026": pct_change(
                    feb20["total"], feb26["total"]
                ),
                "below_february_2020_baseline": "yes"
                if feb26["total"] < feb20["total"]
                else "no",
            }
        )
    return output


def national_by_month(rows: list[dict], measure: str) -> dict[str, float]:
    values: dict[str, float] = defaultdict(float)
    for row in rows:
        value = row[measure]
        if value is not None:
            values[row["month"]] += value
    return dict(values)


def national_measure_summary(rows: list[dict]) -> list[dict]:
    specs = [
        ("total Medicaid/CHIP enrollment", "total", FEB_2020),
        ("Medicaid enrollment", "medicaid", JAN_2019),
        ("CHIP enrollment", "chip", JAN_2019),
        ("child Medicaid/CHIP enrollment", "child", FEB_2020),
    ]
    output = []
    for label, field, baseline_month in specs:
        by_month = national_by_month(rows, field)
        if baseline_month not in by_month or FEB_2026 not in by_month:
            continue
        peak_month, peak_value = max(by_month.items(), key=lambda item: item[1])
        baseline = by_month[baseline_month]
        latest = by_month[FEB_2026]
        output.append(
            {
                "measure": label,
                "baseline_month": baseline_month,
                "baseline_enrollment": baseline,
                "peak_month": peak_month,
                "peak_enrollment": peak_value,
                "february_2026_enrollment": latest,
                "raw_change_baseline_to_feb_2026": latest - baseline,
                "percent_change_baseline_to_feb_2026": pct_change(baseline, latest),
                "raw_decline_peak_to_feb_2026": peak_value - latest,
                "percent_decline_peak_to_feb_2026": pct_decline(peak_value, latest),
            }
        )
    return output


def baseline_summary_rows(state_rows: list[dict], all_rows: list[dict]) -> list[dict]:
    summaries = []
    national_total = national_by_month(all_rows, "total")
    configs = [
        (
            JAN_2019,
            "below_january_2019_baseline",
            "percent_change_jan_2019_to_feb_2026",
            "raw_change_jan_2019_to_feb_2026",
        ),
        (
            FEB_2020,
            "below_february_2020_baseline",
            "percent_change_feb_2020_to_feb_2026",
            "raw_change_feb_2020_to_feb_2026",
        ),
    ]
    for baseline_month, below_field, pct_field, raw_field in configs:
        below = [row for row in state_rows if row[below_field] == "yes"]
        lowest = min(state_rows, key=lambda row: row[pct_field])
        highest = max(state_rows, key=lambda row: row[pct_field])
        baseline_total = national_total[baseline_month]
        latest_total = national_total[FEB_2026]
        summaries.append(
            {
                "baseline_month": baseline_month,
                "number_of_states_plus_dc_below_baseline_by_february_2026": len(below),
                "states_plus_dc_below_baseline": "; ".join(
                    row["state_abbr"] for row in below
                ),
                "lowest_percent_change_state": lowest["state_abbr"],
                "lowest_percent_change": lowest[pct_field],
                "highest_percent_change_state": highest["state_abbr"],
                "highest_percent_change": highest[pct_field],
                "national_total_enrollment_at_baseline": baseline_total,
                "national_total_enrollment_february_2026": latest_total,
                "national_raw_change": latest_total - baseline_total,
                "national_percent_change": pct_change(baseline_total, latest_total),
            }
        )
    return summaries


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def review_note(
    state_rows: list[dict], summaries: list[dict], national_rows: list[dict]
) -> str:
    by_baseline = {row["baseline_month"]: row for row in summaries}
    jan_below = by_baseline[JAN_2019]["states_plus_dc_below_baseline"].split("; ")
    feb20_below = by_baseline[FEB_2020]["states_plus_dc_below_baseline"].split("; ")
    feb20_set = set(feb20_below)
    comparison_match = feb20_set == FEB_2020_COMPARISON_LIST
    missing_from_output = sorted(FEB_2020_COMPARISON_LIST - feb20_set)
    extra_in_output = sorted(feb20_set - FEB_2020_COMPARISON_LIST)

    national_lookup = {row["measure"]: row for row in national_rows}
    child = national_lookup.get("child Medicaid/CHIP enrollment")
    child_sentence = "Child Medicaid/CHIP enrollment was not available."
    if child:
        child_below = child["february_2026_enrollment"] < child["baseline_enrollment"]
        child_sentence = (
            f"Child Medicaid/CHIP enrollment {'fell below' if child_below else 'did not fall below'} "
            f"February 2020 by February 2026: {fmt_count(child['baseline_enrollment'])} "
            f"to {fmt_count(child['february_2026_enrollment'])} "
            f"({fmt_signed_count(child['raw_change_baseline_to_feb_2026'])}; "
            f"{fmt_signed_pct(child['percent_change_baseline_to_feb_2026'])})."
        )

    raw_lines = []
    for row in national_rows:
        raw_lines.append(
            f"- {row['measure']} ({row['baseline_month']} baseline): "
            f"{fmt_count(row['baseline_enrollment'])} at baseline; "
            f"peak {fmt_count(row['peak_enrollment'])} in {row['peak_month']}; "
            f"February 2026 {fmt_count(row['february_2026_enrollment'])}; "
            f"baseline-to-February 2026 {fmt_signed_count(row['raw_change_baseline_to_feb_2026'])} "
            f"({fmt_signed_pct(row['percent_change_baseline_to_feb_2026'])}); "
            f"peak-to-February 2026 decline {fmt_count(row['raw_decline_peak_to_feb_2026'])} "
            f"({fmt_pct(row['percent_decline_peak_to_feb_2026'])})."
        )

    return f"""# Baseline Sensitivity Review

Generated by `scripts/analyze_baseline_sensitivity.py`.

## January 2019 baseline

- States plus DC below January 2019 baseline by February 2026: {by_baseline[JAN_2019]['number_of_states_plus_dc_below_baseline_by_february_2026']}
- States below baseline: {by_baseline[JAN_2019]['states_plus_dc_below_baseline']}
- Largest decline: {by_baseline[JAN_2019]['lowest_percent_change_state']} ({fmt_signed_pct(by_baseline[JAN_2019]['lowest_percent_change'])})
- Largest increase: {by_baseline[JAN_2019]['highest_percent_change_state']} ({fmt_signed_pct(by_baseline[JAN_2019]['highest_percent_change'])})

## February 2020 baseline

- States plus DC below February 2020 baseline by February 2026: {by_baseline[FEB_2020]['number_of_states_plus_dc_below_baseline_by_february_2026']}
- States below baseline: {by_baseline[FEB_2020]['states_plus_dc_below_baseline']}
- Largest decline: {by_baseline[FEB_2020]['lowest_percent_change_state']} ({fmt_signed_pct(by_baseline[FEB_2020]['lowest_percent_change'])})
- Largest increase: {by_baseline[FEB_2020]['highest_percent_change_state']} ({fmt_signed_pct(by_baseline[FEB_2020]['highest_percent_change'])})
- Does the February 2020 below-baseline list match the comparison list? {'yes' if comparison_match else 'no'}
- Missing from output compared with comparison list: {', '.join(missing_from_output) if missing_from_output else 'none'}
- Extra in output compared with comparison list: {', '.join(extra_in_output) if extra_in_output else 'none'}

## Child enrollment check

{child_sentence}

## National raw counts for possible National Trend revision

{chr(10).join(raw_lines)}

## Interpretation

Using February 2020 changes the below-baseline state list but does not increase the count relative to January 2019 in this extract. The January 2019 baseline is useful because it matches the full dashboard series, while February 2020 is a more direct pre-pandemic comparison point. The February 2020 framing appears useful for identifying states that moved below their immediate pre-pandemic enrollment level, but it should be described as a sensitivity check rather than a replacement unless the brief explicitly reframes the baseline.
"""


def main() -> None:
    rows = read_monthly_rows()
    grouped = rows_by_state(rows)
    state_rows = state_sensitivity_rows(grouped)
    summary_rows = baseline_summary_rows(state_rows, rows)
    national_rows = national_measure_summary(rows)

    state_fields = [
        "state",
        "state_abbr",
        "january_2019_total_medicaid_chip_enrollment",
        "february_2020_total_medicaid_chip_enrollment",
        "february_2026_total_medicaid_chip_enrollment",
        "raw_change_jan_2019_to_feb_2026",
        "percent_change_jan_2019_to_feb_2026",
        "below_january_2019_baseline",
        "raw_change_feb_2020_to_feb_2026",
        "percent_change_feb_2020_to_feb_2026",
        "below_february_2020_baseline",
    ]
    summary_fields = [
        "baseline_month",
        "number_of_states_plus_dc_below_baseline_by_february_2026",
        "states_plus_dc_below_baseline",
        "lowest_percent_change_state",
        "lowest_percent_change",
        "highest_percent_change_state",
        "highest_percent_change",
        "national_total_enrollment_at_baseline",
        "national_total_enrollment_february_2026",
        "national_raw_change",
        "national_percent_change",
    ]
    national_fields = [
        "measure",
        "baseline_month",
        "baseline_enrollment",
        "peak_month",
        "peak_enrollment",
        "february_2026_enrollment",
        "raw_change_baseline_to_feb_2026",
        "percent_change_baseline_to_feb_2026",
        "raw_decline_peak_to_feb_2026",
        "percent_decline_peak_to_feb_2026",
    ]

    write_csv(
        OUTPUT_DIR / "state_baseline_sensitivity_check.csv",
        state_rows,
        state_fields,
    )
    write_csv(
        OUTPUT_DIR / "baseline_sensitivity_summary.csv",
        summary_rows,
        summary_fields,
    )
    write_csv(
        OUTPUT_DIR / "national_raw_count_summary.csv",
        national_rows,
        national_fields,
    )
    (OUTPUT_DIR / "baseline_sensitivity_review.md").write_text(
        review_note(state_rows, summary_rows, national_rows), encoding="utf-8"
    )
    print(
        f"Wrote {len(state_rows)} state rows, {len(summary_rows)} summary rows, "
        f"{len(national_rows)} national rows."
    )


if __name__ == "__main__":
    main()
