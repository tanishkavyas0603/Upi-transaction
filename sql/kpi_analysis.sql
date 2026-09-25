-- kpi_analysis.sql
-- Business KPI queries: status, category, payment, geographic, and time analysis.
-- Concepts: GROUP BY, ORDER BY, HAVING, CASE WHEN, aggregate functions

-- ==============================================================
-- STATUS ANALYSIS
-- ==============================================================

-- 10. Successful transactions count
SELECT COUNT(*) AS successful_transactions
FROM upi_transactions
WHERE transaction_status = 'Success';

-- 11. Failed transactions count
SELECT COUNT(*) AS failed_transactions
FROM upi_transactions
WHERE transaction_status = 'Failed';

-- 12. Pending transactions count
SELECT COUNT(*) AS pending_transactions
FROM upi_transactions
WHERE transaction_status = 'Pending';

-- 13. Success rate (%)
-- AVG of success_flag gives proportion, multiply by 100 for percentage
SELECT ROUND(AVG(transaction_success_flag) * 100.0, 2) AS success_rate_pct
FROM upi_transactions;

-- 14. Failure rate (%)
SELECT ROUND(
    SUM(CASE WHEN transaction_status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    2
) AS failure_rate_pct
FROM upi_transactions;

-- ==============================================================
-- CATEGORY ANALYSIS
-- ==============================================================

-- 15. Transaction count by category (highest first)
SELECT merchant_category,
       COUNT(*) AS txn_count
FROM upi_transactions
GROUP BY merchant_category
ORDER BY txn_count DESC;

-- 16. Transaction value by category (successful only)
SELECT merchant_category,
       ROUND(SUM(transaction_amount), 2)         AS total_value,
       ROUND(AVG(transaction_amount), 2)         AS avg_amount,
       COUNT(*)                                  AS txn_count
FROM upi_transactions
WHERE transaction_status = 'Success'
GROUP BY merchant_category
ORDER BY total_value DESC;

-- 17. Categories with more than 5,000 successful transactions (HAVING filters after GROUP BY)
SELECT merchant_category,
       COUNT(*) AS success_count
FROM upi_transactions
WHERE transaction_status = 'Success'
GROUP BY merchant_category
HAVING COUNT(*) > 5000
ORDER BY success_count DESC;

-- ==============================================================
-- PAYMENT METHOD ANALYSIS
-- ==============================================================

-- 18. Transaction count by payment method
SELECT payment_method,
       COUNT(*) AS txn_count
FROM upi_transactions
GROUP BY payment_method
ORDER BY txn_count DESC;

-- 19. Transaction value by payment method
SELECT payment_method,
       ROUND(SUM(transaction_amount) / 1000000.0, 2) AS total_value_mn
FROM upi_transactions
WHERE transaction_status = 'Success'
GROUP BY payment_method
ORDER BY total_value_mn DESC;

-- 20. Success rate by payment method
-- CASE WHEN creates a conditional column; AVG of 0/1 gives the rate
SELECT payment_method,
       COUNT(*) AS total_txns,
       SUM(CASE WHEN transaction_status = 'Success' THEN 1 ELSE 0 END) AS success_count,
       ROUND(
           SUM(CASE WHEN transaction_status = 'Success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
           2
       ) AS success_rate_pct
FROM upi_transactions
GROUP BY payment_method
ORDER BY success_rate_pct DESC;

-- ==============================================================
-- GEOGRAPHIC ANALYSIS
-- ==============================================================

-- 21. Transaction count by city (top 15)
SELECT city, state,
       COUNT(*) AS txn_count
FROM upi_transactions
GROUP BY city, state
ORDER BY txn_count DESC
LIMIT 15;

-- 22. Transaction value by city (top 15)
SELECT city,
       ROUND(SUM(transaction_amount) / 1000000.0, 2) AS total_value_mn
FROM upi_transactions
WHERE transaction_status = 'Success'
GROUP BY city
ORDER BY total_value_mn DESC
LIMIT 15;

-- 23. Success rate by city
SELECT city,
       COUNT(*) AS total_txns,
       ROUND(AVG(transaction_success_flag) * 100.0, 2) AS success_rate_pct
FROM upi_transactions
GROUP BY city
ORDER BY success_rate_pct DESC;

-- ==============================================================
-- TIME ANALYSIS
-- ==============================================================

-- 24. Daily transaction volume
SELECT transaction_date,
       COUNT(*) AS txn_count,
       ROUND(SUM(transaction_amount), 2) AS daily_value
FROM upi_transactions
WHERE transaction_status = 'Success'
GROUP BY transaction_date
ORDER BY transaction_date;

-- 25. Monthly transaction volume and value
SELECT year_month,
       COUNT(*) AS txn_count,
       ROUND(SUM(transaction_amount) / 1000000.0, 2) AS value_mn
FROM upi_transactions
WHERE transaction_status = 'Success'
GROUP BY year_month
ORDER BY year_month;

-- 26. Transactions by hour
SELECT hour,
       COUNT(*) AS txn_count,
       ROUND(AVG(transaction_amount), 2) AS avg_amount
FROM upi_transactions
GROUP BY hour
ORDER BY hour;

-- 27. Transactions by day of week
SELECT day_name,
       COUNT(*) AS txn_count,
       ROUND(AVG(transaction_amount), 2) AS avg_amount
FROM upi_transactions
GROUP BY day_name
ORDER BY txn_count DESC;

-- 28. Weekend vs weekday comparison
-- CASE WHEN classifies each row as Weekend or Weekday
SELECT
    CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(*) AS txn_count,
    ROUND(AVG(transaction_amount), 2) AS avg_amount,
    ROUND(SUM(transaction_amount) / 1000000.0, 2) AS total_value_mn
FROM upi_transactions
GROUP BY is_weekend;
