Personal Finance Analysis App - Plan                                                          │
     │                                                                                               │
     │ Decisions Made                                                                                │
     │ ┌──────────────────┬─────────────────────────────────────────────────────────┐                │
     │ │     Decision     │                         Choice                          │                │
     │ ├──────────────────┼─────────────────────────────────────────────────────────┤                │
     │ │ Framework        │ Streamlit                                               │                │
     │ ├──────────────────┼─────────────────────────────────────────────────────────┤                │
     │ │ Deployment       │ Streamlit Community Cloud (private, password-protected) │                │
     │ ├──────────────────┼─────────────────────────────────────────────────────────┤                │
     │ │ Storage          │ CSV files only (reload on each run)                     │                │
     │ ├──────────────────┼─────────────────────────────────────────────────────────┤                │
     │ │ Category mapping │ Python dictionary in config.py                          │                │
     │ └──────────────────┴─────────────────────────────────────────────────────────┘                │
     │ ---                                                                                           │
     │ Data Source                                                                                   │
     │                                                                                               │
     │ - File: CaixaBank CSV export                                                                  │
     │ - Schema: Concepto;Fecha;Importe;Saldo (Description, Date, Amount, Balance)                   │
     │ - Formats: Date=DD/MM/YYYY, Amount=±X,XXEUR (comma decimal, EUR suffix)                       │
     │ - Delimiter: Semicolon (;)                                                                    │
     │                                                                                               │
     │ ---                                                                                           │
     │ Project Structure                                                                             │
     │                                                                                               │
     │ personal-finances-caixabank/                                                                  │
     │ ├── app.py                    # Main Streamlit app                                            │
     │ ├── data_loader.py            # CSV parsing + validation                                      │
     │ ├── categories.py             # Category mapping dictionary + logic                           │
     │ ├── analysis.py               # Analysis functions (timeseries, categories)                   │
     │ ├── data/                                                                                     │
     │ │   └── *.csv                 # Bank CSV files (gitignored)                                   │
     │ ├── .streamlit/                                                                               │
     │ │   └── secrets.toml          # Password (gitignored, set in Streamlit Cloud)                 │
     │ ├── requirements.txt                                                                          │
     │ ├── .gitignore                                                                                │
     │ └── README.md                                                                                 │
     │                                                                                               │
     │ ---                                                                                           │
     │ Implementation Steps                                                                          │
     │                                                                                               │
     │ Step 1: Data Loader (data_loader.py)                                                          │
     │                                                                                               │
     │ - Load CSV with correct encoding and delimiter                                                │
     │ - Parse amounts: strip EUR, convert comma to dot, handle +/- signs                            │
     │ - Parse dates: DD/MM/YYYY to datetime                                                         │
     │ - Validate schema: check required columns exist                                               │
     │ - Return clean pandas DataFrame                                                               │
     │                                                                                               │
     │ Step 2: Category Mapping (categories.py)                                                      │
     │                                                                                               │
     │ - Python dict mapping keywords to categories                                                  │
     │ - Matching logic: check if keyword is contained in transaction description (case-insensitive) │
     │ - Return "Uncategorized" for unmatched transactions                                           │
     │ - Initial categories based on your data:                                                      │
     │   - Groceries: MERCADONA, CONSUM, ALDI, CARREFOUR                                             │
     │   - Utilities: NATURGY, LUZ                                                                   │
     │   - Transport: RENFE, EESS (gas stations), PARKING                                            │
     │   - Insurance: LINEA DIRECTA                                                                  │
     │   - Internet/TV: CHARTER, QUATTRO                                                             │
     │   - ATM: REINT.CAJERO                                                                         │
     │   - Income: NOMINA, TRASPASO, TRANSF                                                          │
     │   - etc.                                                                                      │
     │                                                                                               │
     │ Step 3: Analysis Functions (analysis.py)                                                      │
     │                                                                                               │
     │ - daily_totals(df) → spending per day                                                         │
     │ - monthly_summary(df) → income vs expenses per month                                          │
     │ - category_breakdown(df) → spending by category                                               │
     │ - top_merchants(df, n=10) → most frequent/expensive merchants                                 │
     │                                                                                               │
     │ Step 4: Streamlit App (app.py)                                                                │
     │                                                                                               │
     │ - Password gate at the top (using st.secrets)                                                 │
     │ - Sidebar:                                                                                    │
     │   - Auto-load from data/ folder if CSV files exist                                            │
     │   - File uploader to override/add new data                                                    │
     │   - Uploaded files processed in-memory (not saved to disk)                                    │
     │ - Main area:                                                                                  │
     │   - Overview: Total income, total expenses, net, date range                                   │
     │   - Time Series tab: Line charts (daily/monthly/yearly)                                       │
     │   - Categories tab: Pie chart, bar chart, table                                               │
     │   - Transactions tab: Searchable/filterable table                                             │
     │   - Uncategorized tab: List transactions needing mapping                                      │
     │                                                                                               │
     │ Step 5: Deployment Setup                                                                      │
     │                                                                                               │
     │ - Add .gitignore (exclude data/*.csv, .streamlit/secrets.toml)                                │
     │ - Create requirements.txt                                                                     │
     │ - Push to GitHub (your existing repo)                                                         │
     │ - Connect to Streamlit Community Cloud                                                        │
     │ - Set password in Streamlit Cloud secrets panel                                               │
     │                                                                                               │
     │ ---                                                                                           │
     │ Password Protection                                                                           │
     │                                                                                               │
     │ Simple pattern in app.py:                                                                     │
     │ def check_password():                                                                         │
     │     password = st.text_input("Password", type="password")                                     │
     │     if password == st.secrets["password"]:                                                    │
     │         return True                                                                           │
     │     if password:                                                                              │
     │         st.error("Incorrect password")                                                        │
     │     return False                                                                              │
     │                                                                                               │
     │ if not check_password():                                                                      │
     │     st.stop()                                                                                 │
     │                                                                                               │
     │ In Streamlit Cloud, set password = "your_secret" in the Secrets panel.                        │
     │                                                                                               │
     │ ---                                                                                           │
     │ Files to Modify/Create                                                                        │
     │ ┌─────────────────────────┬──────────────────────────────────┐                                │
     │ │          File           │              Action              │                                │
     │ ├─────────────────────────┼──────────────────────────────────┤                                │
     │ │ app.py                  │ Create - main Streamlit app      │                                │
     │ ├─────────────────────────┼──────────────────────────────────┤                                │
     │ │ data_loader.py          │ Create - CSV parsing             │                                │
     │ ├─────────────────────────┼──────────────────────────────────┤                                │
     │ │ categories.py           │ Create - category mapping dict   │                                │
     │ ├─────────────────────────┼──────────────────────────────────┤                                │
     │ │ analysis.py             │ Create - analysis functions      │                                │
     │ ├─────────────────────────┼──────────────────────────────────┤                                │
     │ │ requirements.txt        │ Create - dependencies            │                                │
     │ ├─────────────────────────┼──────────────────────────────────┤                                │
     │ │ .gitignore              │ Create - exclude sensitive files │                                │
     │ ├─────────────────────────┼──────────────────────────────────┤                                │
     │ │ .streamlit/secrets.toml │ Create locally (gitignored)      │                                │
     │ └─────────────────────────┴──────────────────────────────────┘                                │
     │ ---                                                                                           │
     │ Verification Plan                                                                             │
     │                                                                                               │
     │ 1. Run locally: streamlit run app.py                                                          │
     │ 2. Test CSV loading with the existing CaixaBank file                                          │
     │ 3. Verify password gate works                                                                 │
     │ 4. Check all charts render correctly                                                          │
     │ 5. Deploy to Streamlit Cloud and verify remote access                                         │
     ╰───────────────────────────────────────────────────────────────────────────────────────────────╯
