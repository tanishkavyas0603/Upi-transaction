"""
generate_data.py
----------------
Generates a synthetic UPI transaction dataset (~75,000 records).
The data is intentionally made statistically realistic:
  - Success/Fail/Pending ratios reflect real UPI patterns
  - Transaction amounts vary by category
  - Volume varies by hour, day, and city
  - Weekends show different spending patterns
  - Controlled data quality issues are injected for cleaning demo
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# Reproducible results
random.seed(42)
np.random.seed(42)

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
TOTAL_RECORDS = 75000
START_DATE = datetime(2023, 1, 1)
END_DATE   = datetime(2024, 6, 30)

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "upi_transactions_raw.csv")

# ------------------------------------------------------------------
# REFERENCE DATA
# ------------------------------------------------------------------

CITIES = {
    "Mumbai":      {"state": "Maharashtra", "weight": 12},
    "Delhi":       {"state": "Delhi",       "weight": 11},
    "Bangalore":   {"state": "Karnataka",   "weight": 10},
    "Hyderabad":   {"state": "Telangana",   "weight": 8},
    "Chennai":     {"state": "Tamil Nadu",  "weight": 7},
    "Pune":        {"state": "Maharashtra", "weight": 6},
    "Kolkata":     {"state": "West Bengal", "weight": 6},
    "Ahmedabad":   {"state": "Gujarat",     "weight": 5},
    "Jaipur":      {"state": "Rajasthan",   "weight": 4},
    "Surat":       {"state": "Gujarat",     "weight": 4},
    "Lucknow":     {"state": "Uttar Pradesh","weight": 3},
    "Kochi":       {"state": "Kerala",      "weight": 3},
    "Chandigarh":  {"state": "Punjab",      "weight": 3},
    "Bhopal":      {"state": "Madhya Pradesh","weight": 2},
    "Nagpur":      {"state": "Maharashtra", "weight": 2},
    "Indore":      {"state": "Madhya Pradesh","weight": 2},
    "Patna":       {"state": "Bihar",       "weight": 2},
    "Vadodara":    {"state": "Gujarat",     "weight": 2},
    "Coimbatore":  {"state": "Tamil Nadu",  "weight": 2},
    "Visakhapatnam":{"state":"Andhra Pradesh","weight": 2},
}
CITY_NAMES   = list(CITIES.keys())
CITY_WEIGHTS = [CITIES[c]["weight"] for c in CITY_NAMES]

CATEGORIES = {
    "Shopping":      {"avg": 1800, "std": 1200, "weight": 18},
    "Food":          {"avg": 350,  "std": 200,  "weight": 20},
    "Travel":        {"avg": 2500, "std": 2000, "weight": 10},
    "Bill Payment":  {"avg": 1200, "std": 800,  "weight": 14},
    "Recharge":      {"avg": 250,  "std": 150,  "weight": 12},
    "Utilities":     {"avg": 900,  "std": 600,  "weight": 8},
    "P2P":           {"avg": 2000, "std": 3000, "weight": 10},
    "Entertainment": {"avg": 600,  "std": 400,  "weight": 8},
}
CAT_NAMES   = list(CATEGORIES.keys())
CAT_WEIGHTS = [CATEGORIES[c]["weight"] for c in CAT_NAMES]

PAYMENT_METHODS = {
    "UPI QR":       0.35,
    "UPI ID":       0.30,
    "Mobile Number":0.20,
    "UPI Lite":     0.10,
    "UPI":          0.05,
}
PM_NAMES   = list(PAYMENT_METHODS.keys())
PM_WEIGHTS = list(PAYMENT_METHODS.values())

BANKS = [
    "SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Bank",
    "Punjab National Bank", "Bank of Baroda", "Canara Bank",
    "IndusInd Bank", "Yes Bank", "PayTM Payments Bank", "Jio Payments Bank"
]

DEVICES = ["Android", "iOS", "Android", "Android", "iOS"]  # Android biased

GENDERS = ["Male", "Female", "Male", "Male", "Female"]     # slight male bias

MERCHANTS = {
    "Shopping":      ["Amazon", "Flipkart", "Myntra", "Meesho", "Nykaa", "Snapdeal"],
    "Food":          ["Swiggy", "Zomato", "Domino's", "McDonald's", "Cafe Coffee Day", "BigBasket"],
    "Travel":        ["IRCTC", "MakeMyTrip", "Goibibo", "OYO", "Ola", "Uber"],
    "Bill Payment":  ["BESCOM", "MSEDCL", "Tata Power", "Airtel", "Jio", "BSNL"],
    "Recharge":      ["Airtel", "Jio", "Vi", "BSNL"],
    "Utilities":     ["Water Board", "Gas Agency", "Internet Provider", "DTH Provider"],
    "P2P":           ["Individual Transfer"],
    "Entertainment": ["BookMyShow", "Hotstar", "Netflix", "Spotify", "PVR Cinemas"],
}

FAILURE_REASONS = {
    "Insufficient Balance":    0.35,
    "Bank Server Down":        0.20,
    "Invalid UPI PIN":         0.18,
    "Transaction Timeout":     0.12,
    "VPA Not Found":           0.08,
    "Daily Limit Exceeded":    0.05,
    "Network Error":           0.02,
}
FR_NAMES   = list(FAILURE_REASONS.keys())
FR_WEIGHTS = list(FAILURE_REASONS.values())

# ------------------------------------------------------------------
# HELPER: generate a realistic timestamp
# ------------------------------------------------------------------

def generate_timestamp(base_date):
    """
    Pick an hour weighted by typical UPI usage patterns.
    Morning rush (8-10am), lunch (12-2pm), evening peak (6-9pm).
    Late night has very low activity.
    """
    hour_weights = [
        1, 1, 1, 1, 1, 2,    # 0-5
        3, 5, 8, 8, 7, 7,    # 6-11
        8, 8, 6, 5, 6, 8,    # 12-17
        10, 10, 8, 6, 4, 2   # 18-23
    ]
    hour = random.choices(range(24), weights=hour_weights, k=1)[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return base_date + timedelta(hours=hour, minutes=minute, seconds=second)


def generate_dates(n):
    """
    Generate n transaction dates distributed across the date range.
    Weekends get ~20% more volume, and some months have spikes (festival months).
    """
    total_days = (END_DATE - START_DATE).days
    dates = []
    while len(dates) < n:
        day_offset = random.randint(0, total_days)
        d = START_DATE + timedelta(days=day_offset)
        # Weekends get a weight boost
        if d.weekday() >= 5:   # Saturday=5, Sunday=6
            if random.random() < 0.55:
                dates.append(d)
        else:
            if random.random() < 0.45:
                dates.append(d)
    return dates[:n]


# ------------------------------------------------------------------
# MAIN GENERATION
# ------------------------------------------------------------------

def generate_dataset(n_records=TOTAL_RECORDS):
    print(f"Generating {n_records} transaction records...")

    dates = generate_dates(n_records)
    random.shuffle(dates)

    rows = []
    used_ids = set()
    customer_pool = [f"CUST{str(i).zfill(5)}" for i in range(1, 8001)]

    for i in range(n_records):
        # Unique transaction ID (with a small chance of duplicate, injected as data quality issue)
        while True:
            txn_id = f"TXN{str(random.randint(100000, 999999))}"
            if txn_id not in used_ids:
                used_ids.add(txn_id)
                break

        base_date = dates[i]
        ts = generate_timestamp(base_date)

        # Category
        category = random.choices(CAT_NAMES, weights=CAT_WEIGHTS, k=1)[0]
        cat_info = CATEGORIES[category]

        # Amount: log-normal distribution shaped to category averages
        amount = max(1.0, np.random.lognormal(
            mean=np.log(cat_info["avg"]),
            sigma=0.6
        ))
        amount = round(amount, 2)

        # Payment method
        payment_method = random.choices(PM_NAMES, weights=PM_WEIGHTS, k=1)[0]

        # City / State
        city = random.choices(CITY_NAMES, weights=CITY_WEIGHTS, k=1)[0]
        state = CITIES[city]["state"]

        # Customer
        customer_id = random.choice(customer_pool)
        # Assign stable demographics per customer (approximate)
        cust_seed = int(customer_id[4:])
        cust_age = 18 + (cust_seed % 45)   # ages 18-62
        cust_gender = "Female" if cust_seed % 3 == 0 else "Male"

        # Device
        device = random.choice(DEVICES)

        # Bank
        bank = random.choice(BANKS)

        # Status: ~88% Success, ~9% Failed, ~3% Pending
        status_roll = random.random()
        if status_roll < 0.88:
            status = "Success"
            failure_reason = None
        elif status_roll < 0.97:
            status = "Failed"
            failure_reason = random.choices(FR_NAMES, weights=FR_WEIGHTS, k=1)[0]
        else:
            status = "Pending"
            failure_reason = None

        # Merchant
        merchant_name = random.choice(MERCHANTS[category])

        rows.append({
            "transaction_id":     txn_id,
            "transaction_date":   base_date.strftime("%Y-%m-%d"),
            "transaction_time":   ts.strftime("%H:%M:%S"),
            "transaction_amount": amount,
            "transaction_type":   category,
            "payment_method":     payment_method,
            "merchant_category":  category,
            "merchant_name":      merchant_name,
            "customer_id":        customer_id,
            "customer_age":       cust_age,
            "customer_gender":    cust_gender,
            "city":               city,
            "state":              state,
            "device_type":        device,
            "bank_name":          bank,
            "transaction_status": status,
            "failure_reason":     failure_reason,
        })

    df = pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # INJECT CONTROLLED DATA QUALITY ISSUES
    # ------------------------------------------------------------------
    print("Injecting controlled data quality issues...")

    # 1. Duplicate transaction IDs (~0.3% of records)
    dup_count = int(n_records * 0.003)
    dup_indices = np.random.choice(df.index, size=dup_count, replace=False)
    dup_rows = df.loc[dup_indices].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)

    # 2. Missing values in non-critical columns (~1-2%)
    missing_cols = ["merchant_name", "bank_name", "customer_age", "device_type", "failure_reason"]
    for col in missing_cols:
        if col == "failure_reason":
            continue   # already NaN for Success/Pending — intentional
        n_missing = int(len(df) * random.uniform(0.005, 0.012))
        miss_idx = np.random.choice(df.index, size=n_missing, replace=False)
        df.loc[miss_idx, col] = np.nan

    # 3. Inconsistent capitalization in category columns
    cat_mask = np.random.choice(df.index, size=int(len(df) * 0.04), replace=False)
    df.loc[cat_mask, "merchant_category"] = df.loc[cat_mask, "merchant_category"].str.upper()

    pm_mask = np.random.choice(df.index, size=int(len(df) * 0.03), replace=False)
    df.loc[pm_mask, "payment_method"] = df.loc[pm_mask, "payment_method"].str.lower()

    # 4. A few invalid/negative transaction amounts
    invalid_idx = np.random.choice(df.index, size=15, replace=False)
    df.loc[invalid_idx, "transaction_amount"] = df.loc[invalid_idx, "transaction_amount"].apply(
        lambda x: -abs(x) if random.random() < 0.5 else 0
    )

    # 5. A handful of wrong status values (typos)
    typo_idx = np.random.choice(df.index, size=8, replace=False)
    df.loc[typo_idx, "transaction_status"] = "success"   # lowercase typo

    # Shuffle rows so issues are scattered
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"Final raw dataset shape: {df.shape}")
    return df


if __name__ == "__main__":
    df = generate_dataset()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Raw dataset saved to: {OUTPUT_PATH}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nSample records:\n{df.head(3).to_string()}")
