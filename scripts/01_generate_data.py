from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)

BANK_NAMES = [
    "State Bank of India",
    "HDFC Bank",
    "ICICI Bank",
    "Axis Bank",
    "Kotak Mahindra Bank",
    "Punjab National Bank",
    "Canara Bank",
    "Bank of Baroda",
    "Yes Bank",
    "Union Bank of India",
]

MERCHANT_CATEGORIES = [
    "E-commerce",
    "Travel",
    "Groceries",
    "Utilities",
    "Food & Dining",
    "Healthcare",
    "Education",
    "Entertainment",
    "Transport",
    "Retail",
]

PAYER_APPS = ["PhonePe", "Google Pay", "Paytm", "BHIM", "Amazon Pay", "MobiKwik", "Freecharge"]
APP_WEIGHTS = [0.38, 0.24, 0.17, 0.08, 0.07, 0.04, 0.02]

REGION_DATA = [
    {"state": "Maharashtra", "zone": "West"},
    {"state": "Gujarat", "zone": "West"},
    {"state": "Rajasthan", "zone": "North"},
    {"state": "Punjab", "zone": "North"},
    {"state": "Delhi", "zone": "North"},
    {"state": "Uttar Pradesh", "zone": "North"},
    {"state": "Bihar", "zone": "East"},
    {"state": "West Bengal", "zone": "East"},
    {"state": "Odisha", "zone": "East"},
    {"state": "Tamil Nadu", "zone": "South"},
    {"state": "Karnataka", "zone": "South"},
    {"state": "Kerala", "zone": "South"},
    {"state": "Telangana", "zone": "South"},
    {"state": "Madhya Pradesh", "zone": "Central"},
    {"state": "Uttarakhand", "zone": "Central"},
]

TRANSACTION_TYPES = ["P2P", "P2M"]
TYPE_WEIGHTS = [0.42, 0.58]

DEVICE_TYPES = ["Mobile", "Web", "POS", "Tablet"]
DEVICE_WEIGHTS = [0.72, 0.12, 0.11, 0.05]

STATUS_CHOICES = ["SUCCESS", "FAILED", "PENDING"]
STATUS_WEIGHTS = [0.956, 0.036, 0.008]

FAILURE_REASONS = [
    "Bank Server Downtime",
    "Insufficient Balance",
    "Network Timeout",
    "Authentication Failure",
    "UPI ID Invalid",
    "Merchant Issue",
    "KYC/Verification Issue",
    "App Crash",
    "Other",
]
FAILURE_WEIGHTS = [0.28, 0.16, 0.14, 0.12, 0.10, 0.08, 0.06, 0.04, 0.02]


def generate_dim_banks() -> pd.DataFrame:
    return pd.DataFrame({
        "bank_id": np.arange(1, len(BANK_NAMES) + 1),
        "bank_name": BANK_NAMES,
    })


def generate_dim_merchants() -> pd.DataFrame:
    rows = []
    for merchant_id in range(1, 51):
        category = MERCHANT_CATEGORIES[(merchant_id - 1) % len(MERCHANT_CATEGORIES)]
        rows.append({
            "merchant_id": merchant_id,
            "merchant_name": f"{category} Merchant {merchant_id:02d}",
            "merchant_category": category,
        })
    return pd.DataFrame(rows)


def generate_dim_regions() -> pd.DataFrame:
    rows = []
    for region_id, region in enumerate(REGION_DATA, start=1):
        rows.append({
            "region_id": region_id,
            "state": region["state"],
            "zone": region["zone"],
        })
    return pd.DataFrame(rows)


def generate_dim_date() -> pd.DataFrame:
    date_range = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
    df = pd.DataFrame({
        "date_id": date_range.strftime("%Y%m%d").astype(int),
        "date": date_range,
        "month": date_range.month,
        "month_name": date_range.month_name(),
        "year": date_range.year,
        "day_of_week": date_range.day_name(),
        "is_weekend": date_range.dayofweek.isin([5, 6]).astype(int),
    })
    return df


def generate_fact_transactions() -> pd.DataFrame:
    n_rows = 20_000
    dim_date = generate_dim_date()
    bank_ids = np.arange(1, len(BANK_NAMES) + 1)
    merchant_ids = np.arange(1, 51)
    region_ids = np.arange(1, len(REGION_DATA) + 1)

    selected_dates = dim_date.loc[rng.integers(0, len(dim_date), size=n_rows), "date"].reset_index(drop=True)
    timestamps = pd.to_datetime(selected_dates.dt.strftime("%Y-%m-%d")) + pd.to_timedelta(
        rng.integers(0, 24, size=n_rows), unit="h"
    ) + pd.to_timedelta(rng.integers(0, 60, size=n_rows), unit="m")

    data = pd.DataFrame({
        "transaction_id": [f"UPI{idx:07d}" for idx in range(1, n_rows + 1)],
        "timestamp": timestamps,
        "date_id": dim_date.loc[rng.integers(0, len(dim_date), size=n_rows), "date_id"].to_numpy(),
        "sender_bank_id": rng.choice(bank_ids, size=n_rows),
        "receiver_bank_id": rng.choice(bank_ids, size=n_rows),
        "payer_app": rng.choice(PAYER_APPS, size=n_rows, p=APP_WEIGHTS),
        "merchant_id": rng.choice(merchant_ids, size=n_rows),
        "region_id": rng.choice(region_ids, size=n_rows),
        "transaction_type": rng.choice(TRANSACTION_TYPES, size=n_rows, p=TYPE_WEIGHTS),
        "amount": np.exp(rng.normal(loc=5.8, scale=1.2, size=n_rows)),
        "device_type": rng.choice(DEVICE_TYPES, size=n_rows, p=DEVICE_WEIGHTS),
        "status": rng.choice(STATUS_CHOICES, size=n_rows, p=STATUS_WEIGHTS),
        "hour_of_day": rng.choice(np.arange(24), size=n_rows, p=np.array([0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.02, 0.03, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.08, 0.04, 0.03])),
    })

    failed_mask = data["status"] == "FAILED"
    data["failure_reason"] = ""
    data.loc[failed_mask, "failure_reason"] = rng.choice(
        FAILURE_REASONS,
        size=failed_mask.sum(),
        p=FAILURE_WEIGHTS,
    )
    data.loc[~failed_mask, "failure_reason"] = "None"

    # Intentional data quality issues for cleaning pipeline.
    data.loc[rng.choice(n_rows, size=37, replace=False), "amount"] *= -1
    data.loc[rng.choice(n_rows, size=185, replace=False), "device_type"] = np.nan
    conversion_idx = rng.choice(n_rows, size=500, replace=False)
    data.loc[conversion_idx, "payer_app"] = data.loc[conversion_idx, "payer_app"].str.upper()

    duplicate_rows = data.iloc[rng.choice(n_rows, size=100, replace=True)].copy()
    data = pd.concat([data, duplicate_rows], ignore_index=True)

    data["is_success"] = (data["status"] == "SUCCESS").astype(int)
    data["is_failed"] = (data["status"] == "FAILED").astype(int)

    return data


def save_raw_data() -> None:
    dim_banks = generate_dim_banks()
    dim_merchants = generate_dim_merchants()
    dim_regions = generate_dim_regions()
    dim_date = generate_dim_date()
    fact_transactions = generate_fact_transactions()

    dim_banks.to_csv(RAW_DIR / "dim_banks.csv", index=False)
    dim_merchants.to_csv(RAW_DIR / "dim_merchants.csv", index=False)
    dim_regions.to_csv(RAW_DIR / "dim_regions.csv", index=False)
    dim_date.to_csv(RAW_DIR / "dim_date.csv", index=False)
    fact_transactions.to_csv(RAW_DIR / "fact_transactions.csv", index=False)

    print(f"Generated raw datasets in {RAW_DIR}")


if __name__ == "__main__":
    save_raw_data()
