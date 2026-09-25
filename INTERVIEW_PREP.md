# INTERVIEW PREP — UPI Transaction Intelligence Dashboard

A complete guide to confidently explaining this project in a Data Analyst interview.

---

## 1. 30-Second Project Explanation

> "I built an end-to-end data analytics project on UPI payment transactions. I generated a realistic synthetic dataset of 75,000 transactions, cleaned it with Python and Pandas, loaded it into a SQLite database, wrote SQL queries to answer business questions like success rates, top cities, and failure reasons, and built an interactive Streamlit dashboard with dynamic filters and KPI cards. The project covers the full analyst workflow: data cleaning, SQL analysis, EDA, KPI design, and dashboarding."

---

## 2. Problem Statement

UPI (Unified Payments Interface) processes over 10 billion transactions a month in India. Banks and fintech companies need to answer questions like:
- Which payment methods fail most often?
- Which cities generate the most revenue?
- What are peak transaction hours?
- Why are transactions failing?

This project simulates a data analyst solving these questions from raw transaction data.

---

## 3. Why I Chose This Project

- UPI is highly relevant in today's Indian fintech landscape
- It covers real-world analyst skills: cleaning messy data, writing SQL queries, building KPIs, and making dashboards
- The dataset has realistic business context (categories, cities, banks, failure reasons)
- It demonstrates the complete DA workflow end-to-end
- I can explain every part of it — no black-box algorithms

---

## 4. Dataset Explanation

The dataset is **synthetic** — I generated it using Python's `random` and `numpy` libraries with controlled statistical properties:
- ~75,000 transaction records over 18 months (Jan 2023 – Jun 2024)
- 20 cities, 8 transaction categories, 5 payment methods, 12 banks
- Success/Fail/Pending ratios: ~88% / ~9% / ~3% (realistic for UPI)
- Transaction amounts vary by category (Food ~₹350, Travel ~₹2,500)
- Volume peaks during evening hours (6–9 PM) and weekends

I also injected **controlled data quality issues** to demonstrate cleaning:
- Duplicate transaction IDs (~0.3%)
- Missing values in non-critical columns (~0.5–1.2%)
- Inconsistent capitalization in category columns
- A few invalid/negative transaction amounts
- Status field typos (e.g., "success" instead of "Success")

---

## 5. Data Cleaning Explanation

I wrote a step-by-step cleaning pipeline in `clean_data.py` using Pandas:

| Step | Action | Reason |
|---|---|---|
| 1 | Load + inspect shape & types | Understand the data before touching it |
| 2 | Identify missing values | Know what needs fixing |
| 3 | Fill missing merchant_name | "Unknown Merchant" — better than dropping rows |
| 4 | Fill missing bank_name | "Unknown Bank" |
| 5 | Fill missing customer_age | Used median — robust to outliers |
| 6 | Fill missing device_type | Used mode (most common value) |
| 7 | Fill failure_reason NaN | "N/A" — expected for Success/Pending rows |
| 8 | Remove duplicate transaction_ids | Kept first occurrence — duplicates distort aggregates |
| 9 | Remove negative/zero amounts | Invalid business data |
| 10 | Remove amounts > ₹1,00,000 | Exceeds UPI daily limit — data error |
| 11 | Standardize to Title Case | Fixes "FOOD", "food", "Food" → "Food" |
| 12 | Convert dates to datetime | Enables proper date filtering and grouping |
| 13 | Create derived columns | year, month, hour, is_weekend, amount_bucket etc. |

---

## 6. SQL Explanation

I wrote SQL queries covering three levels:

**Basic** (`basic_analysis.sql`):
- Total transactions, total value, averages, min/max using `COUNT`, `SUM`, `AVG`

**KPI Analysis** (`kpi_analysis.sql`):
- Status distribution (`GROUP BY transaction_status`)
- Category analysis (`GROUP BY merchant_category ORDER BY total_value DESC`)
- Success rate using `CASE WHEN` and `AVG`
- Time analysis by month, hour, day

**Advanced** (`advanced_analysis.sql`):
- Month-over-month growth using a **CTE** (Common Table Expression)
- City ranking using `RANK() OVER (ORDER BY ...)`
- Running cumulative totals using `SUM() OVER (ORDER BY date)`
- High-value customer filtering using a **subquery**
- Age group bucketing using `CASE WHEN`

---

## 7. Power BI Explanation

I prepared the project for Power BI by:
1. Exporting the clean data as CSV (Power BI can directly import CSV)
2. Creating a `powerbi_measures.md` file with DAX formulas for each KPI
3. Keeping column names clean (no spaces, consistent casing)
4. Including derived columns (year_month, is_weekend) that reduce DAX complexity

Key Power BI KPIs include:
- Total Transactions (`COUNTROWS`)
- Success Rate (`DIVIDE(COUNTROWS(filtered), COUNTROWS(all))`)
- Monthly Growth (`DATEADD` for previous month comparison)

---

## 8. Five Important Insights

*(These are based on typical results from the generated dataset)*

1. **UPI QR is the dominant payment method** — ~35% of all transactions use QR code scanning
2. **Shopping generates the highest transaction value** — large basket sizes drive overall revenue
3. **Evening peak (18:00–21:00) accounts for the highest hourly volume** — infrastructure should scale for this window
4. **Insufficient Balance is the #1 failure reason** — customer education on balance management could reduce failure rate
5. **Mumbai, Delhi, and Bangalore account for ~30% of total transaction value** — metro cities dominate UPI adoption

---

## 9. Technical Challenges

1. **Generating realistic data** — making amounts follow category-specific distributions required lognormal sampling, not just random ranges
2. **Date-based trends** — had to weight hours and weekends separately to mimic real UPI usage patterns
3. **Pandas performance** — with 75K rows, operations like `apply()` on large columns can be slow; used vectorized operations where possible
4. **Streamlit filter state** — ensuring all 6 sections update correctly when multiple filters are combined required careful pandas filtering logic
5. **SQLite window functions** — not all SQLite versions support `RANK() OVER`; confirmed compatibility with SQLite ≥ 3.25

---

## 10. Why SQLite Was Used

- **No setup required** — SQLite is a file-based database. No server, no installation, no configuration.
- **Portable** — the entire database is a single `.db` file that can be shared
- **Sufficient for this scale** — 75,000 rows is easily handled by SQLite
- **Python integration** — Python's built-in `sqlite3` module works without any extra packages
- **Interview-friendly** — demonstrates SQL skills without DevOps complexity
- **Power BI compatible** — Power BI can connect to SQLite via ODBC drivers

In production, I'd use PostgreSQL for multi-user access, or BigQuery for very large datasets.

---

## 11. Why Pandas Was Used

- **Industry standard** for tabular data manipulation in Python
- **Readable syntax** — `df.groupby().agg()` reads like plain English
- **Fast enough** for this scale — 75K rows processes in seconds
- **Integration** — works seamlessly with SQLite (via `df.to_sql()`), Matplotlib, Plotly, and Streamlit
- **Rich functionality** — handles missing values, type conversions, groupby, merges in a few lines

---

## 12. Why Power BI Was Used

- **Industry standard** in India for business dashboards — most DA job descriptions mention Power BI
- **DAX formulas** enable dynamic KPIs without writing Python for every metric
- **Zero code UI** — business users can explore data without technical help
- **Direct CSV import** — no database driver needed for basic use
- **Professional output** — reports can be shared as PDFs or published to Power BI Service

---

## 13. 20 Likely Interviewer Questions

---

### Q1. Tell me about your project in 2 minutes.

**Answer:** I built a UPI Transaction Intelligence Dashboard — an end-to-end analytics project. I started by generating a realistic synthetic dataset of 75,000 UPI transactions with fields like amount, category, city, payment method, and status. Then I cleaned the data using Python and Pandas — handling missing values, removing duplicates, fixing capitalization issues, and validating amounts. I loaded the clean data into a SQLite database and wrote SQL queries to answer business questions like success rates, top cities, and failure analysis. I also created 10 EDA charts using Matplotlib and Seaborn, and built an interactive Streamlit dashboard with live filters and dynamic KPI cards.

---

### Q2. How did you clean the data?

**Answer:** I wrote a step-by-step pipeline in `clean_data.py`. First I inspected the shape and data types. Then I identified missing values — some columns like merchant_name had ~1% missing values which I filled with "Unknown Merchant" rather than dropping rows. I removed ~225 duplicate transaction IDs, keeping the first occurrence. I validated amounts — removed negative values, zeros, and amounts above ₹1 lakh (the UPI limit). I standardized all category columns to Title Case to fix inconsistent capitalization. Finally I created derived columns like hour, month, is_weekend, and amount_bucket for analysis.

---

### Q3. How did you handle missing values?

**Answer:** It depends on the column and business context. For merchant_name and bank_name, I filled with "Unknown" because dropping those rows would lose valid transaction data. For customer_age, I used the median age rather than the mean — median is more robust to age outliers. For device_type, I used the mode (most frequent value). For failure_reason, NaN values are actually expected and correct for Successful transactions, so I replaced them with "N/A" to make it explicit.

---

### Q4. How did you remove duplicates?

**Answer:** I used Pandas `drop_duplicates(subset=["transaction_id"], keep="first")`. This keeps only the first occurrence of each transaction ID and removes any later duplicates. I found about 225 duplicate rows (~0.3%) which were intentionally injected into the raw dataset to demonstrate cleaning.

---

### Q5. What SQL queries did you use?

**Answer:** I wrote queries across three files. Basic queries used `SELECT`, `COUNT`, `SUM`, `AVG`, `WHERE`, and `GROUP BY`. KPI queries used `CASE WHEN` to calculate success rates and `GROUP BY ... ORDER BY` for category and payment analysis. Advanced queries demonstrated CTEs for month-over-month growth, window functions like `RANK() OVER` for city ranking, and subqueries for high-value customer filtering.

---

### Q6. Why did you use GROUP BY?

**Answer:** `GROUP BY` collapses multiple rows with the same value into one summary row so I can apply aggregate functions. For example: `SELECT merchant_category, COUNT(*) FROM upi_transactions GROUP BY merchant_category` gives one row per category with its transaction count. Without `GROUP BY`, `COUNT(*)` would return a single total count.

---

### Q7. What is the difference between WHERE and HAVING?

**Answer:** `WHERE` filters individual rows **before** grouping. `HAVING` filters groups **after** `GROUP BY` has been applied. For example: `WHERE transaction_status = 'Success'` removes failed rows before any aggregation. `HAVING COUNT(*) > 5000` removes categories with fewer than 5,000 transactions after grouping. You cannot use aggregate functions in `WHERE`, but you can in `HAVING`.

---

### Q8. What is a JOIN? Did you use it?

**Answer:** A JOIN combines rows from two or more tables based on a related column. I used a self-join in the CTE query to calculate month-over-month growth — I joined the monthly_totals CTE with itself, matching each month with the previous month. In a real project, JOINs would connect transactions to a separate customer table or merchant table.

---

### Q9. What is a window function?

**Answer:** A window function performs a calculation across a set of rows related to the current row, without collapsing them into groups the way `GROUP BY` does. I used `RANK() OVER (ORDER BY SUM(transaction_amount) DESC)` to rank cities by transaction value. I also used `SUM(COUNT(*)) OVER (ORDER BY transaction_date)` to create a cumulative running total of daily transactions.

---

### Q10. How did you calculate success rate?

**Answer:** Two ways. In SQL: `AVG(transaction_success_flag) * 100` — since the flag is 1 for Success and 0 otherwise, the average gives the proportion, multiplied by 100 for percentage. Alternatively: `SUM(CASE WHEN transaction_status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)`. In Python: `len(df[df['transaction_status']=='Success']) / len(df) * 100`.

---

### Q11. Why did you use Pandas?

**Answer:** Pandas is the standard Python library for tabular data. It lets me load CSV files with one line (`pd.read_csv()`), inspect data with `.info()` and `.describe()`, filter rows with boolean masks, fill missing values with `.fillna()`, and create new columns with vectorized operations. It integrates directly with SQLite via `df.to_sql()` and with Matplotlib for charts.

---

### Q12. What insights did you find?

**Answer:** The main findings were: (1) UPI QR is the most used payment method; (2) Shopping generates the highest transaction value; (3) Evening hours (6–9 PM) are the peak transaction window; (4) Insufficient Balance is the top failure reason; (5) Metro cities — Mumbai, Delhi, Bangalore — lead in total transaction volume. The overall success rate was approximately 88%.

---

### Q13. How did you design the dashboard?

**Answer:** I built it in Streamlit. The layout has a sidebar with 7 filters (date range, city, state, type, payment method, category, status) and a main area with 6 sections: KPI cards at the top, then Overview, Customer Analysis, Geographic Analysis, Payment Analysis, Failure Analysis, and Key Insights. All charts and KPIs are calculated from the filtered dataset dynamically — nothing is hardcoded. I used Plotly for interactive charts because it integrates smoothly with Streamlit.

---

### Q14. What KPIs did you choose?

**Answer:** I chose KPIs that directly answer business questions: Total Transactions (volume), Total Transaction Value (revenue), Average Transaction Value (spending behavior), Success Rate (reliability), Failure Rate (quality issue indicator), Unique Customers (reach), Unique Merchants (ecosystem size), Peak Transaction Hour (operational planning), and Monthly Growth % (trend).

---

### Q15. What was the biggest challenge?

**Answer:** Making the synthetic data feel realistic was harder than expected. Real UPI data has patterns — amounts vary by category, volumes peak at certain hours, weekends behave differently. I had to carefully design the generation logic: using lognormal distributions for amounts, weighting hours by typical usage patterns, and giving cities different transaction volumes proportional to their real economic size.

---

### Q16. How would you improve this if you had real data?

**Answer:** With real data I'd add: (1) Proper customer segmentation using RFM analysis (Recency, Frequency, Monetary); (2) Anomaly detection to flag unusual transaction spikes; (3) Cohort analysis to track retention of new UPI users over time; (4) A proper star schema in the database with separate dimension tables for customers, merchants, and cities; (5) Automated daily data refresh pipeline.

---

### Q17. What is the difference between a CTE and a subquery?

**Answer:** Both let you write a temporary result set inside a query. A subquery is nested inside the main query, which can make long queries hard to read. A CTE (Common Table Expression) uses the `WITH` keyword to define a named temporary table before the main query, making it much more readable and reusable within the same query. CTEs are especially useful when you need to reference the same result set multiple times.

---

### Q18. Why did you choose SQLite over PostgreSQL?

**Answer:** For a local portfolio project with 75,000 rows, SQLite is perfect — no server setup, no configuration, just a single file. PostgreSQL would be the right choice in production: it handles concurrent users, much larger datasets, more advanced SQL features, and better security. But for demonstrating SQL skills in an interview context, SQLite achieves the same result with zero friction.

---

### Q19. What is a lognormal distribution and why did you use it?

**Answer:** A lognormal distribution is a distribution where the logarithm of the values follows a normal distribution. Transaction amounts are naturally lognormal — most transactions are small (₹50–₹500), but a few are very large (₹50,000+). Using `np.random.lognormal(mean=np.log(category_avg), sigma=0.6)` generates amounts clustered around each category's typical value with a realistic right skew, instead of a symmetric normal distribution which would generate too many unrealistically high or negative values.

---

### Q20. How would you present this project to a non-technical manager?

**Answer:** "I analyzed 75,000 digital payment transactions to help the team understand how customers are paying and where we're losing transactions. The dashboard shows that our payment success rate is 88%, evening hours are our busiest time, Shopping is our top revenue-generating category, and 'Insufficient Balance' accounts for 35% of failed payments. If we send balance reminders to customers before their typical transaction time, we could potentially reduce failures and improve that success rate."

---

*Good luck in your interview! Practice explaining each concept in simple language before the day.*
