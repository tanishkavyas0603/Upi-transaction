-- schema.sql
-- Defines the upi_transactions table and analytical indexes.
-- This is the single source of truth for the database structure.

CREATE TABLE IF NOT EXISTS upi_transactions (
    transaction_id           TEXT PRIMARY KEY,
    transaction_date         TEXT,           -- stored as YYYY-MM-DD string
    transaction_time         TEXT,           -- stored as HH:MM:SS string
    transaction_amount       REAL,
    transaction_type         TEXT,
    payment_method           TEXT,
    merchant_category        TEXT,
    merchant_name            TEXT,
    customer_id              TEXT,
    customer_age             INTEGER,
    customer_gender          TEXT,
    city                     TEXT,
    state                    TEXT,
    device_type              TEXT,
    bank_name                TEXT,
    transaction_status       TEXT,           -- Success / Failed / Pending
    failure_reason           TEXT,           -- N/A for non-failed rows
    year                     INTEGER,
    month                    INTEGER,
    month_name               TEXT,
    day                      INTEGER,
    day_name                 TEXT,
    week                     INTEGER,
    quarter                  INTEGER,
    hour                     INTEGER,
    is_weekend               INTEGER,        -- 1 = weekend, 0 = weekday
    transaction_success_flag INTEGER,        -- 1 = Success, 0 = otherwise
    amount_bucket            TEXT,           -- Low / Medium / High / Very High
    year_month               TEXT            -- e.g., 2023-01
);

-- Indexes on frequently filtered / grouped columns
CREATE INDEX IF NOT EXISTS idx_date       ON upi_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_customer   ON upi_transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_city       ON upi_transactions(city);
CREATE INDEX IF NOT EXISTS idx_status     ON upi_transactions(transaction_status);
CREATE INDEX IF NOT EXISTS idx_category   ON upi_transactions(merchant_category);
CREATE INDEX IF NOT EXISTS idx_payment    ON upi_transactions(payment_method);
CREATE INDEX IF NOT EXISTS idx_year_month ON upi_transactions(year_month);
