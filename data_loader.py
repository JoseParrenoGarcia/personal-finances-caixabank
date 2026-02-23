import pandas as pd
import io
from typing import Union
from pathlib import Path
import streamlit as st

# Transactions to exclude (internal transfers, etc.)
EXCLUDE_KEYWORDS = ["TRASPASO PROPIO"]


def parse_amount(amount_str: str) -> float:
    """
    Parse CaixaBank amount format: ±X.XXX,XXEUR (European format)
    Strips EUR, removes thousands separator (dots), converts decimal comma to dot.
    Returns float value.
    """
    # Remove EUR suffix
    amount_str = amount_str.replace("EUR", "").strip()
    # Remove thousands separator (dots)
    amount_str = amount_str.replace(".", "")
    # Convert comma decimal to dot
    amount_str = amount_str.replace(",", ".")
    return float(amount_str)


def parse_date(date_str: str) -> pd.Timestamp:
    """
    Parse CaixaBank date format: DD/MM/YYYY
    Returns datetime object.
    """
    return pd.to_datetime(date_str, format="%d/%m/%Y")


@st.cache_data(ttl=3600)
def load_csv(filepath: str) -> pd.DataFrame:
    """
    Load and parse CaixaBank CSV file.

    Args:
        filepath: Path to CSV file

    Returns:
        Clean pandas DataFrame with parsed amounts, dates, and renamed columns

    Raises:
        ValueError: If schema validation fails
        FileNotFoundError: If file doesn't exist
    """
    # Load CSV with correct delimiter and encoding
    df = pd.read_csv(filepath, sep=";", encoding="utf-8")

    # Validate schema
    required_columns = ["Concepto", "Fecha", "Importe", "Saldo"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Missing required columns. Expected: {required_columns}, Got: {list(df.columns)}")

    # Filter out excluded transactions
    df = _filter_excluded_transactions(df)

    # Parse amounts
    df["Importe"] = df["Importe"].apply(parse_amount)
    df["Saldo"] = df["Saldo"].apply(parse_amount)

    # Parse dates
    df["Fecha"] = df["Fecha"].apply(parse_date)

    # Rename columns to snake_case for consistency
    df = df.rename(columns={
        "Concepto": "description",
        "Fecha": "date",
        "Importe": "amount",
        "Saldo": "balance"
    })

    # Sort by date ascending (oldest first)
    df = df.sort_values("date").reset_index(drop=True)

    return df


@st.cache_data(ttl=3600)
def load_csv_from_bytes(file_bytes: Union[bytes, io.BytesIO]) -> pd.DataFrame:
    """
    Load and parse CaixaBank CSV from uploaded file bytes.
    Used for Streamlit file uploader.

    Args:
        file_bytes: File bytes or BytesIO object

    Returns:
        Clean pandas DataFrame
    """
    df = pd.read_csv(file_bytes, sep=";", encoding="utf-8")

    # Validate schema
    required_columns = ["Concepto", "Fecha", "Importe", "Saldo"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Missing required columns. Expected: {required_columns}, Got: {list(df.columns)}")

    # Filter out excluded transactions
    df = _filter_excluded_transactions(df)

    # Parse amounts
    df["Importe"] = df["Importe"].apply(parse_amount)
    df["Saldo"] = df["Saldo"].apply(parse_amount)

    # Parse dates
    df["Fecha"] = df["Fecha"].apply(parse_date)

    # Rename columns
    df = df.rename(columns={
        "Concepto": "description",
        "Fecha": "date",
        "Importe": "amount",
        "Saldo": "balance"
    })

    # Sort by date ascending
    df = df.sort_values("date").reset_index(drop=True)

    return df


def _filter_excluded_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter out transactions that should be excluded from analysis.

    Args:
        df: DataFrame with 'Concepto' column

    Returns:
        Filtered DataFrame
    """
    mask = ~df["Concepto"].str.contains("|".join(EXCLUDE_KEYWORDS), case=False, na=False)
    return df[mask]


@st.cache_data(ttl=3600)
def load_all_csv_files(data_folder: str = "data") -> pd.DataFrame:
    """
    Load and merge all CSV files from data folder.
    Adds 'account' column to identify which file each transaction came from.

    Args:
        data_folder: Path to folder containing CSV files

    Returns:
        Merged DataFrame with all transactions and account column, or None if no files found
    """
    data_path = Path(data_folder)
    csv_files = list(data_path.glob("*.csv")) if data_path.exists() else []

    if not csv_files:
        return None

    dfs = []
    for filepath in sorted(csv_files):
        try:
            df = load_csv(str(filepath))
            # Add account column based on filename (without .csv extension)
            df["account"] = filepath.stem
            dfs.append(df)
        except Exception as e:
            print(f"Warning: Failed to load {filepath}: {e}")

    if dfs:
        merged_df = pd.concat(dfs, ignore_index=True).sort_values("date").reset_index(drop=True)
        return merged_df
    return None
