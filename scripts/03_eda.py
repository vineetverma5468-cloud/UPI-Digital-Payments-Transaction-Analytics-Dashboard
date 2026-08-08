from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"
IMAGES_DIR = ROOT / "docs" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def save_plot(fig, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(IMAGES_DIR / filename, dpi=200)
    plt.close(fig)


def main() -> None:
    fact = pd.read_csv(DATA_DIR / "fact_transactions.csv")
    dim_merchants = pd.read_csv(DATA_DIR / "dim_merchants.csv")
    dim_regions = pd.read_csv(DATA_DIR / "dim_regions.csv")

    merged = fact.merge(dim_merchants, on="merchant_id", how="left")
    merged = merged.merge(dim_regions, on="region_id", how="left")

    total_transactions = len(merged)
    total_value = merged["amount"].sum()
    success_rate = merged["is_success"].mean() * 100
    failure_rate = merged["is_failed"].mean() * 100
    peak_hour = merged["hour_of_day"].mode().iloc[0]
    top_failure = merged["failure_reason"].replace("Unknown", "None").value_counts().idxmax()
    top_category = (
        merged.groupby("merchant_category", as_index=False)["amount"].sum()
        .sort_values("amount", ascending=False)
        .iloc[0]
    )
    top_zone = merged.groupby("zone").size().sort_values(ascending=False).index[0]

    print("=== UPI Transaction Analytics Summary ===")
    print(f"Total transactions: {total_transactions:,}")
    print(f"Total transaction value: ₹{total_value:,.2f}")
    print(f"Overall success rate: {success_rate:.2f}%")
    print(f"Failure rate: {failure_rate:.2f}%")
    print(f"Peak transaction hour: {peak_hour}:00")
    print(f"Top failure reason: {top_failure}")
    print(f"Highest value merchant category: {top_category['merchant_category']} (₹{top_category['amount']:,.2f})")
    print(f"Top zone by volume: {top_zone}")

    monthly = merged.assign(month=pd.to_datetime(merged["timestamp"]).dt.to_period("M").astype(str))
    monthly_volume = monthly.groupby("month").size().reset_index(name="transaction_count")
    monthly_volume.columns = ["month", "transaction_count"]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_volume["month"], monthly_volume["transaction_count"], marker="o", linewidth=2)
    ax.set_title("Monthly Transaction Volume")
    ax.set_xlabel("Month")
    ax.set_ylabel("Transactions")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate(rotation=45)
    save_plot(fig, "monthly_transaction_volume.png")

    status_counts = merged["status"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(status_counts.values, labels=status_counts.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Transaction Status Distribution")
    save_plot(fig, "status_distribution.png")

    failure_reasons = merged["failure_reason"].replace("Unknown", "None")
    failure_counts = failure_reasons[failure_reasons != "None"].value_counts().head(8)
    fig, ax = plt.subplots(figsize=(10, 6))
    failure_counts.plot(kind="bar", ax=ax, color="tomato")
    ax.set_title("Top Failure Reasons")
    ax.set_xlabel("Failure Reason")
    ax.set_ylabel("Transactions")
    plt.xticks(rotation=30, ha="right")
    save_plot(fig, "failure_reasons.png")

    category_value = merged.groupby("merchant_category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    category_value.plot(kind="bar", x="merchant_category", y="amount", ax=ax, color="steelblue")
    ax.set_title("Transaction Value by Merchant Category")
    ax.set_xlabel("Merchant Category")
    ax.set_ylabel("Transaction Value")
    plt.xticks(rotation=30, ha="right")
    save_plot(fig, "merchant_category_value.png")

    peak_hours = merged.groupby("hour_of_day").size().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    peak_hours.plot(kind="bar", ax=ax, color="darkgreen")
    ax.set_title("Transaction Volume by Hour of Day")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Transactions")
    save_plot(fig, "hourly_transaction_volume.png")

    print(f"EDA charts saved to {IMAGES_DIR}")


if __name__ == "__main__":
    main()
