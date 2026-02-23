# Main Streamlit app

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

from data_loader import load_csv_from_bytes, load_all_csv_files
from categories import add_categories
from analysis import (
    monthly_summary,
    yearly_summary,
    category_breakdown,
    get_uncategorized,
    get_summary_stats,
    get_month_comparison_data,
    calculate_burn_rate,
    calculate_savings_rate,
    get_category_spend_6months,
)

# Predefined colors for categories
CATEGORY_COLORS = {
    "Groceries": "#1f77b4",
    "Energy": "#ff7f0e",
    "Water": "#ffbb78",
    "Transport": "#2ca02c",
    "Insurance": "#d62728",
    "Internet/TV": "#9467bd",
    "ATM": "#8c564b",
    "Income": "#e377c2",
    "Pharmacy": "#7f7f7f",
    "Health": "#bcbd22",
    "Fitness": "#17becf",
    "Shopping": "#aec7e8",
    "Dining": "#ff9896",
    "Entertainment": "#98df8a",
    "Education": "#c5b0d5",
    "Car": "#c49c94",
    "House": "#f7b6d2",
    "Travel": "#c7c7c7",
    "Ayuntamiento": "#ff6b6b",
    "Amazon (others)": "#fbb4ae",
    "Uncategorized": "#cccccc",
}

st.set_page_config(page_title="Personal Finance Analysis", layout="wide", initial_sidebar_state="collapsed")


def check_password():
    """Check password from st.secrets."""
    if "password" not in st.secrets:
        st.warning("Password not configured in secrets")
        return True

    password = st.text_input("Enter password", type="password")
    if password == st.secrets["password"]:
        return True
    if password:
        st.error("Incorrect password")
    return False


def load_data():
    """Load CSV data from folder or uploaded file."""
    data_folder = Path("data")

    # Sidebar: file selection/upload
    st.sidebar.header("Data Source")

    # Try to load all CSV files from data/ folder
    csv_files = list(data_folder.glob("*.csv")) if data_folder.exists() else []

    if csv_files:
        st.sidebar.info(f"Found {len(csv_files)} CSV file(s) in data/ folder")
        df = load_all_csv_files("data")
        if df is not None:
            st.sidebar.text(f"Loaded {len(df)} transactions from {len(csv_files)} account(s)")
    else:
        st.sidebar.warning("No CSV files found in data/ folder")
        df = None

    # File uploader for additional data
    st.sidebar.subheader("Or upload a file")
    uploaded_file = st.sidebar.file_uploader("Upload CaixaBank CSV", type="csv")

    if uploaded_file is not None:
        try:
            df_uploaded = load_csv_from_bytes(uploaded_file)
            st.sidebar.success(f"Loaded {len(df_uploaded)} transactions")
            # Merge with existing data if present
            if df is not None:
                df = pd.concat([df, df_uploaded], ignore_index=True).sort_values("date").reset_index(drop=True)
            else:
                df = df_uploaded
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")

    return df


def display_overview(df, stats):
    """Display hero section with current month KPIs and previous 2 months history."""
    # Get comparison data for current vs previous month
    comparison = get_month_comparison_data(df)

    if not comparison:
        st.info("No data available for overview")
        return

    # Get burn rate for current month
    burn_rate_data = calculate_burn_rate(df)
    savings_rate = calculate_savings_rate(
        comparison["current_income"],
        comparison["current_expenses"]
    )

    # Hero section: current month with KPIs
    st.subheader("📊 Current Month Overview")

    # Check for expense anomaly (>20% change)
    expense_alert = None
    if comparison["has_previous"] and comparison["expenses_change_pct"] is not None:
        if comparison["expenses_change_pct"] > 20:
            expense_alert = "warning"
        elif comparison["expenses_change_pct"] < -20:
            expense_alert = "success"

    # Alert banner if significant expense change
    if expense_alert == "warning":
        change_amount = comparison["expenses_change_euros"]
        change_pct = comparison["expenses_change_pct"]
        st.warning(
            f"⚠️ Expenses increased by €{abs(change_amount):,.2f} ({change_pct:+.1f}%) - Monitor spending!"
        )
    elif expense_alert == "success":
        change_amount = comparison["expenses_change_euros"]
        change_pct = comparison["expenses_change_pct"]
        st.success(
            f"✓ Expenses decreased by €{abs(change_amount):,.2f} ({change_pct:+.1f}%)"
        )

    # Hero card: 6 metrics in 3 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        # Net (primary metric)
        delta_value = None
        if comparison["has_previous"] and comparison["net_change_pct"] is not None:
            delta_value = f"€{comparison['net_change_euros']:+,.0f} ({comparison['net_change_pct']:+.1f}%)"
        st.metric(
            "Net",
            f"€{comparison['current_net']:,.2f}",
            delta=delta_value,
            delta_color="normal"
        )

        # Income
        delta_income = None
        if comparison["has_previous"] and comparison["income_change_pct"] is not None:
            delta_income = f"{comparison['income_change_pct']:+.1f}%"
        st.metric(
            "Income",
            f"€{comparison['current_income']:,.2f}",
            delta=delta_income
        )

    with col2:
        # Expenses
        delta_expenses = None
        if comparison["has_previous"] and comparison["expenses_change_pct"] is not None:
            delta_expenses = f"€{comparison['expenses_change_euros']:+,.0f} ({comparison['expenses_change_pct']:+.1f}%)"
        st.metric(
            "Expenses",
            f"€{comparison['current_expenses']:,.2f}",
            delta=delta_expenses,
            delta_color="inverse"
        )

        # Savings Rate
        st.metric(
            "Savings Rate",
            f"{savings_rate:.1f}%"
        )

    with col3:
        # Burn Rate (€/day)
        st.metric(
            "Burn Rate",
            f"€{burn_rate_data['burn_rate_per_day']:,.2f}/day"
        )

        # Month label
        st.metric(
            "Period",
            comparison["current_month"]
        )

    st.markdown("---")

    # Historical context: previous 2 months
    st.subheader("📈 Recent History")
    monthly = monthly_summary(df)

    # Get last 3 months (most recent first) for display
    if len(monthly) > 0:
        last_3_months = monthly.tail(3).iloc[::-1]  # Reverse to show most recent first
    else:
        last_3_months = monthly

    # Display in simple 4-column layout (no deltas, just raw values for context)
    for idx, row in last_3_months.iterrows():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Month", row["year_month"])

        with col2:
            st.metric("Income", f"€{row['income']:,.2f}")

        with col3:
            st.metric("Expenses", f"€{row['expenses']:,.2f}")

        with col4:
            st.metric("Net", f"€{row['net']:,.2f}")

    st.markdown("---")


def display_time_series(df):
    """Display time series analysis."""
    st.subheader("Time Series Analysis")

    tab1, tab2 = st.tabs(["Monthly", "Yearly"])

    with tab1:
        monthly = monthly_summary(df)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly["year_month"], y=monthly["expenses"], name="Expenses", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=monthly["year_month"], y=monthly["income"], name="Income", mode="lines+markers"))
        fig.layout.update(title="Monthly Summary", xaxis_title="Month", yaxis_title="Amount (€)")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        yearly = yearly_summary(df)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=yearly["year"], y=yearly["expenses"], name="Expenses", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=yearly["year"], y=yearly["income"], name="Income", mode="lines+markers"))
        fig.layout.update(title="Yearly Summary", xaxis_title="Year", yaxis_title="Amount (€)")
        st.plotly_chart(fig, use_container_width=True)


def display_horizontal_bar_chart(df):
    """Display 3 horizontal bar charts for current and previous 2 months (columns layout)."""
    # Get monthly data
    monthly = monthly_summary(df)

    # Get last 3 months (most recent first)
    if len(monthly) > 0:
        last_3_months = monthly.tail(3).iloc[::-1]  # Reverse to show most recent first
    else:
        st.info("No data available for chart")
        return

    # Add year_month column to df
    df["year_month"] = df["date"].dt.to_period("M").astype(str)

    # Collect data for all 3 months
    months_data = []
    for idx, row in last_3_months.iterrows():
        month_str = row["year_month"]
        df_month = df[df["year_month"] == month_str]
        cat_data = category_breakdown(df_month)
        months_data.append((month_str, cat_data))

    # Find global max value for consistent x-axis scale
    global_max = 0
    for month_str, cat_data in months_data:
        if len(cat_data) > 0:
            global_max = max(global_max, cat_data["total"].max())

    # Create consistent category order based on logic:
    # 1. Categories in first month, sorted by spend descending
    # 2. Categories NOT in first month (missing), sorted by spend

    first_month_categories = set(months_data[0][1]["category"].values)

    # Get categories in first month, sorted by spend ascending (so they appear descending on chart)
    first_month_data = months_data[0][1].sort_values("total", ascending=True)
    first_month_order = first_month_data["category"].tolist()

    # Get all categories from all months
    all_categories = set()
    for _, cat_data in months_data:
        all_categories.update(cat_data["category"].values)

    # Get missing categories (not in first month but in others)
    missing_categories = sorted(all_categories - first_month_categories)

    # Combine: missing categories first (will appear at bottom), then first month categories
    category_order = missing_categories + first_month_order

    # Create subplots with 3 columns
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[month for month, _ in months_data],
        shared_yaxes=True,
        horizontal_spacing=0.05
    )

    # Add traces for each month
    for col_idx, (month_str, cat_data) in enumerate(months_data, start=1):
        if len(cat_data) > 0:
            # Reindex to use consistent category order from all months
            cat_data = cat_data.set_index("category").reindex(category_order).reset_index()
            cat_data["total"] = cat_data["total"].fillna(0)

            # Map colors to categories
            bar_colors = [CATEGORY_COLORS.get(cat, CATEGORY_COLORS["Uncategorized"]) for cat in cat_data["category"]]

            # Add horizontal bar for this month
            fig.add_trace(
                go.Bar(
                    y=cat_data["category"],
                    x=cat_data["total"],
                    orientation="h",
                    text=[f"€{val:,.0f}" for val in cat_data["total"]],
                    textposition="outside",
                    marker=dict(color=bar_colors),
                    showlegend=False,
                    hovertemplate="%{y}: €%{x:,.0f}<extra></extra>",
                ),
                row=1, col=col_idx
            )

            # Update x-axis range for consistency
            fig.update_xaxes(range=[0, global_max * 1.15], row=1, col=col_idx)

    # Set x-axis titles
    fig.update_xaxes(title_text="Amount (€)", row=1, col=1)
    fig.update_xaxes(title_text="Amount (€)", row=1, col=2)
    fig.update_xaxes(title_text="Amount (€)", row=1, col=3)

    # Add faint gridlines and axis lines
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(200, 200, 200, 0.3)",
        showline=True,
        linewidth=1,
        linecolor="rgba(100, 100, 100, 0.3)",
        row=1, col=1
    )
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(200, 200, 200, 0.3)",
        showline=True,
        linewidth=1,
        linecolor="rgba(100, 100, 100, 0.3)",
        row=1, col=2
    )
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(200, 200, 200, 0.3)",
        showline=True,
        linewidth=1,
        linecolor="rgba(100, 100, 100, 0.3)",
        row=1, col=3
    )

    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor="rgba(100, 100, 100, 0.3)",
        row=1, col=1
    )

    height = 400 + (len(months_data[0][1]) * 25 if months_data else 0)
    fig.update_layout(height=height, showlegend=False)

    st.plotly_chart(fig, use_container_width=True)


def display_category_transactions(df, category, month_str):
    """Display transactions for a selected category and month."""
    # Filter by month and category
    df["year_month"] = df["date"].dt.to_period("M").astype(str)
    df_filtered = df[(df["year_month"] == month_str) & (df["category"] == category)].copy()

    if len(df_filtered) == 0:
        st.info(f"No transactions found for {category} in {month_str}")
        return

    # Sort by date descending
    df_filtered = df_filtered.sort_values("date", ascending=False)

    # Display summary
    total_amount = df_filtered["amount"].sum()
    num_transactions = len(df_filtered)
    st.metric("Total", f"€{abs(total_amount):,.2f}")
    st.caption(f"{num_transactions} transaction(s)")

    # Display table
    display_df = df_filtered[["date", "description", "amount"]].copy()
    display_df["date"] = display_df["date"].dt.strftime("%d/%m/%Y")
    display_df["amount"] = display_df["amount"].apply(lambda x: f"€{x:,.2f}")

    st.dataframe(display_df, use_container_width=True, hide_index=True)


def display_stacked_area_chart(df):
    """Display stacked area chart showing spending composition over 6 months."""
    st.subheader("Spending Composition (6 Months)")

    # Get 6-month category data
    spend_data = get_category_spend_6months(df)

    if len(spend_data) == 0:
        st.info("Not enough data for 6-month comparison")
        return

    # Create pivot table: months as index, categories as columns
    pivot_data = spend_data.pivot(index="month", columns="category", values="total").fillna(0)

    # Sort categories by latest month spending (descending)
    latest_month = pivot_data.index[-1]
    category_order = pivot_data.loc[latest_month].sort_values(ascending=False).index.tolist()

    # Create stacked area chart
    fig = go.Figure()

    # Add traces in sorted order (latest month spending from high to low)
    for category in category_order:
        color = CATEGORY_COLORS.get(category, CATEGORY_COLORS["Uncategorized"])
        fig.add_trace(go.Scatter(
            x=pivot_data.index,
            y=pivot_data[category],
            mode="lines",
            name=category,
            line=dict(color=color, width=2),
            fillcolor=color,
            stackgroup="one",
            hovertemplate=f"{category}<br>€%{{y:,.0f}}<extra></extra>",
        ))

    fig.update_layout(
        title="Category Spending Trends (6 Months)",
        xaxis_title="Month",
        yaxis_title="Spending (€)",
        hovermode="x unified",
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)


def display_categories(df):
    """Display category analysis for current and previous 2 months."""
    st.subheader("Category Analysis")

    tab1, tab2 = st.tabs(["Horizontal Bar", "Spending Trends"])

    with tab1:
        col1, col2 = st.columns([2, 1])

        with col1:
            display_horizontal_bar_chart(df)

        with col2:
            st.markdown("**Filter Transactions**")

            # Get available months
            df["year_month"] = df["date"].dt.to_period("M").astype(str)
            available_months = sorted(df["year_month"].unique(), reverse=True)

            # Month dropdown
            selected_month = st.selectbox("Month", available_months, key="month_select")

            # Category dropdown
            df_filtered_month = df[df["year_month"] == selected_month]
            available_categories = sorted(df_filtered_month["category"].unique())
            selected_category = st.selectbox("Category", available_categories, key="category_select", placeholder="Groceries")

            # Display transactions for selected month and category
            if selected_month and selected_category:
                display_category_transactions(df, selected_category, selected_month)

    with tab2:
        display_stacked_area_chart(df)


def display_transactions(df):
    """Display searchable transaction table."""
    st.subheader("All Transactions")

    # Search/filter
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("Search description")
    with col2:
        selected_category = st.selectbox("Filter by category", ["All"] + df["category"].unique().tolist())

    df_filtered = df.copy()

    if search:
        df_filtered = df_filtered[df_filtered["description"].str.contains(search, case=False, na=False)]

    if selected_category != "All":
        df_filtered = df_filtered[df_filtered["category"] == selected_category]

    # Sort by date descending (newest first)
    df_filtered = df_filtered.sort_values("date", ascending=False)

    # Display table
    display_df = df_filtered[["date", "description", "amount", "category", "balance"]].copy()
    display_df["date"] = display_df["date"].dt.strftime("%d/%m/%Y")
    display_df["amount"] = display_df["amount"].apply(lambda x: f"€{x:,.2f}")
    display_df["balance"] = display_df["balance"].apply(lambda x: f"€{x:,.2f}")

    st.info(f"Showing {len(display_df)} transactions")
    st.dataframe(display_df, use_container_width=True)


def display_uncategorized(df):
    """Display uncategorized transactions."""
    st.subheader("Uncategorized Transactions")

    uncategorized = get_uncategorized(df)

    if len(uncategorized) == 0:
        st.success("No uncategorized transactions!")
    else:
        st.warning(f"{len(uncategorized)} uncategorized transactions found")

        display_df = uncategorized[["date", "description", "amount", "balance"]].copy()
        display_df["date"] = display_df["date"].dt.strftime("%d/%m/%Y")

        st.info("Add these keywords to categories.py to categorize them:")
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "amount": st.column_config.NumberColumn(format="€ %.2f"),
                "balance": st.column_config.NumberColumn(format="€ %.2f"),
            }
        )


def main():
    """Main app."""
    st.title("💰 Personal Finance Analysis")

    # Password gate
    if not check_password():
        st.stop()

    # Load data
    df = load_data()

    if df is None or len(df) == 0:
        st.error("No data loaded. Please upload a CSV file or add files to the data/ folder.")
        st.stop()

    # Add categories
    add_categories(df)

    # Calculate stats
    stats = get_summary_stats(df)

    # Overview
    display_overview(df, stats)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Time Series", "Categories", "Transactions", "Uncategorized"])

    with tab1:
        display_time_series(df)

    with tab2:
        display_categories(df)

    with tab3:
        display_transactions(df)

    with tab4:
        display_uncategorized(df)


if __name__ == "__main__":
    main()
