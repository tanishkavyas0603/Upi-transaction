"""
run_analysis.py
---------------
Runs SQL analytical queries against the SQLite database
and generates all EDA charts.

Usage:
    python scripts/run_analysis.py
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")   # non-interactive backend for saving files
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore")

DB_PATH     = os.path.join(os.path.dirname(__file__), "..", "database", "upi_transactions.db")
CHARTS_DIR  = os.path.join(os.path.dirname(__file__), "..", "outputs", "charts")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs", "reports")
os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ------------------------------------------------------------------
# Chart styling
# ------------------------------------------------------------------
PALETTE    = sns.color_palette("Set2")
ACCENT     = "#2E86AB"
SUCCESS_C  = "#27AE60"
FAIL_C     = "#E74C3C"
PENDING_C  = "#F39C12"

plt.rcParams.update({
    "figure.dpi":     120,
    "font.family":    "DejaVu Sans",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.grid":      True,
    "grid.alpha":     0.3,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})

def run_query(conn, sql):
    """Execute a SQL query and return a DataFrame."""
    return pd.read_sql_query(sql, conn)

def save_chart(fig, filename):
    path = os.path.join(CHARTS_DIR, filename)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {filename}")

# ==================================================================
# CHART 1: Transaction Status Distribution (Pie + Bar)
# ==================================================================
def chart_status_distribution(conn):
    df = run_query(conn, """
        SELECT transaction_status,
               COUNT(*) AS txn_count,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM upi_transactions), 2) AS pct
        FROM upi_transactions
        GROUP BY transaction_status
        ORDER BY txn_count DESC
    """)
    print(df.to_string(index=False))

    colors = [SUCCESS_C if s == "Success" else FAIL_C if s == "Failed" else PENDING_C
              for s in df["transaction_status"]]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Transaction Status Distribution", fontsize=14, fontweight="bold")

    # Pie chart
    axes[0].pie(df["txn_count"], labels=df["transaction_status"],
                autopct="%1.1f%%", colors=colors, startangle=90)
    axes[0].set_title("Share of Transactions")

    # Bar chart
    axes[1].bar(df["transaction_status"], df["txn_count"], color=colors, width=0.5)
    axes[1].set_title("Count by Status")
    axes[1].set_xlabel("Status")
    axes[1].set_ylabel("Number of Transactions")
    for bar, val in zip(axes[1].patches, df["txn_count"]):
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
                     f"{val:,}", ha="center", va="bottom", fontsize=10)

    save_chart(fig, "01_status_distribution.png")
    return df


# ==================================================================
# CHART 2: Transaction Volume by Category
# ==================================================================
def chart_category_volume(conn):
    df = run_query(conn, """
        SELECT merchant_category,
               COUNT(*) AS txn_count
        FROM upi_transactions
        GROUP BY merchant_category
        ORDER BY txn_count DESC
    """)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df["merchant_category"], df["txn_count"],
                   color=sns.color_palette("Set2", len(df)))
    ax.set_title("Transaction Volume by Category", fontweight="bold")
    ax.set_xlabel("Number of Transactions")
    ax.set_ylabel("Category")
    for bar in bars:
        ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height() / 2,
                f"{int(bar.get_width()):,}", va="center", fontsize=9)
    save_chart(fig, "02_category_volume.png")
    return df


# ==================================================================
# CHART 3: Transaction Value by Category
# ==================================================================
def chart_category_value(conn):
    df = run_query(conn, """
        SELECT merchant_category,
               ROUND(SUM(transaction_amount) / 1e6, 2) AS total_value_mn
        FROM upi_transactions
        WHERE transaction_status = 'Success'
        GROUP BY merchant_category
        ORDER BY total_value_mn DESC
    """)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df["merchant_category"], df["total_value_mn"],
                   color=sns.color_palette("Blues_d", len(df)))
    ax.set_title("Successful Transaction Value by Category (₹ Millions)", fontweight="bold")
    ax.set_xlabel("Total Value (₹ Millions)")
    ax.set_ylabel("Category")
    for bar in bars:
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                f"₹{bar.get_width():.1f}M", va="center", fontsize=9)
    save_chart(fig, "03_category_value.png")
    return df


# ==================================================================
# CHART 4: Payment Method Usage
# ==================================================================
def chart_payment_method(conn):
    df = run_query(conn, """
        SELECT payment_method,
               COUNT(*) AS txn_count,
               ROUND(SUM(transaction_amount) / 1e6, 2) AS total_value_mn
        FROM upi_transactions
        GROUP BY payment_method
        ORDER BY txn_count DESC
    """)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Payment Method Analysis", fontsize=14, fontweight="bold")

    colors = sns.color_palette("Paired", len(df))
    axes[0].bar(df["payment_method"], df["txn_count"], color=colors)
    axes[0].set_title("Transaction Count")
    axes[0].set_xlabel("Payment Method")
    axes[0].set_ylabel("Count")
    axes[0].tick_params(axis="x", rotation=30)

    axes[1].bar(df["payment_method"], df["total_value_mn"], color=colors)
    axes[1].set_title("Transaction Value (₹ Millions)")
    axes[1].set_xlabel("Payment Method")
    axes[1].set_ylabel("Value (₹ Millions)")
    axes[1].tick_params(axis="x", rotation=30)

    save_chart(fig, "04_payment_method.png")
    return df


# ==================================================================
# CHART 5: Daily Transaction Trend
# ==================================================================
def chart_daily_trend(conn):
    df = run_query(conn, """
        SELECT transaction_date,
               COUNT(*) AS txn_count,
               ROUND(SUM(transaction_amount) / 1e3, 2) AS value_k
        FROM upi_transactions
        WHERE transaction_status = 'Success'
        GROUP BY transaction_date
        ORDER BY transaction_date
    """)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df["transaction_date"], df["txn_count"], color=ACCENT, linewidth=1.2, alpha=0.8)
    # 7-day rolling average
    rolling_avg = df["txn_count"].rolling(window=7, center=True).mean()
    ax.plot(df["transaction_date"], rolling_avg, color="red", linewidth=2, label="7-day avg")
    ax.set_title("Daily Transaction Volume (Successful)", fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Transactions")
    ax.legend()
    save_chart(fig, "05_daily_trend.png")
    return df


# ==================================================================
# CHART 6: Monthly Transaction Trend
# ==================================================================
def chart_monthly_trend(conn):
    df = run_query(conn, """
        SELECT year_month,
               COUNT(*) AS txn_count,
               ROUND(SUM(transaction_amount) / 1e6, 2) AS value_mn
        FROM upi_transactions
        WHERE transaction_status = 'Success'
        GROUP BY year_month
        ORDER BY year_month
    """)

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    fig.suptitle("Monthly Transaction Trends", fontsize=14, fontweight="bold")

    x = range(len(df))
    axes[0].bar(x, df["txn_count"], color=ACCENT, alpha=0.8)
    axes[0].set_ylabel("Transaction Count")
    axes[0].set_title("Monthly Volume")

    axes[1].bar(x, df["value_mn"], color=SUCCESS_C, alpha=0.8)
    axes[1].set_ylabel("Total Value (₹ Millions)")
    axes[1].set_title("Monthly Transaction Value")
    axes[1].set_xticks(list(x))
    axes[1].set_xticklabels(df["year_month"].tolist(), rotation=45, ha="right", fontsize=8)

    plt.tight_layout()
    save_chart(fig, "06_monthly_trend.png")
    return df


# ==================================================================
# CHART 7: Transactions by Hour
# ==================================================================
def chart_hourly(conn):
    df = run_query(conn, """
        SELECT hour,
               COUNT(*) AS txn_count
        FROM upi_transactions
        GROUP BY hour
        ORDER BY hour
    """)

    fig, ax = plt.subplots(figsize=(12, 5))
    colors = [SUCCESS_C if h in range(18, 22) else ACCENT for h in df["hour"]]
    ax.bar(df["hour"], df["txn_count"], color=colors, width=0.8)
    ax.set_title("Transaction Volume by Hour of Day", fontweight="bold")
    ax.set_xlabel("Hour (0 = Midnight, 12 = Noon)")
    ax.set_ylabel("Number of Transactions")
    ax.set_xticks(range(0, 24))
    ax.set_xticklabels([f"{h}:00" for h in range(24)], rotation=45, fontsize=8)
    ax.text(19, df["txn_count"].max() * 0.9, "Evening Peak", color="green", fontsize=10)
    save_chart(fig, "07_hourly_distribution.png")
    return df


# ==================================================================
# CHART 8: Transactions by Day of Week
# ==================================================================
def chart_day_of_week(conn):
    df = run_query(conn, """
        SELECT day_name,
               COUNT(*) AS txn_count,
               ROUND(AVG(transaction_amount), 2) AS avg_amount
        FROM upi_transactions
        GROUP BY day_name
    """)
    # Order days correctly
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["day_name"] = pd.Categorical(df["day_name"], categories=day_order, ordered=True)
    df = df.sort_values("day_name")

    colors = ["#E74C3C" if d in ["Saturday", "Sunday"] else ACCENT for d in df["day_name"]]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Transactions by Day of Week", fontsize=14, fontweight="bold")

    axes[0].bar(df["day_name"], df["txn_count"], color=colors)
    axes[0].set_title("Transaction Count")
    axes[0].set_xlabel("Day")
    axes[0].set_ylabel("Count")
    axes[0].tick_params(axis="x", rotation=30)

    axes[1].bar(df["day_name"], df["avg_amount"], color=colors)
    axes[1].set_title("Average Transaction Amount (₹)")
    axes[1].set_xlabel("Day")
    axes[1].set_ylabel("Avg Amount (₹)")
    axes[1].tick_params(axis="x", rotation=30)

    save_chart(fig, "08_day_of_week.png")
    return df


# ==================================================================
# CHART 9: Top Cities by Transaction Value
# ==================================================================
def chart_top_cities(conn):
    df = run_query(conn, """
        SELECT city,
               COUNT(*) AS txn_count,
               ROUND(SUM(transaction_amount) / 1e6, 2) AS total_value_mn,
               ROUND(AVG(transaction_success_flag) * 100, 2) AS success_rate
        FROM upi_transactions
        GROUP BY city
        ORDER BY total_value_mn DESC
        LIMIT 15
    """)

    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    fig.suptitle("Top Cities — Transaction Value & Success Rate", fontsize=14, fontweight="bold")

    colors = sns.color_palette("tab20", len(df))
    axes[0].barh(df["city"][::-1], df["total_value_mn"][::-1], color=colors)
    axes[0].set_title("Total Value (₹ Millions)")
    axes[0].set_xlabel("Value (₹ Millions)")

    axes[1].barh(df["city"][::-1], df["success_rate"][::-1], color=SUCCESS_C, alpha=0.75)
    axes[1].set_title("Success Rate (%)")
    axes[1].set_xlabel("Success Rate (%)")
    axes[1].axvline(x=88, color="red", linestyle="--", label="Overall Avg")
    axes[1].legend()

    save_chart(fig, "09_top_cities.png")
    return df


# ==================================================================
# CHART 10: Failure Reasons Distribution
# ==================================================================
def chart_failure_reasons(conn):
    df = run_query(conn, """
        SELECT failure_reason,
               COUNT(*) AS fail_count
        FROM upi_transactions
        WHERE transaction_status = 'Failed'
          AND failure_reason != 'N/A'
        GROUP BY failure_reason
        ORDER BY fail_count DESC
    """)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df["failure_reason"][::-1], df["fail_count"][::-1], color=FAIL_C, alpha=0.8)
    ax.set_title("Most Common Failure Reasons", fontweight="bold")
    ax.set_xlabel("Number of Failed Transactions")
    ax.set_ylabel("Failure Reason")
    for bar in bars:
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height() / 2,
                f"{int(bar.get_width()):,}", va="center", fontsize=9)
    save_chart(fig, "10_failure_reasons.png")
    return df


# ==================================================================
# KPI CALCULATION
# ==================================================================
def calculate_kpis(conn):
    print("\n" + "=" * 60)
    print("KEY PERFORMANCE INDICATORS")
    print("=" * 60)

    kpi_queries = {
        "Total Transactions":
            "SELECT COUNT(*) FROM upi_transactions",
        "Total Transaction Value (₹)":
            "SELECT ROUND(SUM(transaction_amount), 2) FROM upi_transactions WHERE transaction_status='Success'",
        "Average Transaction Amount (₹)":
            "SELECT ROUND(AVG(transaction_amount), 2) FROM upi_transactions WHERE transaction_status='Success'",
        "Success Rate (%)":
            "SELECT ROUND(AVG(transaction_success_flag) * 100, 2) FROM upi_transactions",
        "Failure Rate (%)":
            "SELECT ROUND(SUM(CASE WHEN transaction_status='Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) FROM upi_transactions",
        "Unique Customers":
            "SELECT COUNT(DISTINCT customer_id) FROM upi_transactions",
        "Unique Merchants":
            "SELECT COUNT(DISTINCT merchant_name) FROM upi_transactions",
        "Peak Transaction Hour":
            "SELECT hour FROM upi_transactions GROUP BY hour ORDER BY COUNT(*) DESC LIMIT 1",
        "Top Category by Value":
            "SELECT merchant_category FROM upi_transactions WHERE transaction_status='Success' GROUP BY merchant_category ORDER BY SUM(transaction_amount) DESC LIMIT 1",
        "Top City by Value":
            "SELECT city FROM upi_transactions WHERE transaction_status='Success' GROUP BY city ORDER BY SUM(transaction_amount) DESC LIMIT 1",
        "Most Used Payment Method":
            "SELECT payment_method FROM upi_transactions GROUP BY payment_method ORDER BY COUNT(*) DESC LIMIT 1",
    }

    kpis = {}
    for label, query in kpi_queries.items():
        result = run_query(conn, query).iloc[0, 0]
        kpis[label] = result
        print(f"  {label:<40}: {result}")

    return kpis


# ==================================================================
# MAIN
# ==================================================================
def main():
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)

    print("\n" + "=" * 60)
    print("RUNNING SQL ANALYTICS QUERIES")
    print("=" * 60)

    kpis = calculate_kpis(conn)

    print("\nGenerating charts...")
    print("\n--- Chart 1: Status Distribution ---")
    chart_status_distribution(conn)

    print("--- Chart 2: Category Volume ---")
    chart_category_volume(conn)

    print("--- Chart 3: Category Value ---")
    chart_category_value(conn)

    print("--- Chart 4: Payment Method ---")
    chart_payment_method(conn)

    print("--- Chart 5: Daily Trend ---")
    chart_daily_trend(conn)

    print("--- Chart 6: Monthly Trend ---")
    chart_monthly_trend(conn)

    print("--- Chart 7: Hourly Distribution ---")
    chart_hourly(conn)

    print("--- Chart 8: Day of Week ---")
    chart_day_of_week(conn)

    print("--- Chart 9: Top Cities ---")
    chart_top_cities(conn)

    print("--- Chart 10: Failure Reasons ---")
    chart_failure_reasons(conn)

    conn.close()
    print(f"\n✅ All charts saved to: {CHARTS_DIR}")


if __name__ == "__main__":
    main()
