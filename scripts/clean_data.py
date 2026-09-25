"""
clean_data.py
-------------
Preprocessing pipeline for the raw UPI transaction dataset.

Steps performed:
1. Load raw CSV and inspect its shape/types
2. Identify and handle missing values
3. Remove duplicate transaction IDs
4. Validate and fix transaction amounts (remove negatives/zeros)
5. Standardize categorical columns (title-case)
6. Fix transaction_status typos
7. Convert date and time columns to correct types
8. Create useful derived columns for analysis
9. Create amount bucket column for segmentation
10. Save the clean dataset
"""

import pandas as pd
import numpy as np
import os

RAW_PATH   = os.path.join(os.path.dirname(__file__), "..", "data", "raw",       "upi_transactions_raw.csv")
CLEAN_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "upi_transactions_clean.csv")


# ---------------------------------------------------------------
# STEP 1: Load the raw dataset
# ---------------------------------------------------------------
def load_data(path):
    print("=" * 60)
    print("STEP 1: Loading raw data")
    print("=" * 60)
    df = pd.read_csv(path)
    print(f"Shape          : {df.shape}")
    print(f"Columns        : {list(df.columns)}")
    print(f"\nData types:\n{df.dtypes}")
    return df


# ---------------------------------------------------------------
# STEP 2: Inspect missing values
# ---------------------------------------------------------------
def inspect_missing(df):
    print("\n" + "=" * 60)
    print("STEP 2: Missing value analysis")
    print("=" * 60)
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({"Missing Count": missing, "Missing %": missing_pct})
    missing_df = missing_df[missing_df["Missing Count"] > 0]
    print(missing_df.to_string())
    return df


# ---------------------------------------------------------------
# STEP 3: Handle missing values
# ---------------------------------------------------------------
def handle_missing_values(df):
    print("\n" + "=" * 60)
    print("STEP 3: Handling missing values")
    print("=" * 60)

    # merchant_name: fill with "Unknown Merchant" — better than dropping
    before = df["merchant_name"].isnull().sum()
    df["merchant_name"] = df["merchant_name"].fillna("Unknown Merchant")
    print(f"  merchant_name  : filled {before} NaNs with 'Unknown Merchant'")

    # bank_name: fill with "Unknown Bank"
    before = df["bank_name"].isnull().sum()
    df["bank_name"] = df["bank_name"].fillna("Unknown Bank")
    print(f"  bank_name      : filled {before} NaNs with 'Unknown Bank'")

    # customer_age: fill with median age (reasonable imputation)
    before = df["customer_age"].isnull().sum()
    median_age = df["customer_age"].median()
    df["customer_age"] = df["customer_age"].fillna(median_age).astype(int)
    print(f"  customer_age   : filled {before} NaNs with median age ({median_age})")

    # device_type: fill with mode
    before = df["device_type"].isnull().sum()
    mode_device = df["device_type"].mode()[0]
    df["device_type"] = df["device_type"].fillna(mode_device)
    print(f"  device_type    : filled {before} NaNs with mode ('{mode_device}')")

    # failure_reason: NaN is valid for Success/Pending — keep as "N/A"
    df["failure_reason"] = df["failure_reason"].fillna("N/A")
    print(f"  failure_reason : NaN -> 'N/A' (expected for Success/Pending records)")

    return df


# ---------------------------------------------------------------
# STEP 4: Remove duplicate transaction IDs
# ---------------------------------------------------------------
def remove_duplicates(df):
    print("\n" + "=" * 60)
    print("STEP 4: Removing duplicate transaction IDs")
    print("=" * 60)
    before = len(df)
    # Keep the first occurrence of each transaction_id
    df = df.drop_duplicates(subset=["transaction_id"], keep="first")
    after = len(df)
    print(f"  Removed {before - after} duplicate rows. Rows remaining: {after}")
    return df


# ---------------------------------------------------------------
# STEP 5: Validate transaction amounts
# ---------------------------------------------------------------
def validate_amounts(df):
    print("\n" + "=" * 60)
    print("STEP 5: Validating transaction amounts")
    print("=" * 60)

    # Negative amounts
    neg_mask = df["transaction_amount"] < 0
    print(f"  Negative amounts   : {neg_mask.sum()} rows — removing")

    # Zero amounts
    zero_mask = df["transaction_amount"] == 0
    print(f"  Zero amounts       : {zero_mask.sum()} rows — removing")

    # Extremely high outliers (> ₹1,00,000) — UPI daily limit is ₹1 lakh
    high_mask = df["transaction_amount"] > 100000
    print(f"  Amount > ₹1,00,000 : {high_mask.sum()} rows — removing (exceeds UPI limit)")

    # Drop invalid rows
    invalid_mask = neg_mask | zero_mask | high_mask
    df = df[~invalid_mask].reset_index(drop=True)
    print(f"  Rows after cleaning: {len(df)}")
    return df


# ---------------------------------------------------------------
# STEP 6: Standardize categorical columns
# ---------------------------------------------------------------
def standardize_categoricals(df):
    print("\n" + "=" * 60)
    print("STEP 6: Standardizing categorical columns")
    print("=" * 60)

    # Fix inconsistent capitalization introduced during raw data generation
    cat_cols = ["merchant_category", "transaction_type", "payment_method",
                "city", "state", "transaction_status", "device_type",
                "customer_gender", "bank_name"]

    for col in cat_cols:
        df[col] = df[col].astype(str).str.strip().str.title()

    # Fix transaction_status: ensure only valid values exist
    valid_statuses = {"Success", "Failed", "Pending"}
    invalid_statuses = ~df["transaction_status"].isin(valid_statuses)
    if invalid_statuses.sum() > 0:
        print(f"  Found {invalid_statuses.sum()} invalid status values — setting to 'Unknown'")
        df.loc[invalid_statuses, "transaction_status"] = "Unknown"

    # Fix payment method names — UPI should stay uppercase, not become "Upi Qr"
    pm_corrections = {
        "Upi Qr":       "UPI QR",
        "Upi Id":       "UPI ID",
        "Mobile Number":"Mobile Number",
        "Upi Lite":     "UPI Lite",
        "Upi":          "UPI",
    }
    df["payment_method"] = df["payment_method"].replace(pm_corrections)

    # Show unique values for key columns
    for col in ["transaction_status", "payment_method", "merchant_category"]:
        print(f"  {col} unique values: {sorted(df[col].unique())}")

    return df


# ---------------------------------------------------------------
# STEP 7: Convert date/time columns
# ---------------------------------------------------------------
def convert_datetime_columns(df):
    print("\n" + "=" * 60)
    print("STEP 7: Converting date and time columns")
    print("=" * 60)

    df["transaction_date"] = pd.to_datetime(df["transaction_date"], format="%Y-%m-%d")
    df["transaction_time"] = pd.to_datetime(df["transaction_time"], format="%H:%M:%S").dt.time

    print(f"  transaction_date dtype : {df['transaction_date'].dtype}")
    print(f"  transaction_time dtype : {df['transaction_time'].dtype}")
    print(f"  Date range: {df['transaction_date'].min().date()} to {df['transaction_date'].max().date()}")
    return df


# ---------------------------------------------------------------
# STEP 8: Create derived columns
# ---------------------------------------------------------------
def create_derived_columns(df):
    print("\n" + "=" * 60)
    print("STEP 8: Creating derived columns")
    print("=" * 60)

    df["year"]        = df["transaction_date"].dt.year
    df["month"]       = df["transaction_date"].dt.month
    df["month_name"]  = df["transaction_date"].dt.strftime("%B")
    df["day"]         = df["transaction_date"].dt.day
    df["day_name"]    = df["transaction_date"].dt.day_name()
    df["week"]        = df["transaction_date"].dt.isocalendar().week.astype(int)
    df["quarter"]     = df["transaction_date"].dt.quarter
    df["hour"]        = df["transaction_time"].apply(lambda t: t.hour)

    # 1 if the transaction happened on a weekend (Saturday/Sunday)
    df["is_weekend"]  = df["transaction_date"].dt.dayofweek.isin([5, 6]).astype(int)

    # Binary flag for success: 1 = Success, 0 = anything else
    df["transaction_success_flag"] = (df["transaction_status"] == "Success").astype(int)

    # Amount bucket for segmentation
    def bucket_amount(amount):
        if amount < 200:
            return "Low"
        elif amount < 1000:
            return "Medium"
        elif amount < 5000:
            return "High"
        else:
            return "Very High"

    df["amount_bucket"] = df["transaction_amount"].apply(bucket_amount)

    # Year-Month string for easy grouping (e.g., "2023-01")
    df["year_month"] = df["transaction_date"].dt.to_period("M").astype(str)

    print(f"  Derived columns created: year, month, month_name, day, day_name,")
    print(f"                           week, quarter, hour, is_weekend,")
    print(f"                           transaction_success_flag, amount_bucket, year_month")

    return df


# ---------------------------------------------------------------
# STEP 9: Final inspection
# ---------------------------------------------------------------
def final_inspection(df):
    print("\n" + "=" * 60)
    print("STEP 9: Final dataset inspection")
    print("=" * 60)
    print(f"  Shape          : {df.shape}")
    print(f"  Missing values : {df.isnull().sum().sum()}")
    print(f"\n  Descriptive statistics for transaction_amount:")
    print(df["transaction_amount"].describe().round(2).to_string())
    print(f"\n  Status distribution:")
    print(df["transaction_status"].value_counts().to_string())


# ---------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------
def run_pipeline():
    df = load_data(RAW_PATH)
    df = inspect_missing(df)
    df = handle_missing_values(df)
    df = remove_duplicates(df)
    df = validate_amounts(df)
    df = standardize_categoricals(df)
    df = convert_datetime_columns(df)
    df = create_derived_columns(df)
    final_inspection(df)

    # Save the clean dataset
    # Convert transaction_date back to string for CSV compatibility
    df["transaction_date"] = df["transaction_date"].dt.strftime("%Y-%m-%d")
    df["transaction_time"] = df["transaction_time"].apply(str)

    os.makedirs(os.path.dirname(CLEAN_PATH), exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    print(f"\n✅ Clean dataset saved to: {CLEAN_PATH}")
    return df


if __name__ == "__main__":
    run_pipeline()
