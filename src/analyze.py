from __future__ import annotations

import pandas as pd


def _add_month_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a 'month' column formatted as YYYY-MM.
    Expects df['date'] in YYYY-MM-DD string format.
    """
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], format="%Y-%m-%d", errors="raise")
    out["month"] = out["date"].dt.to_period("M").astype(str)
    return out


def monthly_spending_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Monthly spending totals (expenses only): month, total_expenses
    Expenses are amount < 0 (stored as negative).
    Output total_expenses as positive number for readability.
    """
    d = _add_month_column(df)
    expenses = d[d["amount"] < 0].copy()
    if expenses.empty:
        return pd.DataFrame({"month": [], "total_expenses": []})

    grouped = (
        expenses.groupby("month", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "total_expenses"})
    )
    grouped["total_expenses"] = grouped["total_expenses"].abs()
    return grouped.sort_values("month").reset_index(drop=True)


def category_expense_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Category totals (expenses only): category, total_expenses
    Output total_expenses as positive number.
    """
    expenses = df[df["amount"] < 0].copy()
    if expenses.empty:
        return pd.DataFrame({"category": [], "total_expenses": []})

    grouped = (
        expenses.groupby("category", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "total_expenses"})
    )
    grouped["total_expenses"] = grouped["total_expenses"].abs()
    return grouped.sort_values("total_expenses", ascending=False).reset_index(drop=True)


def income_vs_expense_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns: month, income, expenses
    income is positive sum of amount>0
    expenses is positive sum of abs(amount<0)
    """
    d = _add_month_column(df)

    income = d[d["amount"] > 0].groupby("month")["amount"].sum()
    expenses = d[d["amount"] < 0].groupby("month")["amount"].sum().abs()

    months = sorted(set(d["month"].unique()))
    rows = []
    for m in months:
        rows.append(
            {
                "month": m,
                "income": float(income.get(m, 0.0)),
                "expenses": float(expenses.get(m, 0.0)),
            }
        )
    return pd.DataFrame(rows)


def build_summary_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "monthly_spending": monthly_spending_totals(df),
        "category_expenses": category_expense_totals(df),
        "income_vs_expense": income_vs_expense_by_month(df),
    }


def build_console_summary(df: pd.DataFrame, top_n: int = 5) -> dict:
    total_income = float(df.loc[df["amount"] > 0, "amount"].sum())
    total_expenses = float(df.loc[df["amount"] < 0, "amount"].sum())  # negative
    net = total_income + total_expenses

    cat = category_expense_totals(df)
    top = cat.head(top_n).to_dict(orient="records")

    return {
        "total_income": total_income,
        "total_expenses": abs(total_expenses),
        "net": net,
        "top_categories": top,
    }
