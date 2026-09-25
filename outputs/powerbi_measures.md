# Power BI DAX Measures — UPI Transaction Intelligence

This file documents the DAX measures to recreate in Power BI after importing `upi_transactions_clean.csv`.

---

## How to Import

1. Open Power BI Desktop
2. **Get Data → Text/CSV**
3. Select: `data/processed/upi_transactions_clean.csv`
4. In Power Query, ensure:
   - `transaction_date` is set to **Date** type
   - `transaction_amount` is set to **Decimal Number**
   - `transaction_success_flag` is set to **Whole Number**
5. Close & Apply

---

## DAX Measures

### 1. Total Transactions
```dax
Total Transactions = COUNTROWS(upi_transactions_clean)
```
**What it does:** Counts every row in the table — one row = one transaction.

---

### 2. Total Transaction Value
```dax
Total Transaction Value =
CALCULATE(
    SUM(upi_transactions_clean[transaction_amount]),
    upi_transactions_clean[transaction_status] = "Success"
)
```
**What it does:** Sums the amount only for successful transactions.

---

### 3. Average Transaction Value
```dax
Avg Transaction Value =
CALCULATE(
    AVERAGEX(
        FILTER(upi_transactions_clean, upi_transactions_clean[transaction_status] = "Success"),
        upi_transactions_clean[transaction_amount]
    )
)
```
**What it does:** Average amount across successful transactions only.

---

### 4. Success Rate
```dax
Success Rate % =
DIVIDE(
    COUNTROWS(FILTER(upi_transactions_clean, upi_transactions_clean[transaction_status] = "Success")),
    COUNTROWS(upi_transactions_clean),
    0
) * 100
```
**What it does:** Divides successful count by total count and converts to percentage. `DIVIDE` safely handles division by zero.

---

### 5. Failure Rate
```dax
Failure Rate % =
DIVIDE(
    COUNTROWS(FILTER(upi_transactions_clean, upi_transactions_clean[transaction_status] = "Failed")),
    COUNTROWS(upi_transactions_clean),
    0
) * 100
```
**What it does:** Same as success rate but for failed transactions.

---

### 6. Unique Customers
```dax
Unique Customers = DISTINCTCOUNT(upi_transactions_clean[customer_id])
```
**What it does:** Counts how many distinct customers appear in the filtered data.

---

### 7. Unique Merchants
```dax
Unique Merchants = DISTINCTCOUNT(upi_transactions_clean[merchant_name])
```
**What it does:** Counts distinct merchant names.

---

### 8. Monthly Growth %
```dax
Monthly Growth % =
VAR CurrentMonth = SUM(upi_transactions_clean[transaction_amount])
VAR PreviousMonth =
    CALCULATE(
        SUM(upi_transactions_clean[transaction_amount]),
        DATEADD(upi_transactions_clean[transaction_date], -1, MONTH)
    )
RETURN
    DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth, 0) * 100
```
**What it does:** Compares this month's total value to the previous month using `DATEADD` for date arithmetic.

---

### 9. Peak Transaction Hour
```dax
Peak Hour =
TOPN(
    1,
    SUMMARIZE(
        upi_transactions_clean,
        upi_transactions_clean[hour],
        "txn_count", COUNTROWS(upi_transactions_clean)
    ),
    [txn_count],
    DESC
)[hour]
```
**What it does:** Finds the hour with the highest transaction count.

---

### 10. Average Daily Transactions
```dax
Avg Daily Transactions =
DIVIDE(
    COUNTROWS(upi_transactions_clean),
    DISTINCTCOUNT(upi_transactions_clean[transaction_date]),
    0
)
```
**What it does:** Total transactions divided by number of distinct dates.

---

## Suggested Visuals in Power BI

| Visual | Fields |
|---|---|
| Card | Total Transactions, Total Value, Success Rate %, Unique Customers |
| Line Chart | transaction_date → txn count (Daily Trend) |
| Bar Chart | merchant_category → Total Transaction Value |
| Donut Chart | transaction_status → Count |
| Stacked Bar | payment_method → Count by Status |
| Map | city → transaction count (if Bing Maps enabled) |
| Matrix | city vs merchant_category → SUM amount |
| Slicer | transaction_date, city, payment_method, merchant_category, status |

---

*Connect Power BI to `data/processed/upi_transactions_clean.csv` for full compatibility.*
