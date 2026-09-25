"""
load_database.py
----------------
Loads the cleaned UPI transaction dataset into a SQLite database.
Creates the upi_transactions table with appropriate schema and indexes.
"""

import pandas as pd
import sqlite3
import os

CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "upi_transactions_clean.csv")
DB_PATH    = os.path.join(os.path.dirname(__file__), "..", "database", "upi_transactions.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS upi_transactions (
    transaction_id           TEXT PRIMARY KEY,
    transaction_date         TEXT,
    transaction_time         TEXT,
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
    transaction_status       TEXT,
    failure_reason           TEXT,
    year                     INTEGER,
    month                    INTEGER,
    month_name               TEXT,
    day                      INTEGER,
    day_name                 TEXT,
    week                     INTEGER,
    quarter                  INTEGER,
    hour                     INTEGER,
    is_weekend               INTEGER,
    transaction_success_flag INTEGER,
    amount_bucket            TEXT,
    year_month               TEXT
);
"""

# Indexes on frequently queried columns speed up analytical queries
INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_date            ON upi_transactions(transaction_date);",
    "CREATE INDEX IF NOT EXISTS idx_customer        ON upi_transactions(customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_city            ON upi_transactions(city);",
    "CREATE INDEX IF NOT EXISTS idx_status          ON upi_transactions(transaction_status);",
    "CREATE INDEX IF NOT EXISTS idx_category        ON upi_transactions(merchant_category);",
    "CREATE INDEX IF NOT EXISTS idx_payment         ON upi_transactions(payment_method);",
    "CREATE INDEX IF NOT EXISTS idx_year_month      ON upi_transactions(year_month);",
]


def load_to_sqlite():
    print("Loading clean data into SQLite...")

    df = pd.read_csv(CLEAN_PATH)
    print(f"  Records to load: {len(df)}")

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Remove existing DB so we start fresh each run
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("  Removed existing database.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table
    cursor.execute(SCHEMA_SQL)
    print("  Table 'upi_transactions' created.")

    # Load data using pandas (much faster than row-by-row inserts)
    df.to_sql("upi_transactions", conn, if_exists="append", index=False)
    print(f"  Loaded {len(df)} records successfully.")

    # Create indexes
    for idx_sql in INDEXES_SQL:
        cursor.execute(idx_sql)
    print("  Indexes created.")

    # Verify row count
    result = cursor.execute("SELECT COUNT(*) FROM upi_transactions").fetchone()
    print(f"  Verified row count in DB: {result[0]}")

    conn.commit()
    conn.close()
    print(f"\n✅ SQLite database saved to: {DB_PATH}")


if __name__ == "__main__":
    load_to_sqlite()
