from __future__ import annotations

from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = ["date", "description", "amount", "category"]


def read_transactions(csv_path: Path) -> pd.DataFrame:
    """
    Read transactions CSV and enforce required columns.
    Expected columns: date, description, amount, category
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Input file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Found: {list(df.columns)}")

    # Keep only required columns (in order)
    return df[REQUIRED_COLUMNS].copy()
