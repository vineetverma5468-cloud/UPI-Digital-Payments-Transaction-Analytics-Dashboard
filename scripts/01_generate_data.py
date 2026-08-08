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
STATUS_WEIGHTS = [0.957, 0.035, 0.008]

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
        suffix = f"{merchant_id:02d}"
        rows.append({
            "merchant_id": merchant_id,
            "merchant_name": f"{category} Merchant {suffix}",
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
    return pd.DataFrame({
        "date_id": date_range.strftime("%Y%m%d").astype(int),
        "date": date_range,
        "month": date_range.month,
        "month_name": date_range.month_name(),
        "year": date_range.year,
        "day_of_week": date_range.day_name(),
        "is_weekend": date_range.dayofweek.isin([5, 6]).astype(int),
    })


def generate_fact_transactions() -> pd.DataFrame:
    n_rows = 22_000
    dim_date = generate_dim_date()
    bank_ids = np.arange(1, len(BANK_NAMES) + 1)
    merchant_ids = np.arange(1, 51)
    region_ids = np.arange(1, len(REGION_DATA) + 1)

    selected_dates = rng.choice(dim_date["date"].to_numpy(), size=n_rows, replace=True)
    timestamps = pd.to_datetime(selected_dates) + pd.to_timedelta(
        rng.integers(0, 24, size=n_rows), unit="h"
    ) + pd.to_timedelta(rng.integers(0, 60, size=n_rows), unit="m")

    merchant_category_multiplier = {
        "E-commerce": 1.45,
        "Travel": 1.70,
        "Groceries": 1.10,
        "Utilities": 1.20,
        "Food & Dining": 1.30,
        "Healthcare": 1.50,
        "Education": 1.35,
        "Entertainment": 1.40,
        "Transport": 1.25,
        "Retail": 1.15,
    }

    transaction_type_base = {"P2P": 450.0, "P2M": 950.0}
    merchant_id_array = rng.choice(merchant_ids, size=n_rows)
    type_array = rng.choice(TRANSACTION_TYPES, size=n_rows, p=TYPE_WEIGHTS)
    category_array = [MERCHANT_CATEGORIES[(mid - 1) % len(MERCHANT_CATEGORIES)] for mid in merchant_id_array]

    amount_base = [transaction_type_base[t] * merchant_category_multiplier[c] for c, t in zip(category_array, type_array)]
    amount = np.array(amount_base) * rng.lognormal(mean=0.0, sigma=0.55, size=n_rows)
    amount = np.clip(np.round(amount, 2), 50.0, 200000.0)

    status_array = rng.choice(STATUS_CHOICES, size=n_rows, p=STATUS_WEIGHTS)
    failure_reason = np.full(n_rows, "None", dtype=object)
    failed_mask = status_array == "FAILED"
    failure_reason[failed_mask] = rng.choice(FAILURE_REASONS, size=failed_mask.sum(), p=FAILURE_WEIGHTS)

    date_id_values = pd.to_datetime(selected_dates).strftime("%Y%m%d").astype(int)
    data = pd.DataFrame({
        "transaction_id": [f"UPI{idx:07d}" for idx in range(1, n_rows + 1)],
        "timestamp": timestamps,
        "date_id": date_id_values,
        "sender_bank_id": rng.choice(bank_ids, size=n_rows),
        "receiver_bank_id": rng.choice(bank_ids, size=n_rows),
        "payer_app": rng.choice(PAYER_APPS, size=n_rows, p=APP_WEIGHTS),
        "merchant_id": merchant_id_array,
        "region_id": rng.choice(region_ids, size=n_rows),
        "transaction_type": type_array,
        "amount": amount,
        "device_type": rng.choice(DEVICE_TYPES, size=n_rows, p=DEVICE_WEIGHTS),
        "status": status_array,
        "failure_reason": failure_reason,
        "hour_of_day": rng.integers(0, 24, size=n_rows),
    })

    data["is_success"] = (data["status"] == "SUCCESS").astype(int)
    data["is_failed"] = (data["status"] == "FAILED").astype(int)

    timestamp_dt = pd.to_datetime(data["timestamp"])
    data["hour_of_day"] = timestamp_dt.dt.hour
    data["status"] = data["status"].str.title()
    data["failure_reason"] = np.where(data["status"] == "Failed", data["failure_reason"], "None")
    data["payer_app"] = data["payer_app"].str.title()
    data["device_type"] = data["device_type"].str.title()

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

    print(f"Generated realistic public-style payment datasets in {RAW_DIR}")


if __name__ == "__main__":
    save_raw_data()
