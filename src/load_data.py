"""Load official public Medicaid/CHIP enrollment source data.

This module downloads the CMS/Data.Medicaid.gov Performance Indicator dataset
used for enrollment and eligibility operations reporting. Raw data are saved
under data/raw, which is intentionally ignored by Git.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
METADATA_PATH = RAW_DIR / "source_metadata.json"
RAW_CSV_PATH = RAW_DIR / "pi-dataset-may-2026-release.csv"

DATASET_ID = "6165f45b-ca93-5bb5-9d06-db29c692a360"
METADATA_URL = (
    "https://data.medicaid.gov/api/1/metastore/schemas/dataset/items/"
    f"{DATASET_ID}"
)
DATA_DICTIONARY_URL = (
    "https://data.medicaid.gov/api/1/metastore/schemas/data-dictionary/items/"
    "7d80cfd8-3266-4c55-8436-948b7c55b9dd"
)
SOURCE_CSV_URL = "https://download.medicaid.gov/data/pi-dataset-may-2026-release.csv"


def fetch_json(url: str) -> dict[str, Any]:
    """Fetch JSON metadata from an official CMS endpoint."""
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()


def download_source_csv(destination: Path = RAW_CSV_PATH) -> Path:
    """Download the official source CSV if it is not already present."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        return destination

    with requests.get(SOURCE_CSV_URL, stream=True, timeout=120) as response:
        response.raise_for_status()
        with destination.open("wb") as output_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    output_file.write(chunk)
    return destination


def save_source_metadata(destination: Path = METADATA_PATH, force: bool = False) -> Path:
    """Save source and data dictionary metadata for reproducibility."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0 and not force:
        return destination

    metadata = {
        "dataset_metadata_url": METADATA_URL,
        "data_dictionary_url": DATA_DICTIONARY_URL,
        "source_csv_url": SOURCE_CSV_URL,
        "dataset_metadata": fetch_json(METADATA_URL),
        "data_dictionary": fetch_json(DATA_DICTIONARY_URL),
    }
    destination.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return destination


def load_raw_data(csv_path: Path = RAW_CSV_PATH) -> pd.DataFrame:
    """Load the downloaded CMS source CSV into a DataFrame."""
    return pd.read_csv(csv_path, low_memory=False)


def main() -> None:
    """Download source data and metadata."""
    metadata_path = save_source_metadata()
    csv_path = download_source_csv()
    df = load_raw_data(csv_path)
    print(f"Metadata saved to {metadata_path}")
    print(f"Raw source CSV saved to {csv_path}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")


if __name__ == "__main__":
    main()
