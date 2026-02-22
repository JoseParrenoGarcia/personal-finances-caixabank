# Main Streamlit app

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import os

from data_loader import load_csv, load_csv_from_bytes
from categories import add_categories
from analysis import (
    daily_totals,
    monthly_summary,
    yearly_summary,
    category_breakdown,
    top_merchants,
    get_uncategorized,
    get_summary_stats,
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

    # Try to load from data/ folder first
    csv_files = list(data_folder.glob("*.csv")) if data_folder.exists() else []

    # Sidebar: file selection/upload
    st.sidebar.header("Data Source")

    if csv_files:
        st.sidebar.info(f"Found {len(csv_files)} CSV file(s) in data/ folder")
        file_path = csv_files[0]  # Load first file
        st.sidebar.text(f"Loading: {file_path.name}")
        df = load_csv(str(file_path))
    else:
        st.sidebar.warning("No CSV files found in data/ folder")
        df = None

    # File uploader
    st.sidebar.subheader("Or upload a file")
    uploaded_file = st.sidebar.file_uploader("Upload CaixaBank CSV", type="csv")

    if uploaded_file is not None:
        try:
            df = load_csv_from_bytes(uploaded_file)
            st.sidebar.success(f"Loaded {len(df)} transactions")
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")
            df = None

    return df


def display_overview(df, stats):
    """Display monthly metrics for current and previous 2 months."""
    # Get monthly summary
    monthly = monthly_summary(df)

    # Get last 3 months (most recent first)
    if len(monthly) > 0:
        last_3_months = monthly.tail(3).iloc[::-1]  # Reverse to show most recent first
    else:
        last_3_months = monthly

    # Display metrics for each month
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


def display_categories(df):
    """Display category analysis for current and previous 2 months."""
    st.subheader("Category Analysis")

    tab1, tab2 = st.tabs(["Bar Chart", "Table"])

    # Get monthly data
    monthly = monthly_summary(df)

    # Get last 3 months (most recent first)
    if len(monthly) > 0:
        last_3_months = monthly.tail(3).iloc[::-1]  # Reverse to show most recent first
    else:
        last_3_months = monthly

    with tab1:
        # Add year_month column to df
        df["year_month"] = df["date"].dt.to_period("M").astype(str)

        # Collect data for all 3 months
        months_data = []
        for idx, row in last_3_months.iterrows():
            month_str = row["year_month"]
            df_month = df[df["year_month"] == month_str]
            cat_data = category_breakdown(df_month)
            months_data.append((month_str, cat_data))

        # Find global max value for consistent y-axis scale
        global_max = 0
        for month_str, cat_data in months_data:
            if len(cat_data) > 0:
                global_max = max(global_max, cat_data["total"].max())

        # Create subplots with shared y-axis
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=[month for month, _ in months_data],
            shared_yaxes=False,
            vertical_spacing=0.1
        )

        # Add traces for each month
        for row_idx, (month_str, cat_data) in enumerate(months_data, start=1):
            if len(cat_data) > 0:
                # Map colors to categories
                bar_colors = [CATEGORY_COLORS.get(cat, CATEGORY_COLORS["Uncategorized"]) for cat in cat_data["category"]]

                fig.add_trace(
                    go.Bar(
                        x=cat_data["category"],
                        y=cat_data["total"],
                        text=[f"€{val:,.0f}" for val in cat_data["total"]],
                        textposition="outside",
                        name=month_str,
                        marker=dict(color=bar_colors),
                        showlegend=False
                    ),
                    row=row_idx, col=1
                )
                fig.update_xaxes(tickangle=-45, row=row_idx, col=1)
                # Set same y-axis range for all subplots
                fig.update_yaxes(range=[0, global_max * 1.1], row=row_idx, col=1)

        fig.update_layout(height=1000, showlegend=False)
        fig.update_yaxes(title_text="Amount (€)", row=1, col=1)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        cat_data = category_breakdown(df)
        st.dataframe(cat_data, use_container_width=True)


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
