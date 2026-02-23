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


def category_breakdown_with_averages(df: pd.DataFrame, months: int = 6) -> pd.DataFrame:
    """
    Calculate current month category breakdown with N-month average.

    Args:
        df: DataFrame with 'date', 'category', and 'amount' columns
        months: Number of months to average (default 6)

    Returns:
        DataFrame with columns: category, current, avg, difference
    """
    df_copy = df.copy()
    df_copy["year_month"] = df_copy["date"].dt.to_period("M")

    # Get current month (most recent)
    current_month = df_copy["year_month"].max()
    df_current = df_copy[df_copy["year_month"] == current_month]

    # Get current month breakdown
    current_breakdown = category_breakdown(df_current)

    # Get N most recent months for averaging
    all_months = sorted(df_copy["year_month"].unique())
    months_for_avg = all_months[-months:] if len(all_months) >= months else all_months
    df_history = df_copy[df_copy["year_month"].isin(months_for_avg)]

    # Calculate average per category across all months
    df_history_expenses = df_history[df_history["amount"] < 0].copy()
    df_avg = df_history_expenses.groupby("category").apply(
        lambda x: pd.Series({
            "avg": abs(x["amount"].sum()) / len(months_for_avg),
        })
    ).reset_index()

    # Merge current and average
    result = current_breakdown[["category", "total"]].rename(columns={"total": "current"})
    result = result.merge(df_avg, on="category", how="left")
    result["avg"] = result["avg"].fillna(0)
    result["difference"] = result["current"] - result["avg"]

    # Sort by current spending descending
    result = result.sort_values("current", ascending=True)  # ascending for horizontal bar

    return result


def get_month_comparison_data(df: pd.DataFrame, target_month: str = None) -> dict:
    """
    Get current and previous month metrics with MoM % changes.

    Args:
        df: DataFrame with 'date' and 'amount' columns
        target_month: Target month as string (YYYY-MM). If None, uses most recent month.

    Returns:
        Dictionary with keys:
            - current_month: month label (YYYY-MM)
            - current_income: current month income
            - current_expenses: current month expenses
            - current_net: current month net
            - previous_income: previous month income
            - previous_expenses: previous month expenses
            - previous_net: previous month net
            - income_change_pct: % change (can be None)
            - expenses_change_pct: % change (can be None)
            - expenses_change_euros: € change (can be None)
            - net_change_pct: % change (can be None)
            - has_previous: boolean flag
    """
    df_copy = df.copy()
    df_copy["year_month"] = df_copy["date"].dt.to_period("M").astype(str)

    all_months = sorted(df_copy["year_month"].unique())

    if not all_months:
        return {}

    # Determine target month
    if target_month is None:
        current_month = all_months[-1]
    else:
        current_month = target_month

    # Get current month data
    df_current = df_copy[df_copy["year_month"] == current_month]
    current_income = df_current[df_current["amount"] > 0]["amount"].sum()
    current_expenses = abs(df_current[df_current["amount"] < 0]["amount"].sum())
    current_net = current_income - current_expenses

    # Get previous month data (if exists)
    current_idx = all_months.index(current_month)
    has_previous = current_idx > 0

    result = {
        "current_month": current_month,
        "current_income": current_income,
        "current_expenses": current_expenses,
        "current_net": current_net,
        "has_previous": has_previous,
    }

    if has_previous:
        previous_month = all_months[current_idx - 1]
        df_previous = df_copy[df_copy["year_month"] == previous_month]
        previous_income = df_previous[df_previous["amount"] > 0]["amount"].sum()
        previous_expenses = abs(df_previous[df_previous["amount"] < 0]["amount"].sum())
        previous_net = previous_income - previous_expenses

        result["previous_month"] = previous_month
        result["previous_income"] = previous_income
        result["previous_expenses"] = previous_expenses
        result["previous_net"] = previous_net

        # Calculate € and % changes
        result["income_change_pct"] = (
            ((current_income - previous_income) / previous_income * 100)
            if previous_income != 0 else None
        )
        result["expenses_change_pct"] = (
            ((current_expenses - previous_expenses) / previous_expenses * 100)
            if previous_expenses != 0 else None
        )
        result["expenses_change_euros"] = current_expenses - previous_expenses
        result["net_change_pct"] = (
            ((current_net - previous_net) / abs(previous_net) * 100)
            if previous_net != 0 else None
        )
        result["net_change_euros"] = current_net - previous_net
    else:
        result["income_change_pct"] = None
        result["expenses_change_pct"] = None
        result["expenses_change_euros"] = None
        result["net_change_pct"] = None

    return result


def calculate_burn_rate(df: pd.DataFrame, target_month: str = None) -> dict:
    """
    Calculate burn rate (€/day) for a given month.

    Args:
        df: DataFrame with 'date' and 'amount' columns
        target_month: Target month as string (YYYY-MM). If None, uses most recent month.

    Returns:
        Dictionary with keys:
            - burn_rate_per_day: average expenses per day with transactions
            - total_expenses: total expenses for the month
            - days_with_transactions: number of days with transactions
            - month: month label (YYYY-MM)
    """
    df_copy = df.copy()
    df_copy["year_month"] = df_copy["date"].dt.to_period("M").astype(str)

    if target_month is None:
        target_month = df_copy["year_month"].max()

    df_month = df_copy[df_copy["year_month"] == target_month]

    if len(df_month) == 0:
        return {
            "burn_rate_per_day": 0,
            "total_expenses": 0,
            "days_with_transactions": 0,
            "month": target_month,
        }

    # Total expenses (as positive value)
    total_expenses = abs(df_month[df_month["amount"] < 0]["amount"].sum())

    # Count distinct days with transactions
    days_with_transactions = df_month["date"].dt.date.nunique()

    # Burn rate = total expenses / days with transactions
    burn_rate = total_expenses / days_with_transactions if days_with_transactions > 0 else 0

    return {
        "burn_rate_per_day": burn_rate,
        "total_expenses": total_expenses,
        "days_with_transactions": days_with_transactions,
        "month": target_month,
    }


def calculate_savings_rate(income: float, expenses: float) -> float:
    """
    Calculate savings rate as a percentage.

    Args:
        income: Total income amount
        expenses: Total expenses amount (as positive value)

    Returns:
        Savings rate as percentage, or 0 if income is 0
    """
    if income <= 0:
        return 0.0
    return ((income - expenses) / income) * 100


def get_category_spend_6months(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get spending by category for the last 6 months.
    Returns only categories that appear in all 6 months (as requested).

    Args:
        df: DataFrame with 'date', 'category', and 'amount' columns

    Returns:
        DataFrame with columns: month, category, total
        Indexed by month ascending, with top 8 categories + "Other"
    """
    df_copy = df.copy()
    df_copy["year_month"] = df_copy["date"].dt.to_period("M").astype(str)

    # Get last 6 months
    all_months = sorted(df_copy["year_month"].unique())
    last_6_months = all_months[-6:] if len(all_months) >= 6 else all_months

    # Filter to these months
    df_6m = df_copy[df_copy["year_month"].isin(last_6_months)].copy()

    # Only expenses (negative amounts)
    df_6m_expenses = df_6m[df_6m["amount"] < 0].copy()

    # Group by month and category
    monthly_cat = df_6m_expenses.groupby(["year_month", "category"])["amount"].apply(lambda x: abs(x.sum())).reset_index()
    monthly_cat.columns = ["month", "category", "total"]

    # Find categories that appear in all 6 months
    months_set = set(last_6_months)
    category_months = monthly_cat.groupby("category")["month"].apply(set).reset_index()
    active_categories = category_months[category_months["month"] == months_set]["category"].tolist()

    # Filter to active categories only
    monthly_cat_filtered = monthly_cat[monthly_cat["category"].isin(active_categories)].copy()

    # Get top 8 categories by total spending across 6 months
    category_totals = monthly_cat_filtered.groupby("category")["total"].sum().nlargest(8)
    top_8_categories = category_totals.index.tolist()

    # Split: top 8 categories and "Other"
    result_list = []
    for month in last_6_months:
        df_month = monthly_cat_filtered[monthly_cat_filtered["month"] == month]

        # Add top 8 categories
        for cat in top_8_categories:
            cat_data = df_month[df_month["category"] == cat]
            if len(cat_data) > 0:
                result_list.append({
                    "month": month,
                    "category": cat,
                    "total": cat_data["total"].values[0]
                })

        # Calculate "Other" (all remaining categories)
        other_categories = df_month[~df_month["category"].isin(top_8_categories)]
        other_total = other_categories["total"].sum()
        if other_total > 0:
            result_list.append({
                "month": month,
                "category": "Other",
                "total": other_total
            })

    result = pd.DataFrame(result_list)
    return result
