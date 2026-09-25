# UPI Transaction Intelligence Dashboard

## Problem Statement

UPI (Unified Payments Interface) has transformed digital payments in India, processing billions of transactions monthly. Businesses and banks need to understand payment patterns, identify failure causes, and optimize transaction success rates. This project simulates a real-world analytics scenario where a Data Analyst must extract actionable insights from large-scale UPI transaction data.

## Objective

Analyze a synthetic UPI transaction dataset (~75,000 records) to:
- Calculate key business KPIs (success rate, total value, average transaction)
- Identify high-performing cities, categories, and payment methods
- Understand time-based transaction patterns (hourly, daily, monthly)
- Investigate failure reasons and suggest improvements
- Build an interactive dashboard for stakeholder exploration

## Dataset

> ⚠️ **This dataset is entirely synthetic** — generated programmatically for portfolio/demonstration purposes. It does not represent any real individual's or company's transaction data.

**Size:** ~75,000 records | **Period:** January 2023 – June 2024

| Column | Description |
|---|---|
| transaction_id | Unique transaction identifier |
| transaction_date | Date of transaction (YYYY-MM-DD) |
| transaction_time | Time of transaction (HH:MM:SS) |
| transaction_amount | Amount in INR |
| transaction_type | Category (Food, Shopping, Travel, etc.) |
| payment_method | UPI QR / UPI ID / Mobile Number / UPI Lite / UPI |
| merchant_category | Same as transaction type |
| merchant_name | Merchant (e.g., Swiggy, Amazon, IRCTC) |
| customer_id | Anonymous customer identifier |
| customer_age | Customer age |
| customer_gender | Male / Female |
| city | Transaction city |
| state | Transaction state |
| device_type | Android / iOS |
| bank_name | Customer's bank |
| transaction_status | Success / Failed / Pending |
| failure_reason | Reason if failed (else N/A) |

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Data generation, cleaning, analysis |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| SQLite | Analytical database |
| SQL | Querying and KPI calculation |
| Matplotlib/Seaborn | EDA charts |
| Plotly | Interactive dashboard charts |
| Streamlit | Local interactive dashboard |

## Project Architecture

```
Raw CSV (upi_transactions_raw.csv)
    ↓ clean_data.py
Cleaned CSV (upi_transactions_clean.csv)
    ↓ load_database.py
SQLite Database (upi_transactions.db)
    ↓ SQL Queries + run_analysis.py
Charts (outputs/charts/) + KPIs
    ↓ dashboard/app.py
Streamlit Dashboard
```

## Data Cleaning

The raw dataset contains intentional data quality issues:

| Issue | Solution |
|---|---|
| Missing merchant_name | Filled with "Unknown Merchant" |
| Missing bank_name | Filled with "Unknown Bank" |
| Missing customer_age | Filled with median age |
| Missing device_type | Filled with mode |
| Duplicate transaction IDs | Removed duplicates, kept first occurrence |
| Negative/zero amounts | Removed as invalid |
| Amounts > ₹1,00,000 | Removed (exceeds UPI daily limit) |
| Inconsistent capitalization | Standardized to Title Case |
| Status typos (e.g., "success") | Corrected to "Success" |

**Derived columns created:** year, month, month_name, day, day_name, hour, week, quarter, is_weekend, transaction_success_flag, amount_bucket, year_month

## SQL Analysis

The SQL layer demonstrates:

- `SELECT`, `WHERE`, `GROUP BY`, `ORDER BY`, `HAVING`
- `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `DISTINCT`
- `CASE WHEN` for conditional aggregation and bucketing
- **CTEs** (Common Table Expressions) for month-over-month growth
- **Window functions** — `RANK() OVER`, `SUM() OVER` for running totals
- **Subqueries** for multi-step filtering

SQL files:
- `sql/basic_analysis.sql` — Dataset overview
- `sql/kpi_analysis.sql` — Status, category, payment, geo, time KPIs
- `sql/advanced_analysis.sql` — CTEs, window functions, subqueries

## Dashboard

The Streamlit dashboard (`dashboard/app.py`) has 6 sections:

1. **KPI Cards** — Total transactions, value, success rate, unique customers
2. **Overview** — Daily volume trend, status distribution, category analysis
3. **Customer Analysis** — Amount distribution, top customers, age group analysis
4. **Geographic Analysis** — Top cities by volume, value, and success rate
5. **Payment Analysis** — Method usage, value share, success rates
6. **Failure Analysis** — Failure reasons, category failure rates, hourly/daily patterns
7. **Key Insights** — 7 dynamically calculated observations (no hardcoded values)

**Sidebar filters:** Date Range, City, State, Transaction Type, Payment Method, Category, Status — all filters update every chart and KPI dynamically.

## Key Insights

*(Calculated from the generated dataset — values will reflect your actual generated data)*

Run the dashboard to see live insights. Typical findings include:

- UPI QR is the most used payment method (~35% of transactions)
- Shopping generates the highest total transaction value
- Evening hours (6–9 PM) see peak transaction activity
- Weekend transactions tend to have higher average values
- "Insufficient Balance" is the most common failure reason
- Mumbai, Delhi, and Bangalore lead in transaction volume
- Overall success rate is approximately 88%

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic dataset
python scripts/generate_data.py

# 3. Clean the dataset
python scripts/clean_data.py

# 4. Load into SQLite database
python scripts/load_database.py

# 5. Run EDA and generate charts
python scripts/run_analysis.py

# 6. Launch the dashboard
streamlit run dashboard/app.py
```

## Project Structure

```
upi-transaction-intelligence/
├── data/
│   ├── raw/
│   │   └── upi_transactions_raw.csv
│   └── processed/
│       └── upi_transactions_clean.csv
├── database/
│   └── upi_transactions.db
├── scripts/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── load_database.py
│   └── run_analysis.py
├── sql/
│   ├── schema.sql
│   ├── basic_analysis.sql
│   ├── kpi_analysis.sql
│   └── advanced_analysis.sql
├── dashboard/
│   └── app.py
├── outputs/
│   ├── charts/
│   └── reports/
├── requirements.txt
├── README.md
├── INTERVIEW_PREP.md
└── .gitignore
```

---
*Portfolio project by [Your Name] | Data Analyst | Synthetic dataset*
