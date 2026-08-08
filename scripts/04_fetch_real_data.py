from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REAL_DIR = ROOT / "data" / "real"
PROCESSED_DIR = ROOT / "data" / "processed"
REAL_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DATA_URL = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"
PAYER_APPS = ["PhonePe", "Google Pay", "Paytm", "BHIM", "Amazon Pay", "MobiKwik"]
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
REGION_ROWS = [
    {"state": "Maharashtra", "zone": "West"},
    {"state": "Delhi", "zone": "North"},
    {"state": "Tamil Nadu", "zone": "South"},
    {"state": "West Bengal", "zone": "East"},
    {"state": "Karnataka", "zone": "South"},
    {"state": "Gujarat", "zone": "West"},
    {"state": "Uttar Pradesh", "zone": "North"},
    {"state": "Kerala", "zone": "South"},
    {"state": "Bihar", "zone": "East"},
    {"state": "Madhya Pradesh", "zone": "Central"},
]


def download_public_dataset(url: str, output_path: Path) -> Path:
    with urlopen(url, timeout=60) as response:
        data = response.read()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    return output_path


def generate_dim_merchants() -> pd.DataFrame:
    rows = []
    for merchant_id, category in enumerate(MERCHANT_CATEGORIES, start=1):
        rows.append(
            {
                "merchant_id": merchant_id,
                "merchant_name": f"{category} Merchant {merchant_id:02d}",
                "merchant_category": category,
            }
        )
    return pd.DataFrame(rows)


def generate_dim_regions() -> pd.DataFrame:
    rows = []
    for region_id, row in enumerate(REGION_ROWS, start=1):
        rows.append({
            "region_id": region_id,
            "state": row["state"],
            "zone": row["zone"],
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


def create_dashboard_data(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    amount_col = next((c for c in ["total_bill", "amount", "value", "total", "sales", "revenue"] if c in raw_df.columns), None)
    if amount_col is None:
        numeric_columns = raw_df.select_dtypes(include=["number"]).columns.tolist()
        if not numeric_columns:
            raise ValueError("No numeric amount column found in the public dataset.")
        amount_col = numeric_columns[0]

    raw_df = raw_df.copy()
    raw_df["amount"] = pd.to_numeric(raw_df[amount_col], errors="coerce").fillna(0.0)
    n_rows = len(raw_df)
    timestamps = pd.date_range(start="2024-01-01 00:00:00", periods=n_rows, freq="h")

    merchant_df = generate_dim_merchants()
    region_df = generate_dim_regions()
    date_df = generate_dim_date()

    rng = np.random.default_rng(42)
    merchant_ids = np.resize(np.arange(1, len(merchant_df) + 1), n_rows)
    region_ids = np.resize(np.arange(1, len(region_df) + 1), n_rows)
    payer_apps = np.resize(np.array(PAYER_APPS), n_rows)
    transaction_types = np.resize(np.array(["P2P", "P2M"]), n_rows)
    device_types = np.resize(np.array(["Mobile", "Web", "POS"]), n_rows)

    status_choice = np.where(rng.random(n_rows) < 0.96, "Success", "Failed")
    failure_reason = np.where(status_choice == "Failed", rng.choice(["Network Timeout", "Insufficient Balance", "Authentication Failure", "Bank Issue", "Merchant Issue"], size=n_rows), "Unknown")

    fact = pd.DataFrame({
        "transaction_id": [f"REAL{idx:07d}" for idx in range(1, n_rows + 1)],
        "timestamp": timestamps,
        "date_id": timestamps.strftime("%Y%m%d").astype(int),
        "sender_bank_id": rng.integers(1, 11, size=n_rows),
        "receiver_bank_id": rng.integers(1, 11, size=n_rows),
        "payer_app": payer_apps,
        "merchant_id": merchant_ids,
        "region_id": region_ids,
        "transaction_type": transaction_types,
        "amount": raw_df["amount"].values,
        "device_type": device_types,
        "status": status_choice,
        "failure_reason": failure_reason,
        "hour_of_day": timestamps.hour.values,
    })
    fact["is_success"] = (fact["status"] == "Success").astype(int)
    fact["is_failed"] = (fact["status"] == "Failed").astype(int)

    fact = fact.merge(merchant_df[["merchant_id", "merchant_category"]], on="merchant_id", how="left")
    fact = fact.merge(region_df[["region_id", "zone"]], on="region_id", how="left")

    return fact, merchant_df, region_df, date_df


def main() -> None:
    raw_csv = REAL_DIR / "raw_public_dataset.csv"
    if not raw_csv.exists():
        download_public_dataset(DEFAULT_DATA_URL, raw_csv)

    public_df = pd.read_csv(raw_csv)
    fact, dim_merchants, dim_regions, dim_date = create_dashboard_data(public_df)

    dim_merchants.to_csv(PROCESSED_DIR / "dim_merchants.csv", index=False)
    dim_regions.to_csv(PROCESSED_DIR / "dim_regions.csv", index=False)
    dim_date.to_csv(PROCESSED_DIR / "dim_date.csv", index=False)
    fact.to_csv(PROCESSED_DIR / "fact_transactions.csv", index=False)

    print(f"Downloaded public dataset to: {raw_csv}")
    print(f"Processed dashboard-ready data to: {PROCESSED_DIR}")
    print(f"Fact rows: {len(fact)}")
    print(f"Status values: {sorted(fact['status'].unique().tolist())}")
    print(fact.head(3).to_dict(orient="records"))


if __name__ == "__main__":
    main()
