from __future__ import annotations


def print_console_summary(summary: dict) -> None:
    print("\n=== Console Summary ===")
    print(f"Total Income:   ${summary['total_income']:.2f}")
    print(f"Total Expenses: ${summary['total_expenses']:.2f}")
    print(f"Net:            ${summary['net']:.2f}")

    print("\nTop 5 Expense Categories:")
    top = summary.get("top_categories", [])
    if not top:
        print("  (no expense data)")
        return

    for i, row in enumerate(top, start=1):
        print(f"  {i}. {row['category']}: ${row['total_expenses']:.2f}")
