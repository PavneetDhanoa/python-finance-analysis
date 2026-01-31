from __future__ import annotations

import argparse
from pathlib import Path

from src.ingest import read_transactions
from src.clean import clean_transactions
from src.analyze import build_summary_tables, build_console_summary
from src.viz import save_all_charts
from src.report import print_console_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Python Financial Analytics Tool (v1)")
    parser.add_argument("--input", required=True, help="Path to input transactions CSV")
    parser.add_argument("--out", required=True, help="Output directory (e.g., outputs/)")
    parser.add_argument(
        "--category-map",
        default=None,
        help="Optional category mapping CSV path (columns: raw, normalized)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    out_dir = Path(args.out)
    figures_dir = out_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Ensure a consistent 'data/' folder exists for rejected rows log
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    rejected_path = data_dir / "rejected_rows.csv"

    df_raw = read_transactions(input_path)

    cleaned_df, rejected_df = clean_transactions(
        df_raw,
        rejected_out_path=rejected_path,
        category_map_path=Path(args.category_map) if args.category_map else None,
    )

    # Save cleaned data
    cleaned_out_path = out_dir / "cleaned_transactions.csv"
    cleaned_df.to_csv(cleaned_out_path, index=False)

    # Build and save summary tables
    tables = build_summary_tables(cleaned_df)
    (out_dir / "monthly_spending_totals.csv").write_text(tables["monthly_spending"].to_csv(index=False))
    (out_dir / "category_expense_totals.csv").write_text(tables["category_expenses"].to_csv(index=False))

    # Charts
    save_all_charts(
        cleaned_df,
        out_figures_dir=figures_dir,
    )

    # Console summary
    console_summary = build_console_summary(cleaned_df, top_n=5)
    print_console_summary(console_summary)

    # Small note about rejected rows
    if not rejected_df.empty:
        print(f"\nRejected rows logged to: {rejected_path}")
    else:
        print("\nNo rejected rows.")

    print(f"\nSaved cleaned data to: {cleaned_out_path}")
    print(f"Saved figures to: {figures_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
