# Analysis functions (timeseries, categories)

import pandas as pd


def daily_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate total spending and income per day.

    Args:
        df: DataFrame with 'date' and 'amount' columns

    Returns:
        DataFrame with columns: date, expenses (positive), income, net
    """
    df_daily = df.groupby("date").apply(
        lambda x: pd.Series({
            "expenses": abs(x[x["amount"] < 0]["amount"].sum()),
            "income": x[x["amount"] > 0]["amount"].sum(),
        })
    ).reset_index()

    df_daily["net"] = df_daily["income"] - df_daily["expenses"]

    return df_daily


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate income vs expenses per month.

    Args:
        df: DataFrame with 'date' and 'amount' columns

    Returns:
        DataFrame with columns: year_month, expenses (positive), income, net
    """
    df_copy = df.copy()
    df_copy["year_month"] = df_copy["date"].dt.to_period("M")

    df_monthly = df_copy.groupby("year_month").apply(
        lambda x: pd.Series({
            "expenses": abs(x[x["amount"] < 0]["amount"].sum()),
            "income": x[x["amount"] > 0]["amount"].sum(),
        })
    ).reset_index()

    df_monthly["net"] = df_monthly["income"] - df_monthly["expenses"]
    df_monthly["year_month"] = df_monthly["year_month"].astype(str)

    return df_monthly


def yearly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate income vs expenses per year.

    Args:
        df: DataFrame with 'date' and 'amount' columns

    Returns:
        DataFrame with columns: year, expenses (positive), income, net
    """
    df_copy = df.copy()
    df_copy["year"] = df_copy["date"].dt.year

    df_yearly = df_copy.groupby("year").apply(
        lambda x: pd.Series({
            "expenses": abs(x[x["amount"] < 0]["amount"].sum()),
            "income": x[x["amount"] > 0]["amount"].sum(),
        })
    ).reset_index()

    df_yearly["net"] = df_yearly["income"] - df_yearly["expenses"]

    return df_yearly


def category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate total expenses by category (expenses as positive values).

    Args:
        df: DataFrame with 'category' and 'amount' columns

    Returns:
        DataFrame with columns: category, total (positive), count, average (positive)
    """
    # Only include expenses (negative amounts)
    df_expenses = df[df["amount"] < 0].copy()

    df_cat = df_expenses.groupby("category").apply(
        lambda x: pd.Series({
            "total": abs(x["amount"].sum()),
            "count": len(x),
            "average": abs(x["amount"].mean()),
        })
    ).reset_index()

    df_cat = df_cat.sort_values("total", ascending=False).reset_index(drop=True)

    return df_cat


def top_merchants(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Get top merchants by total spending.

    Args:
        df: DataFrame with 'description' and 'amount' columns
        n: Number of top merchants to return

    Returns:
        DataFrame with columns: description, total, count
    """
    df_merchants = df.groupby("description").apply(
        lambda x: pd.Series({
            "total": x["amount"].sum(),
            "count": len(x),
        })
    ).reset_index()

    df_merchants = df_merchants.sort_values("total").head(n)

    return df_merchants


def get_uncategorized(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get all uncategorized transactions.

    Args:
        df: DataFrame with 'category' column

    Returns:
        DataFrame of uncategorized transactions sorted by date (newest first)
    """
    df_uncategorized = df[df["category"] == "Uncategorized"].copy()
    df_uncategorized = df_uncategorized.sort_values("date", ascending=False)

    return df_uncategorized


def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Calculate summary statistics for the entire dataset.

    Args:
        df: DataFrame with 'amount' and 'date' columns

    Returns:
        Dictionary with total income, total expenses, net, date range, transaction count
    """
    total_income = df[df["amount"] > 0]["amount"].sum()
    total_expenses = df[df["amount"] < 0]["amount"].sum()
    net = total_income + total_expenses

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net": net,
        "date_from": df["date"].min(),
        "date_to": df["date"].max(),
        "transaction_count": len(df),
    }
