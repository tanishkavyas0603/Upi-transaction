-- advanced_analysis.sql
-- Advanced SQL queries using CTEs, subqueries, window functions, and JOINs.
-- Every non-trivial query includes a comment explaining what it does.

-- ==============================================================
-- FAILURE ANALYSIS
-- ==============================================================

-- 29. Most common failure reasons
SELECT failure_reason,
       COUNT(*) AS fail_count,
       ROUND(COUNT(*) * 100.0 / (
           SELECT COUNT(*) FROM upi_transactions WHERE transaction_status = 'Failed'
       ), 2) AS pct_of_failures
FROM upi_transactions
WHERE transaction_status = 'Failed'
  AND failure_reason != 'N/A'
GROUP BY failure_reason
ORDER BY fail_count DESC;

-- 30. Failure rate by category
-- Shows which transaction categories have the highest failure rate
SELECT merchant_category,
       COUNT(*) AS total_txns,
       SUM(CASE WHEN transaction_status = 'Failed' THEN 1 ELSE 0 END) AS fail_count,
       ROUND(
           SUM(CASE WHEN transaction_status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
           2
       ) AS failure_rate_pct
FROM upi_transactions
GROUP BY merchant_category
ORDER BY failure_rate_pct DESC;

-- 31. Failure rate by payment method
SELECT payment_method,
       COUNT(*) AS total_txns,
       SUM(CASE WHEN transaction_status = 'Failed' THEN 1 ELSE 0 END) AS fail_count,
       ROUND(
           SUM(CASE WHEN transaction_status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
           2
       ) AS failure_rate_pct
FROM upi_transactions
GROUP BY payment_method
ORDER BY failure_rate_pct DESC;

-- 32. Failure rate by city
SELECT city,
       COUNT(*) AS total_txns,
       ROUND(
           SUM(CASE WHEN transaction_status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
           2
       ) AS failure_rate_pct
FROM upi_transactions
GROUP BY city
ORDER BY failure_rate_pct DESC;

-- ==============================================================
-- CUSTOMER ANALYSIS
-- ==============================================================

-- 33. Top 10 customers by total transaction value
SELECT customer_id,
       COUNT(*) AS txn_count,
       ROUND(SUM(transaction_amount), 2) AS total_spent
FROM upi_transactions
WHERE transaction_status = 'Success'
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 10;

-- 34. Top 10 customers by transaction count
SELECT customer_id,
       COUNT(*) AS txn_count,
       ROUND(AVG(transaction_amount), 2) AS avg_amount
FROM upi_transactions
GROUP BY customer_id
ORDER BY txn_count DESC
LIMIT 10;

-- 35. Average transaction value by customer age group
-- CASE WHEN used to create age buckets on the fly
SELECT
    CASE
        WHEN customer_age < 25 THEN '18-24 (Gen Z)'
        WHEN customer_age < 35 THEN '25-34 (Millennial)'
        WHEN customer_age < 45 THEN '35-44 (Gen X Junior)'
        WHEN customer_age < 55 THEN '45-54 (Gen X Senior)'
        ELSE '55+ (Boomer)'
    END AS age_group,
    COUNT(*) AS txn_count,
    ROUND(AVG(transaction_amount), 2) AS avg_amount,
    ROUND(SUM(transaction_amount) / 1000000.0, 2) AS total_value_mn
FROM upi_transactions
WHERE transaction_status = 'Success'
GROUP BY age_group
ORDER BY total_value_mn DESC;

-- ==============================================================
-- CTE EXAMPLES
-- Common Table Expressions (CTEs) make complex queries readable
-- ==============================================================

-- 36. Month-over-month growth rate using a CTE
-- Step 1: Calculate monthly totals → Step 2: Join current and previous month
WITH monthly_totals AS (
    SELECT year_month,
           COUNT(*) AS txn_count,
           SUM(transaction_amount) AS total_value
    FROM upi_transactions
    WHERE transaction_status = 'Success'
    GROUP BY year_month
),
growth AS (
    -- Self-join to get the previous month's values alongside current month
    SELECT
        curr.year_month,
        curr.txn_count,
        prev.txn_count AS prev_txn_count,
        ROUND(
            (curr.txn_count - prev.txn_count) * 100.0 / prev.txn_count,
            2
        ) AS mom_growth_pct
    FROM monthly_totals curr
    LEFT JOIN monthly_totals prev
        ON curr.rowid = prev.rowid + 1  -- simplified ordering by rowid
)
SELECT * FROM growth ORDER BY year_month;


-- 37. Rank cities by transaction value using a window function
-- RANK() assigns a rank to each city within the overall result set
-- Window functions operate across a set of rows related to the current row
SELECT
    city,
    ROUND(SUM(transaction_amount) / 1000000.0, 2) AS total_value_mn,
    RANK() OVER (ORDER BY SUM(transaction_amount) DESC) AS city_rank
FROM upi_transactions
WHERE transaction_status = 'Success'
GROUP BY city
ORDER BY city_rank;


-- 38. Running total of daily transactions (window function: SUM OVER)
-- This gives cumulative transaction count as we move through dates
SELECT
    transaction_date,
    COUNT(*) AS daily_txns,
    SUM(COUNT(*)) OVER (ORDER BY transaction_date) AS cumulative_txns
FROM upi_transactions
WHERE transaction_status = 'Success'
GROUP BY transaction_date
ORDER BY transaction_date;


-- 39. Transaction value bucket analysis
-- Shows how transactions are distributed across Low/Medium/High/Very High amounts
SELECT amount_bucket,
       COUNT(*) AS txn_count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM upi_transactions), 2) AS pct_of_total,
       ROUND(AVG(transaction_amount), 2) AS avg_amount
FROM upi_transactions
GROUP BY amount_bucket
ORDER BY
    CASE amount_bucket
        WHEN 'Low'       THEN 1
        WHEN 'Medium'    THEN 2
        WHEN 'High'      THEN 3
        WHEN 'Very High' THEN 4
    END;


-- 40. High-value customers who made more than 20 transactions (subquery)
-- The subquery first finds qualifying customer_ids, then outer query fetches details
SELECT customer_id,
       txn_count,
       total_value
FROM (
    SELECT customer_id,
           COUNT(*) AS txn_count,
           ROUND(SUM(transaction_amount), 2) AS total_value
    FROM upi_transactions
    WHERE transaction_status = 'Success'
    GROUP BY customer_id
) AS customer_summary
WHERE txn_count > 20
ORDER BY total_value DESC
LIMIT 20;
