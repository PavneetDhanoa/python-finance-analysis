from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from src.analyze import monthly_spending_totals, category_expense_totals, income_vs_expense_by_month


def save_monthly_expenses_bar(df: pd.DataFrame, out_path: Path) -> None:
    data = monthly_spending_totals(df)
    plt.figure()
    plt.bar(data["month"], data["total_expenses"])
    plt.title("Monthly Total Expenses")
    plt.xlabel("Month")
    plt.ylabel("Total Expenses")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def save_category_expenses_pie(df: pd.DataFrame, out_path: Path) -> None:
    data = category_expense_totals(df)
    # Avoid unreadable pie charts by limiting slices
    top = data.head(8).copy()
    if len(data) > 8:
        other_sum = data.iloc[8:]["total_expenses"].sum()
        top = pd.concat([top, pd.DataFrame([{"category": "Other", "total_expenses": other_sum}])], ignore_index=True)

    plt.figure()
    plt.pie(top["total_expenses"], labels=top["category"], autopct="%1.1f%%", startangle=140)
    plt.title("Expense Share by Category")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def save_income_vs_expense_line(df: pd.DataFrame, out_path: Path) -> None:
    data = income_vs_expense_by_month(df)

    plt.figure()
    plt.plot(data["month"], data["income"], marker="o", label="Income")
    plt.plot(data["month"], data["expenses"], marker="o", label="Expenses")
    plt.title("Income vs Expenses by Month")
    plt.xlabel("Month")
    plt.ylabel("Amount")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def save_all_charts(df: pd.DataFrame, out_figures_dir: Path) -> None:
    save_monthly_expenses_bar(df, out_figures_dir / "monthly_expenses_bar.png")
    save_category_expenses_pie(df, out_figures_dir / "category_expenses_pie.png")
    save_income_vs_expense_line(df, out_figures_dir / "income_vs_expense_line.png")
