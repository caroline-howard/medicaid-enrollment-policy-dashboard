"""Load official Census state population denominators for dashboard context."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

SOURCE_NAME = (
    "U.S. Census Bureau Annual Estimates of the Resident Population for the "
    "United States, Regions, States, District of Columbia, and Puerto Rico: "
    "April 1, 2020 to July 1, 2024 (NST-EST2024-POP)"
)
SOURCE_URL = (
    "https://www2.census.gov/programs-surveys/popest/tables/2020-2024/"
    "state/totals/NST-EST2024-POP.xlsx"
)
RAW_FILE = RAW_DIR / "NST-EST2024-POP.xlsx"
OUTPUT_FILE = PROCESSED_DIR / "state_population_denominators.csv"

STATE_ABBREVIATIONS = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


def download_population_workbook() -> Path:
    """Download the official Census workbook to the ignored raw data folder."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not RAW_FILE.exists():
        import requests

        response = requests.get(SOURCE_URL, timeout=60)
        response.raise_for_status()
        RAW_FILE.write_bytes(response.content)
    return RAW_FILE


def _cell_text(cell: ET.Element, shared_strings: list[str], namespace: dict[str, str]) -> str:
    value_node = cell.find("x:v", namespace)
    if value_node is None or value_node.text is None:
        return ""
    value = value_node.text
    if cell.attrib.get("t") == "s":
        return shared_strings[int(value)]
    return value


def _read_xlsx_rows(path: Path) -> list[list[str]]:
    namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(path) as workbook:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
            for item in root.findall("x:si", namespace):
                shared_strings.append(
                    "".join(node.text or "" for node in item.findall(".//x:t", namespace))
                )

        sheet = ET.fromstring(workbook.read("xl/worksheets/sheet1.xml"))
        rows: list[list[str]] = []
        for row in sheet.findall(".//x:row", namespace):
            values: list[str] = []
            for cell in row.findall("x:c", namespace):
                values.append(_cell_text(cell, shared_strings, namespace))
            rows.append(values)
    return rows


def parse_population_workbook(path: Path) -> list[dict[str, object]]:
    """Parse Census state rows and return one row per state/DC population year."""
    rows = _read_xlsx_rows(path)
    records: list[dict[str, object]] = []
    access_date = date.today().isoformat()

    for row in rows:
        if not row:
            continue
        geography = row[0].strip()
        if not geography.startswith("."):
            continue

        state_name = geography.lstrip(".").strip()
        state_abbreviation = STATE_ABBREVIATIONS.get(state_name)
        if not state_abbreviation:
            continue

        for offset, population_year in enumerate(range(2020, 2025), start=2):
            if offset >= len(row) or not row[offset]:
                continue
            records.append(
                {
                    "state_abbreviation": state_abbreviation,
                    "state_name": state_name,
                    "population_year": population_year,
                    "state_population": int(float(row[offset])),
                    "source_name": SOURCE_NAME,
                    "source_url": SOURCE_URL,
                    "date_accessed": access_date,
                    "population_notes": (
                        "Annual resident population estimate as of July 1. "
                        "Used as descriptive state population context, not a utilization denominator."
                    ),
                }
            )

    if len(records) != 51 * 5:
        raise ValueError(f"Expected 255 state/year rows, found {len(records)}")
    if len({record["state_abbreviation"] for record in records}) != 51:
        raise ValueError("Expected all 50 states plus DC")
    return sorted(records, key=lambda record: (record["state_abbreviation"], record["population_year"]))


def main() -> None:
    workbook = download_population_workbook()
    population = parse_population_workbook(workbook)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(population[0].keys()))
        writer.writeheader()
        writer.writerows(population)
    print(f"Saved {len(population):,} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
