# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal finance analysis dashboard built with Streamlit for visualizing and analyzing CaixaBank transaction data. The app provides spending breakdowns by category, time-series trends, merchant analysis, and transaction filtering with password protection.

**Tech Stack**: Python 3.11, Streamlit, Pandas, Plotly, RapidFuzz

## Development Commands

| Command | Purpose |
|---------|---------|
| `make venv` | Create Python virtual environment |
| `make install` | Install dependencies (pip + ruff) |
| `make lint` | Run ruff linter checks |
| `make format` | Format code and auto-fix linting issues |
| `make run` | Launch Streamlit app locally (http://localhost:8501) |
| `make clean` | Remove venv and Python cache files |

**Quick Start**: `make install && make run`

## Architecture & Code Organization

The codebase follows a **layered separation of concerns** pattern:

### Data Layer: `data_loader.py`
Handles CSV parsing, validation, and data ingestion from CaixaBank exports.

**Expected CSV Format**: Semicolon-delimited, UTF-8, columns: `Concepto` (description), `Fecha` (date DD/MM/YYYY), `Importe` (amount), `Saldo` (balance). Amounts use European format with thousands separator (.) and decimal comma (,).

### Business Logic: `analysis.py`
Aggregations and analytics functions operating on categorized DataFrames.

**Convention**: All expense amounts are normalized to positive values internally; display methods handle negation.

### Configuration: `categories.py`
Transaction categorization via keyword matching against 20+ categories (Groceries, Energy, Transport, Dining, etc.).

**Matching Logic**: Case-insensitive substring matching—first match wins. Add categories by extending the `CATEGORY_KEYWORDS` dict.

### Presentation: `app.py`
Streamlit UI orchestration and visualizations.

**Key Features**:
- Password protection via `st.secrets["password"]`
- Auto-load from `data/` folder; manual file upload support
- Wide layout with collapsed sidebar
- Tabs: Overview, Time Series, Categories, Transactions, Uncategorized
- Color-coded categories (21+ predefined colors)
- Visualizations: Line charts (trends), horizontal bar charts (category comparison), data tables

## Data Flow

```
CSV File → parse_amount/date → DataFrame
  ↓
categorize_transaction → add 'category' column
  ↓
analysis functions → aggregations
  ↓
Streamlit visualizations → Dashboard
```

## Key Design Patterns

| Pattern | Implementation | Rationale |
|---------|----------------|-----------|
| **CSV-only storage** | No database | Simplicity, no backend needed |
| **Stateless reload** | Full CSV load per app run | Supports multiple users, no session state |
| **Substring categorization** | Python dict + first-match | Fast, maintainable |
| **Plotly visualizations** | Interactive, responsive | Rich interactivity, easy filtering |
| **Multi-account support** | `account` column in DataFrames | Track spending per account |

## Important Implementation Details

1. **Amount Handling**: Expenses are negative in CSV but stored as-is; display logic applies `abs()`. Use `analysis.py` functions which expect negative expenses.

2. **Date Handling**: All dates converted to pandas datetime; enables groupby operations like `df.groupby(df['Fecha'].dt.to_period('M'))`.

3. **Transaction Filtering**: Internal transfers (same merchant in/out) are excluded by `_filter_excluded_transactions()`.

4. **Uncategorized Transactions**: Default category is "Uncategorized"; identify via `get_uncategorized()` for review.

5. **Password Security**: Stored in `.streamlit/secrets.toml` (gitignored); Streamlit Cloud uses secrets panel.

## Configuration Files

- `requirements.txt` - Dependencies (Streamlit, Pandas, Plotly, RapidFuzz)
- `.streamlit/secrets.toml` - Password config (gitignored)
- `.gitignore` - Excludes data CSVs, secrets, venv

## Testing & Linting

- **Linter**: Ruff (via `make lint`)
- **Formatter**: Ruff (via `make format`)
- **Tests**: None currently; functions in `analysis.py` and `data_loader.py` are designed for unit testing

To test a single function interactively:
```python
python3 -c "from analysis import category_breakdown; from data_loader import load_all_csv_files; df = load_all_csv_files('data'); print(category_breakdown(df))"
```

## Adding Features

**New Analysis Function**: Add to `analysis.py`, accept DataFrame parameter, return aggregated result. Test via Python REPL.

**New Category**: Add key-value pair to `CATEGORY_KEYWORDS` in `categories.py`. Substring matching is case-insensitive.

**New Chart/Tab**: Add to `app.py` in the appropriate section (e.g., add tab in `st.tabs()`); call analysis functions and render via Plotly or Streamlit.

## Known Limitations

- Full CSV reload on every interaction (no caching between sessions)
- Basic keyword-based categorization (no ML)
- No transaction editing or annotation capability
- Static category definitions (no UI for adding categories without code)
