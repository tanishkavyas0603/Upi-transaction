-- basic_analysis.sql
-- Fundamental queries covering dataset overview and basic statistics.
-- Concepts: SELECT, COUNT, SUM, AVG, MIN, MAX, DISTINCT, WHERE

-- 1. Total number of transactions
SELECT COUNT(*) AS total_transactions
FROM upi_transactions;

-- 2. Total transaction value (successful transactions only)
SELECT ROUND(SUM(transaction_amount), 2) AS total_value_inr
FROM upi_transactions
WHERE transaction_status = 'Success';

-- 3. Average transaction amount (successful only)
SELECT ROUND(AVG(transaction_amount), 2) AS avg_transaction_amount
FROM upi_transactions
WHERE transaction_status = 'Success';

-- 4. Minimum transaction amount
SELECT MIN(transaction_amount) AS min_amount
FROM upi_transactions;

-- 5. Maximum transaction amount
SELECT MAX(transaction_amount) AS max_amount
FROM upi_transactions;

-- 6. Number of unique customers
SELECT COUNT(DISTINCT customer_id) AS unique_customers
FROM upi_transactions;

-- 7. Number of unique merchants
SELECT COUNT(DISTINCT merchant_name) AS unique_merchants
FROM upi_transactions;

-- 8. Transaction count by status
-- GROUP BY groups rows with the same status, COUNT(*) counts each group
SELECT transaction_status,
       COUNT(*) AS txn_count
FROM upi_transactions
GROUP BY transaction_status
ORDER BY txn_count DESC;

-- 9. Quick dataset overview — all stats in one query
SELECT
    COUNT(*)                                          AS total_records,
    COUNT(DISTINCT customer_id)                       AS unique_customers,
    COUNT(DISTINCT merchant_name)                     AS unique_merchants,
    ROUND(MIN(transaction_amount), 2)                 AS min_amount,
    ROUND(MAX(transaction_amount), 2)                 AS max_amount,
    ROUND(AVG(transaction_amount), 2)                 AS avg_amount,
    ROUND(SUM(transaction_amount) / 1000000.0, 2)    AS total_value_millions,
    MIN(transaction_date)                             AS start_date,
    MAX(transaction_date)                             AS end_date
FROM upi_transactions;
