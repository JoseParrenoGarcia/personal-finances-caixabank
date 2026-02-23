# Personal Finance Dashboard - Expert Consultant Review

**Date:** 2026-02-23
**Focus:** Monthly deep-dive analysis with emphasis on category patterns and transaction details

---

## Executive Summary

Your dashboard has solid foundations but significant opportunities for improvement.

---

## Ideas to implement

### 2 views - savings account and spending account

The savings account needs to be defined.

```
┌──────────────────────────────────────┐
│ HERO SECTION                         │
├──────────────────────────────────────┤
│ 3 month section                      │
├──────────────────────────────────────┤
│ Saving account view (new)            │
├──────────────────────────────────────┤
│ TAB CATEGORY BREAKDOWN               │
│ - Horizontal bar charts.             │
│ - Heatmap                            │
│ - Spending changes (vs 3-month  avg) │
│ - If possible, when I click on a bar |
│ in the plotly chart, then show a     |
│ table with the transactions associa  |
│ with the bar.                        |
├──────────────────────────────────────┤
│ TAB TRANSACTIONS                     │ <- see Notable Transactions section for ideas
│ - A table to look at amounts         │
│ - Highest expense                    │
│ - New merchants                      │
│ - Unusual amounts                    │
├──────────────────────────────────────┤
│ TAB UNCATEGORIZED.                   │
│ - Uncategorized                      │
├──────────────────────────────────────┤
│ Saving account view (new)            │
└──────────────────────────────────────┘
```


---

### Notable Transactions

**Auto-surface transactions that need attention:**

```
🚨 NOTABLE TRANSACTIONS (This Month)

Highest Single Expense:
📍 15/02 - IKEA - €524.50 [Shopping]

New Merchants (First Time):
📍 12/02 - HOTEL Barcelona - €180 [Travel]
📍 08/02 - ZARA HOME - €65.20 [Shopping]

Unusual Amounts (>2x Category Average):
📍 20/02 - MERCADONA - €215.30 [Groceries] (avg: €85)
```

---

### Add Missing KPIs

**2. Period Comparisons:**
- Always show: "vs last month", "vs 3-month avg"
- Color code: Green (improving), Red (worsening), Gray (flat)

**3. Trend Indicators:**
- Add arrows and % changes to all metrics
- Show direction clearly: ▲ ▼ →

**4. Contextual Benchmarks:**
- Reference lines showing personal averages
- Help answer: "Is €800 on groceries high for me?"

---

## Visual Design Improvements

### Custom CSS
```css
.metric-card {
    padding: 1rem;
    border-radius: 0.5rem;
    background: #f8f9fa;
    border-left: 4px solid #4CAF50;
}

.section-header {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 2rem 0 1rem 0;
}

.alert-box-red {
    background: #f8d7da;
    border: 1px solid #dc3545;
}

.alert-box-green {
    background: #d4edda;
    border: 1px solid #28a745;
}
```

### Color Palette
**Current:** 20+ random colors, no semantic meaning

**Recommended:**
- Essentials (Groceries, Energy): Blues/Grays
- Discretionary (Dining, Entertainment): Warm colors
- Financial (Income): Green
- Use Plotly's colorblind-safe palette: `px.colors.qualitative.Safe`

---

## Data Quality Enhancements

### 1. Priority-Based Categorization
```python
# High priority (exact merchants)
CATEGORY_KEYWORDS_HIGH = {
    "Groceries": ["MERCADONA", "CARREFOUR", "LIDL"],
}

# Low priority (generic terms)
CATEGORY_KEYWORDS_LOW = {
    "Groceries": ["SUPER", "ALIMENTA"],
}
```

### 2. Activate Fuzzy Matching
```python
from rapidfuzz import fuzz  # Already in requirements.txt!

if fuzz.partial_ratio(description, keyword) > 85:
    category = matched_category
```

---

## Performance Optimization

**Add caching to expensive operations:**

```python
@st.cache_data(ttl=3600)  # 1 hour cache
def load_and_process_data(file_path):
    df = load_csv(file_path)
    add_categories(df)
    return df

@st.cache_data(ttl=3600)
def calculate_all_analyses(df):
    return {
        "monthly": monthly_summary(df),
        "categories": category_breakdown(df),
        "notable": get_notable_transactions(df),
        "kpis": calculate_kpis(df),
    }
```

**Benefits:**
- Instant re-renders on interactions
- No loading spinners
- Better UX overall