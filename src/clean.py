from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class CleanResult:
    cleaned: pd.DataFrame
    rejected: pd.DataFrame


def _load_category_map(category_map_path: Optional[Path]) -> dict[str, str]:
    """
    Load category mapping from CSV with columns: raw, normalized
    Returns dict: raw -> normalized
    """
    if not category_map_path:
        return {}

    if not category_map_path.exists():
        raise FileNotFoundError(f"Category map not found: {category_map_path}")

    m = pd.read_csv(category_map_path)
    expected = {"raw", "normalized"}
    if not expected.issubset(set(m.columns)):
        raise ValueError(f"Category map must have columns {expected}. Found: {set(m.columns)}")

    # Strip whitespace in mapping as well
    m["raw"] = m["raw"].astype(str).str.strip()
    m["normalized"] = m["normalized"].astype(str).str.strip()
    return dict(zip(m["raw"], m["normalized"]))


def clean_transactions(
    df: pd.DataFrame,
    rejected_out_path: Path,
    category_map_path: Optional[Path] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Cleaning rules:
    - drop rows with invalid dates or invalid amounts
    - log rejected rows to rejected_out_path (CSV)
    - trim whitespace in category/description
    - normalize categories using mapping dict (optional)
    """
    df = df.copy()

    # Trim whitespace
    df["description"] = df["description"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()

    # Parse date & amount (mark invalid)
    parsed_date = pd.to_datetime(df["date"], errors="coerce", format="%Y-%m-%d")
    parsed_amount = pd.to_numeric(df["amount"], errors="coerce")

    invalid_mask = parsed_date.isna() | parsed_amount.isna()

    rejected = df.loc[invalid_mask].copy()
    cleaned = df.loc[~invalid_mask].copy()

    # Apply parsed types
    cleaned["date"] = parsed_date.loc[~invalid_mask].dt.date.astype(str)  # keep YYYY-MM-DD as string
    cleaned["amount"] = parsed_amount.loc[~invalid_mask].astype(float)

    # Normalize categories (optional)
    cat_map = _load_category_map(category_map_path)
    if cat_map:
        cleaned["category"] = cleaned["category"].map(lambda c: cat_map.get(c, c))

    # Write rejected rows log (append-friendly but simple overwrite for v1)
    rejected_out_path.parent.mkdir(parents=True, exist_ok=True)
    rejected.to_csv(rejected_out_path, index=False)

    return cleaned, rejected
