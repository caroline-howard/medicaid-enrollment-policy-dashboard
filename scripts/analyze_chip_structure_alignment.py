#!/usr/bin/env python3
"""Analyze whether CHIP program structure aligns with enrollment patterns.

This script uses project-local CMS/Medicaid.gov-derived data only:
- monthly state Medicaid/CHIP enrollment from the processed dashboard data
- Medicaid.gov CHIP program structure categories from data/context

The outputs are descriptive review artifacts. They do not change dashboard
logic or the writing-sample brief.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[1]
STATE_MONTH_CSV = ROOT / "data/processed/medicaid_state_month_summary.csv"
CHIP_STRUCTURE_CSV = ROOT / "data/context/chip_program_structure.csv"
OUTPUT_DIR = ROOT / "data/outputs"

BASELINE_MONTH = "2019-01-01"
LATEST_MONTH = "2026-02-01"
FLAGGED_STATES = ["TX", "LA", "NC", "OK", "OR", "ME", "MT", "FL", "MI", "VA", "MO"]

STRUCTURE_LABELS = {
    "Separate CHIP only": "Separate CHIP only",
    "Medicaid expansion CHIP only": "CHIP Medicaid expansion only",
    "CHIP Medicaid expansion only": "CHIP Medicaid expansion only",
    "Both separate CHIP and Medicaid expansion CHIP": (
        "CHIP Medicaid expansion and separate CHIP"
    ),
    "CHIP Medicaid expansion and separate CHIP": (
        "CHIP Medicaid expansion and separate CHIP"
    ),
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


def fmt_pct(value: float | None) -> str:
    return "" if value is None else f"{value:.1f}%"


def fmt_count(value: float | None) -> str:
    return "" if value is None else f"{int(round(value)):,}"


def read_chip_structure() -> dict[str, dict[str, str]]:
    structures: dict[str, dict[str, str]] = {}
    with CHIP_STRUCTURE_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            raw = row["chip_program_structure"]
            normalized = STRUCTURE_LABELS.get(raw, raw)
            structures[row["state_abbr"]] = {
                "state": row["state"],
                "state_abbr": row["state_abbr"],
                "chip_structure_category": normalized,
                "source_name": row.get("source_name", ""),
                "source_url": row.get("source_url", ""),
            }
    return structures


def read_monthly_enrollment() -> dict[str, list[dict]]:
    by_state: dict[str, list[dict]] = defaultdict(list)
    with STATE_MONTH_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            by_state[row["state_abbreviation"]].append(
                {
                    "state": row["state_name"],
                    "state_abbr": row["state_abbreviation"],
                    "month": row["reporting_month"],
                    "total": parse_float(row["total_medicaid_and_chip_enrollment"]),
                    "medicaid": parse_float(row["total_medicaid_enrollment"]),
                    "chip": parse_float(row["total_chip_enrollment"]),
                }
            )
    for rows in by_state.values():
        rows.sort(key=lambda item: item["month"])
    return by_state


def find_month(rows: list[dict], month: str) -> dict | None:
    return next((row for row in rows if row["month"] == month), None)


def state_metrics(structures: dict[str, dict[str, str]], monthly: dict[str, list[dict]]):
    output = []
    for abbr, structure in sorted(structures.items(), key=lambda item: item[1]["state"]):
        rows = monthly.get(abbr, [])
        baseline = find_month(rows, BASELINE_MONTH)
        latest = find_month(rows, LATEST_MONTH)
        if not rows or baseline is None or latest is None:
            raise ValueError(f"Missing baseline/latest enrollment data for {abbr}")
        peak = max(rows, key=lambda row: row["total"] or 0)
        total_pct = pct_change(baseline["total"], latest["total"])
        medicaid_pct = pct_change(baseline["medicaid"], latest["medicaid"])
        chip_pct = pct_change(baseline["chip"], latest["chip"])
        peak_decline = pct_decline(peak["total"], latest["total"])
        output.append(
            {
                "state": structure["state"],
                "state_abbr": abbr,
                "chip_structure_category": structure["chip_structure_category"],
                "january_2019_total_medicaid_chip_enrollment": baseline["total"],
                "february_2026_total_medicaid_chip_enrollment": latest["total"],
                "percent_change_jan_2019_to_feb_2026_total": total_pct,
                "observed_peak_month": peak["month"],
                "observed_peak_enrollment": peak["total"],
                "percent_decline_peak_to_feb_2026_total": peak_decline,
                "february_2026_below_january_2019_baseline": (
                    latest["total"] < baseline["total"]
                ),
                "medicaid_january_2019_enrollment": baseline["medicaid"],
                "medicaid_february_2026_enrollment": latest["medicaid"],
                "medicaid_percent_change_jan_2019_to_feb_2026": medicaid_pct,
                "chip_january_2019_enrollment": baseline["chip"],
                "chip_february_2026_enrollment": latest["chip"],
                "chip_percent_change_jan_2019_to_feb_2026": chip_pct,
            }
        )
    return output


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize_by_structure(rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["chip_structure_category"]].append(row)

    summaries = []
    for category, items in sorted(grouped.items()):
        below_count = sum(
            1 for row in items if row["february_2026_below_january_2019_baseline"]
        )
        flagged = [row["state_abbr"] for row in items if row["state_abbr"] in FLAGGED_STATES]
        summaries.append(
            {
                "chip_structure_category": category,
                "number_of_states": len(items),
                "median_percent_change_total_jan_2019_to_feb_2026": median(
                    row["percent_change_jan_2019_to_feb_2026_total"] for row in items
                ),
                "median_percent_change_medicaid_jan_2019_to_feb_2026": median(
                    row["medicaid_percent_change_jan_2019_to_feb_2026"] for row in items
                ),
                "median_percent_change_chip_jan_2019_to_feb_2026": median(
                    row["chip_percent_change_jan_2019_to_feb_2026"] for row in items
                ),
                "median_peak_to_current_percent_decline_total": median(
                    row["percent_decline_peak_to_feb_2026_total"] for row in items
                ),
                "number_of_states_below_january_2019_baseline_by_february_2026": below_count,
                "percent_of_states_below_january_2019_baseline_by_february_2026": (
                    below_count / len(items) * 100
                ),
                "flagged_outlier_states_in_group": "; ".join(flagged),
            }
        )
    return summaries


def interpretation_note(row: dict, group_rows: list[dict]) -> str:
    category = row["chip_structure_category"]
    peer_signs = {
        "below": sum(
            1 for item in group_rows if item["february_2026_below_january_2019_baseline"]
        ),
        "above": sum(
            1
            for item in group_rows
            if not item["february_2026_below_january_2019_baseline"]
        ),
    }
    if peer_signs["below"] and peer_signs["above"]:
        return (
            f"Unclear: {row['state_abbr']} uses {category}, but this category includes "
            "states both above and below baseline, so structure does not fully explain the pattern."
        )
    return (
        f"May provide context: {row['state_abbr']} uses {category}, but this is a "
        "descriptive association only and should be reviewed alongside renewal and reporting context."
    )


def flagged_rows(rows: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_group[row["chip_structure_category"]].append(row)
    selected = [row for row in rows if row["state_abbr"] in FLAGGED_STATES]
    selected.sort(key=lambda row: FLAGGED_STATES.index(row["state_abbr"]))
    out = []
    for row in selected:
        clipped = {
            key: row[key]
            for key in [
                "state",
                "state_abbr",
                "chip_structure_category",
                "january_2019_total_medicaid_chip_enrollment",
                "february_2026_total_medicaid_chip_enrollment",
                "percent_change_jan_2019_to_feb_2026_total",
                "observed_peak_month",
                "observed_peak_enrollment",
                "percent_decline_peak_to_feb_2026_total",
                "february_2026_below_january_2019_baseline",
            ]
        }
        clipped["short_interpretation_note"] = interpretation_note(
            row, by_group[row["chip_structure_category"]]
        )
        out.append(clipped)
    return out


def markdown_review(rows: list[dict], summaries: list[dict], flagged: list[dict]) -> str:
    flagged_by_category: dict[str, list[str]] = defaultdict(list)
    for row in flagged:
        flagged_by_category[row["chip_structure_category"]].append(row["state_abbr"])

    summary_lines = []
    for row in summaries:
        summary_lines.append(
            f"- {row['chip_structure_category']}: {row['number_of_states']} states/DC; "
            f"median total change {fmt_pct(row['median_percent_change_total_jan_2019_to_feb_2026'])}; "
            f"median peak-to-current decline {fmt_pct(row['median_peak_to_current_percent_decline_total'])}; "
            f"{row['number_of_states_below_january_2019_baseline_by_february_2026']} below baseline."
        )

    flagged_lines = []
    for category, states in sorted(flagged_by_category.items()):
        flagged_lines.append(f"- {category}: {', '.join(states)}")

    flagged_notes = []
    for row in flagged:
        flagged_notes.append(
            f"- {row['state_abbr']} ({row['chip_structure_category']}): "
            f"{fmt_pct(row['percent_change_jan_2019_to_feb_2026_total'])} since baseline; "
            f"{fmt_pct(row['percent_decline_peak_to_feb_2026_total'])} below peak; "
            f"below baseline = {row['february_2026_below_january_2019_baseline']}."
        )

    return f"""# CHIP Structure Alignment Review

Generated by `scripts/analyze_chip_structure_alignment.py` on {datetime.now().date().isoformat()}.

## Source and scope

This review uses the project CMS monthly enrollment data and the official Medicaid.gov CHIP program structure categories from `data/context/chip_program_structure.csv`. Categories were normalized to:

- Separate CHIP only
- CHIP Medicaid expansion only
- CHIP Medicaid expansion and separate CHIP

This is a descriptive association check only. It does not test causality and does not modify the dashboard or writing-sample brief.

## Do flagged states cluster in one CHIP structure category?

Most flagged states fall into the combined CHIP Medicaid expansion and separate CHIP category:

{chr(10).join(flagged_lines)}

The clustering is partly a function of the national distribution of CHIP structures: most states/DC in the source file are in the combined category. Because both above-baseline and below-baseline flagged states appear in that same category, structure alone does not fully explain the divergence pattern.

## Do categories show meaningfully different median enrollment changes?

{chr(10).join(summary_lines)}

The median differences provide context, but the category groups are uneven in size. The combined category contains many more states than the separate-only and Medicaid-expansion-only categories, so medians should be interpreted cautiously.

## Does CHIP structure explain the state divergence pattern?

CHIP program structure may help interpret the program-design context for specific states, but it does not fully explain the state divergence pattern. The same CHIP structure category includes states that remained materially above baseline and states that fell below baseline by February 2026. This weakens the case for adding CHIP structure as a central explanation in the brief without additional state-specific policy, renewal, or reporting review.

## Flagged state review notes

{chr(10).join(flagged_notes)}

## What should be reviewed before adding this to the brief?

- Review whether each state's CHIP structure changed during the analysis window or was stable throughout 2019-2026.
- Compare CHIP structure with state-specific renewal timing, ex parte renewal performance, procedural disenrollment context, and reporting notes.
- Review whether state divergence is more closely aligned with Medicaid changes than CHIP changes in the flagged states.
- Treat this as context only unless a stronger mechanism is supported by official state or CMS documentation.
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    structures = read_chip_structure()
    monthly = read_monthly_enrollment()
    rows = state_metrics(structures, monthly)
    summaries = summarize_by_structure(rows)
    flagged = flagged_rows(rows)

    state_fields = [
        "state",
        "state_abbr",
        "chip_structure_category",
        "january_2019_total_medicaid_chip_enrollment",
        "february_2026_total_medicaid_chip_enrollment",
        "percent_change_jan_2019_to_feb_2026_total",
        "observed_peak_month",
        "observed_peak_enrollment",
        "percent_decline_peak_to_feb_2026_total",
        "february_2026_below_january_2019_baseline",
        "medicaid_january_2019_enrollment",
        "medicaid_february_2026_enrollment",
        "medicaid_percent_change_jan_2019_to_feb_2026",
        "chip_january_2019_enrollment",
        "chip_february_2026_enrollment",
        "chip_percent_change_jan_2019_to_feb_2026",
    ]
    summary_fields = [
        "chip_structure_category",
        "number_of_states",
        "median_percent_change_total_jan_2019_to_feb_2026",
        "median_percent_change_medicaid_jan_2019_to_feb_2026",
        "median_percent_change_chip_jan_2019_to_feb_2026",
        "median_peak_to_current_percent_decline_total",
        "number_of_states_below_january_2019_baseline_by_february_2026",
        "percent_of_states_below_january_2019_baseline_by_february_2026",
        "flagged_outlier_states_in_group",
    ]
    flagged_fields = [
        "state",
        "state_abbr",
        "chip_structure_category",
        "january_2019_total_medicaid_chip_enrollment",
        "february_2026_total_medicaid_chip_enrollment",
        "percent_change_jan_2019_to_feb_2026_total",
        "observed_peak_month",
        "observed_peak_enrollment",
        "percent_decline_peak_to_feb_2026_total",
        "february_2026_below_january_2019_baseline",
        "short_interpretation_note",
    ]

    write_csv(
        OUTPUT_DIR / "chip_structure_state_enrollment_patterns.csv",
        rows,
        state_fields,
    )
    write_csv(OUTPUT_DIR / "chip_structure_summary.csv", summaries, summary_fields)
    write_csv(
        OUTPUT_DIR / "chip_structure_flagged_states_review.csv",
        flagged,
        flagged_fields,
    )
    (OUTPUT_DIR / "chip_structure_alignment_review.md").write_text(
        markdown_review(rows, summaries, flagged), encoding="utf-8"
    )
    print(f"Wrote {len(rows)} state rows, {len(summaries)} summary rows, {len(flagged)} flagged rows.")


if __name__ == "__main__":
    main()
