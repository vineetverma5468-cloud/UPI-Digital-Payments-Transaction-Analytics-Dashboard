from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR = ROOT / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def normalize_app_name(value: str) -> str:
    mapping = {
        "PHONEPE": "PhonePe",
        "GOOGLEPAY": "Google Pay",
        "GOOGLE PAY": "Google Pay",
        "PAYTM": "Paytm",
        "BHIM": "BHIM",
        "AMAZONPAY": "Amazon Pay",
        "AMAZON PAY": "Amazon Pay",
        "MOBIKWIK": "MobiKwik",
        "FREECHARGE": "Freecharge",
    }
    if pd.isna(value):
        return "Unknown"
    cleaned = str(value).strip()
    return mapping.get(cleaned.upper(), cleaned.title())


def main() -> None:
    fact = pd.read_csv(RAW_DIR / "fact_transactions.csv")
    dim_banks = pd.read_csv(RAW_DIR / "dim_banks.csv")
    dim_merchants = pd.read_csv(RAW_DIR / "dim_merchants.csv")
    dim_regions = pd.read_csv(RAW_DIR / "dim_regions.csv")
    dim_date = pd.read_csv(RAW_DIR / "dim_date.csv")

    original_rows = len(fact)
    fact = fact.drop_duplicates(subset=["transaction_id"], keep="first").copy()
    removed_duplicates = original_rows - len(fact)

    fact["payer_app"] = fact["payer_app"].apply(normalize_app_name)
    fact["device_type"] = fact["device_type"].fillna("Unknown")
    fact["amount"] = fact["amount"].apply(lambda x: abs(float(x)) if pd.notna(x) else 0.0)
    fact["status"] = fact["status"].str.title()
    fact["failure_reason"] = fact["failure_reason"].replace("None", "Unknown")
    fact["failure_reason"] = fact["failure_reason"].fillna("Unknown")
    fact["timestamp"] = pd.to_datetime(fact["timestamp"], errors="coerce")
    fact["hour_of_day"] = fact["hour_of_day"].fillna(0).astype(int)
    fact["is_success"] = (fact["status"] == "Success").astype(int)
    fact["is_failed"] = (fact["status"] == "Failed").astype(int)

    dim_banks["bank_name"] = dim_banks["bank_name"].str.title()
    dim_merchants["merchant_name"] = dim_merchants["merchant_name"].str.title()
    dim_regions["state"] = dim_regions["state"].str.title()
    dim_regions["zone"] = dim_regions["zone"].str.title()
    dim_date["date"] = pd.to_datetime(dim_date["date"], errors="coerce")
    dim_date["month_name"] = dim_date["month_name"].str.title()
    dim_date["day_of_week"] = dim_date["day_of_week"].str.title()

    fact.to_csv(PROCESSED_DIR / "fact_transactions.csv", index=False)
    dim_banks.to_csv(PROCESSED_DIR / "dim_banks.csv", index=False)
    dim_merchants.to_csv(PROCESSED_DIR / "dim_merchants.csv", index=False)
    dim_regions.to_csv(PROCESSED_DIR / "dim_regions.csv", index=False)
    dim_date.to_csv(PROCESSED_DIR / "dim_date.csv", index=False)

    missing_device_count = int(fact["device_type"].eq("Unknown").sum())
    negative_amount_count = int((pd.to_numeric(fact["amount"], errors="coerce") < 0).sum())
    report_lines = [
        "UPI Transaction Data Cleaning Report",
        "===================================",
        f"Original transaction rows: {original_rows}",
        f"Duplicate rows removed: {removed_duplicates}",
        f"Rows with missing device_type filled with 'Unknown': {missing_device_count}",
        f"Rows with negative amounts corrected using absolute value: {negative_amount_count}",
        "Standardized app names to consistent title case naming.",
        "Normalized status values and filled empty failure reasons with 'Unknown'.",
        "Converted timestamp/date fields to valid datetime format for dashboard analysis.",
    ]

    with (DOCS_DIR / "cleaning_report.txt").open("w", encoding="utf-8") as report_file:
        report_file.write("\n".join(report_lines) + "\n")

    print(f"Cleaned data written to {PROCESSED_DIR}")
    print(f"Cleaning report saved to {DOCS_DIR / 'cleaning_report.txt'}")


if __name__ == "__main__":
    main()
