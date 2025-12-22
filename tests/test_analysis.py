import pandas as pd

from src.analyze import monthly_spending_totals, category_expense_totals, income_vs_expense_by_month


def test_monthly_spending_totals_expenses_only():
    df = pd.DataFrame(
        {
            "date": ["2025-10-01", "2025-10-02", "2025-10-03"],
            "description": ["A", "B", "C"],
            "amount": [-10.0, 100.0, -5.0],
            "category": ["Food", "Income", "Food"],
        }
    )
    out = monthly_spending_totals(df)
    assert out.loc[0, "month"] == "2025-10"
    assert abs(out.loc[0, "total_expenses"] - 15.0) < 1e-9


def test_category_expense_totals_sums_by_category():
    df = pd.DataFrame(
        {
            "date": ["2025-10-01", "2025-10-02", "2025-10-03"],
            "description": ["A", "B", "C"],
            "amount": [-10.0, -20.0, -5.0],
            "category": ["Food", "Gas", "Food"],
        }
    )
    out = category_expense_totals(df)
    # Food total = 15, Gas total = 20 -> Gas should be first
    assert out.loc[0, "category"] == "Gas"
    assert abs(out.loc[out["category"] == "Food", "total_expenses"].iloc[0] - 15.0) < 1e-9


def test_income_vs_expense_by_month_handles_missing_side():
    df = pd.DataFrame(
        {
            "date": ["2025-10-01", "2025-11-01"],
            "description": ["Rent", "Salary"],
            "amount": [-100.0, 200.0],
            "category": ["Housing", "Income"],
        }
    )
    out = income_vs_expense_by_month(df)
    oct_row = out[out["month"] == "2025-10"].iloc[0]
    nov_row = out[out["month"] == "2025-11"].iloc[0]
    assert oct_row["income"] == 0.0 and oct_row["expenses"] == 100.0
    assert nov_row["income"] == 200.0 and nov_row["expenses"] == 0.0
