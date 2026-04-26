import json
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import requests

from .config import (
    DATASET_DIRECT_URL,
    RAW_DATA_FILE,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    OUTPUTS_DIR,
    FIGURES_DIR,
    TABLES_DIR,
    REPORT_DIR,
    EXPECTED_COLUMNS,
)


def make_directories() -> None:
    """Create all project output folders if they do not already exist."""
    for folder in [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        OUTPUTS_DIR,
        FIGURES_DIR,
        TABLES_DIR,
        REPORT_DIR,
    ]:
        folder.mkdir(parents=True, exist_ok=True)


def download_dataset(force: bool = False) -> Path:
    """
    Download the UCI Online Retail Excel file.

    The file is not stored in this repository by default because it is large.
    This function downloads it into data/raw/Online_Retail.xlsx.
    """
    make_directories()

    if RAW_DATA_FILE.exists() and RAW_DATA_FILE.stat().st_size > 1_000_000 and not force:
        print(f"Dataset already exists: {RAW_DATA_FILE}")
        return RAW_DATA_FILE

    print("Downloading dataset from UCI Machine Learning Repository...")
    print(f"URL: {DATASET_DIRECT_URL}")

    try:
        with requests.get(DATASET_DIRECT_URL, stream=True, timeout=120) as response:
            response.raise_for_status()
            with open(RAW_DATA_FILE, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file.write(chunk)
    except Exception as exc:
        raise RuntimeError(
            "Could not download the dataset automatically. "
            "Please download Online Retail.xlsx manually from "
            "https://archive.ics.uci.edu/dataset/352/online+retail "
            f"and place it at {RAW_DATA_FILE}."
        ) from exc

    print(f"Downloaded dataset to: {RAW_DATA_FILE}")
    return RAW_DATA_FILE


def load_raw_data(path: Path = RAW_DATA_FILE) -> pd.DataFrame:
    """Load the raw Excel dataset into a Pandas DataFrame."""
    return pd.read_excel(path, engine="openpyxl")


def validate_dataset(df: pd.DataFrame) -> None:
    """Validate the dataset against the project brief requirements."""
    missing_columns = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"The dataset is missing expected columns: {missing_columns}")

    if df.shape[0] < 1000:
        raise ValueError("Dataset does not meet the minimum 1000-row requirement.")

    if df.shape[1] < 6:
        raise ValueError("Dataset does not meet the minimum 6-column requirement.")


def create_data_understanding_outputs(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Save initial data-understanding outputs:
    - shape
    - columns
    - data types
    - missing values
    - duplicate count
    - numeric summary statistics
    - sample rows
    """
    make_directories()

    profile: Dict[str, Any] = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
    }

    data_types = pd.DataFrame(
        {
            "column": df.columns,
            "data_type": [str(dtype) for dtype in df.dtypes],
            "missing_values": df.isna().sum().values,
            "missing_percent": (df.isna().mean().values * 100).round(2),
            "unique_values": df.nunique(dropna=True).values,
        }
    )
    data_types.to_csv(TABLES_DIR / "data_types_and_missing_values.csv", index=False)

    df.head(10).to_csv(TABLES_DIR / "sample_rows.csv", index=False)

    numeric_summary = df.describe(include="number").T
    numeric_summary.to_csv(TABLES_DIR / "numeric_summary_statistics.csv")

    with open(OUTPUTS_DIR / "data_profile.json", "w", encoding="utf-8") as file:
        json.dump(profile, file, indent=4)

    return profile