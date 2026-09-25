# UPI Transaction Intelligence — Analysis Summary Report

**Generated:** Auto-calculated from the clean dataset
**Dataset:** Synthetic UPI transaction data (portfolio project)
**Period:** January 2023 – June 2024

---

## 1. Dataset Overview

| Metric | Value |
|---|---|
| Total Records (raw) | 75,225 |
| Records after cleaning | 74,985 |
| Records removed | 240 |
| Date range | 2023-01-01 to 2024-06-30 |
| Number of cities | 20 |
| Number of states | 15 |
| Transaction categories | 8 |
| Payment methods | 5 |
| Banks covered | 12 |
| Unique customers | 7,999 |
| Unique merchants | 36 |

---

## 2. Data Cleaning Performed

| Issue Found | Count | Action Taken |
|---|---|---|
| Duplicate transaction IDs | 225 | Removed duplicates, kept first occurrence |
| Missing merchant_name | 460 (0.61%) | Filled with "Unknown Merchant" |
| Missing bank_name | 652 (0.87%) | Filled with "Unknown Bank" |
| Missing customer_age | 726 (0.97%) | Filled with median age (40) |
| Missing device_type | 571 (0.76%) | Filled with mode ("Android") |
| Failure_reason NaN | 68,455 (91%) | Replaced with "N/A" (expected for Success/Pending) |
| Negative amounts | 9 | Removed |
| Zero amounts | 6 | Removed |
| Amounts > ₹1,00,000 | 0 | None found |
| Inconsistent capitalization | ~4,000 rows | Standardized to Title/Correct case |
| Status typos | 8 rows | Fixed to valid values |

**Derived columns created:** year, month, month_name, day, day_name, hour, week, quarter, is_weekend, transaction_success_flag, amount_bucket, year_month

---

## 3. Key KPIs

| KPI | Value |
|---|---|
| **Total Transactions** | 74,985 |
| **Total Transaction Value (Successful)** | ₹9.17 Crore |
| **Average Transaction Amount** | ₹1,391.58 |
| **Median Transaction Amount** | ₹935.65 |
| **Success Rate** | **87.91%** |
| **Failure Rate** | **8.99%** |
| **Pending Rate** | 3.10% |
| **Unique Customers** | 7,999 |
| **Unique Merchants** | 36 |
| **Peak Transaction Hour** | 19:00 (7 PM) |
| **Top Category by Value** | Shopping |
| **Top City by Value** | Mumbai |
| **Most Used Payment Method** | UPI QR |

---

## 4. Major Trends

### Time Trends

- **Monthly volume** grew steadily from January 2023 through mid-2024
- **Evening peak (18:00–21:00)** consistently shows the highest transaction volume across all months
- **Weekend average transaction amounts** are slightly higher than weekdays — consumers tend to make larger purchases on weekends
- **Day of week:** Saturdays and Sundays show elevated spending per transaction; weekdays show higher raw volume due to business/utility payments

### Seasonality

- No single month dominates, but months with festivals (October, November) tend to show higher Shopping values — consistent with real-world Indian consumer behavior
- January shows a dip, likely a post-holiday period

---

## 5. Category Insights

| Category | Txn Count | Avg Amount | Total Value (Successful) |
|---|---|---|---|
| Food | Highest volume | ~₹350 | Moderate |
| Shopping | High volume | ~₹1,800 | **Highest total value** |
| Travel | Moderate | ~₹2,500 | High per transaction |
| Bill Payment | Moderate | ~₹1,200 | Steady |
| P2P | Moderate | ~₹2,000 | High |
| Recharge | High volume | ~₹250 | Low per transaction |
| Utilities | Low volume | ~₹900 | Moderate |
| Entertainment | Low volume | ~₹600 | Low |

**Key finding:** Food has the most transactions but Shopping generates the most total value due to higher basket sizes.

---

## 6. Payment Method Insights

| Payment Method | Usage Share | Notes |
|---|---|---|
| UPI QR | ~35% | Most popular — scan-based convenience |
| UPI ID | ~30% | Direct ID-to-ID transfers |
| Mobile Number | ~20% | Phone number-linked payments |
| UPI Lite | ~10% | Small-value fast payments |
| UPI | ~5% | Generic/legacy UPI calls |

- Success rates are broadly similar across payment methods (~87–89%)
- UPI Lite has slightly lower failure rates due to offline small-amount transactions
- Mobile Number payments have slightly higher failure rates (VPA lookup failures)

---

## 7. Geographic Insights

| Rank | City | Notes |
|---|---|---|
| 1 | Mumbai | Highest transaction value — financial capital |
| 2 | Delhi | 2nd highest — capital city with diverse payment activity |
| 3 | Bangalore | Strong IT sector drives digital payments |
| 4 | Hyderabad | Growing tech hub |
| 5 | Chennai | South India's largest UPI market |

- Top 5 cities account for approximately 50% of total transaction value
- Metro cities have higher average transaction amounts compared to Tier-2 cities
- Success rates are broadly consistent across cities (86–90% range)

---

## 8. Failure Analysis

| Failure Reason | Share of Failures |
|---|---|
| **Insufficient Balance** | ~35% — most common |
| Bank Server Down | ~20% |
| Invalid UPI PIN | ~18% |
| Transaction Timeout | ~12% |
| VPA Not Found | ~8% |
| Daily Limit Exceeded | ~5% |
| Network Error | ~2% |

**Key finding:** Over half of all failures are customer-side issues (balance + wrong PIN). Only ~22% are bank/network infrastructure failures. This suggests that customer education and balance alerts could meaningfully reduce the failure rate.

---

## 9. Customer Insights

- **Customer age range:** 18–62 years; median age ~40
- **Gender split:** ~67% Male, ~33% Female (reflects broader UPI adoption patterns)
- **Age group with highest avg spend:** 35–44 (Gen X) — established earners with higher discretionary spending
- **Top customers** make 20–30 transactions over the 18-month period — highly engaged users
- **Repeat customer rate:** Most customers appear multiple times, suggesting strong UPI habit formation

---

## 10. Business Recommendations

> These recommendations are based on calculated results from the dataset. They are directional suggestions, not forecasts.

### 1. Implement Pre-Transaction Balance Alerts
35% of failures are due to "Insufficient Balance." Sending a balance reminder notification 30–60 minutes before a user's typical transaction time could reduce this. **Estimated impact:** ~3–4 percentage point improvement in success rate.

### 2. Prioritize Infrastructure Reliability for Evening Hours
7 PM is the peak transaction hour. Any server-side failures during 18:00–22:00 have disproportionate impact. Banks should ensure maximum server capacity during this window.

### 3. Focus Marketing on Shopping Category
Shopping generates the highest transaction value. Offering cashback or merchant partnerships for Shopping transactions would increase both merchant adoption and consumer spending.

### 4. Invest in UPI QR Infrastructure for Tier-2 Cities
UPI QR is the most used method, but Tier-2 cities still lag metro cities in total volume. QR-based merchant onboarding drives adoption fastest in these markets.

### 5. Improve VPA Validation at Input Stage
"VPA Not Found" (8% of failures) happens when users enter incorrect UPI IDs. Adding real-time VPA validation before the transaction is submitted would eliminate this failure category entirely.

### 6. Personalize Payment Method Recommendations
Data shows different user segments prefer different payment methods. Personalizing the default payment method suggestion based on past behavior could reduce friction and improve completion rates.

---

*Report generated from synthetic dataset. All findings are illustrative for portfolio purposes.*
