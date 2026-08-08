# UPI / Digital Payments Transaction Analytics Dashboard

A Power BI dashboard analyzing synthetic UPI (Unified Payments Interface) transaction data
to monitor transaction health, failure patterns, peak load times, and merchant/regional
performance for a digital payments business.

![Status](https://img.shields.io/badge/status-complete-brightgreen)
![Tool](https://img.shields.io/badge/tool-Power%20BI-yellow)
![Language](https://img.shields.io/badge/language-Python%20%2B%20DAX-blue)

---

## 📌 Problem Statement

Digital payment platforms process millions of UPI transactions daily, but without a
unified view of transaction health, businesses struggle to answer basic operational
questions in real time: Where are transactions failing? When is system load highest?
Which merchant categories and regions drive the most volume? This project builds an
interactive Power BI dashboard that consolidates transaction, merchant, and regional
data to answer these questions and support faster operational decisions.

### Core Business Questions
1. What is the month-over-month trend in transaction volume, and where are the drop-offs?
2. What is the overall transaction success rate, and what are the top reasons for failure?
3. What are the peak hours of transaction load (relevant for infrastructure planning)?
4. Which merchant categories and payment apps drive the most transaction value?
5. How does performance (volume, success rate) vary by region/zone?

---

## 🗂️ Project Structure

```
upi-payments-dashboard/
├── data/
│   ├── raw/                    # Raw generated data (with intentional data quality issues)
│   └── processed/              # Cleaned, Power-BI-ready CSVs
├── scripts/
│   ├── 01_generate_data.py     # Generates synthetic star-schema dataset
│   ├── 02_clean_data.py        # Cleans raw data, handles nulls/dupes/errors
│   └── 03_eda.py               # Exploratory analysis + summary charts
├── docs/
│   ├── images/                 # Chart exports & dashboard screenshots
│   └── cleaning_report.txt     # Auto-generated data cleaning log
├── dashboard/
│   └── upi_dashboard.pbix      # Power BI dashboard file (build using guide below)
├── requirements.txt
└── README.md
```

---

## 📊 Dataset

Since transaction-level UPI data is not publicly released (NPCI only publishes monthly
aggregates for privacy/regulatory reasons), this project uses a **synthetically generated
dataset** built with realistic distributions based on publicly known UPI trends (e.g.,
PhonePe/Google Pay market dominance, ~95-98% success rates, evening usage peaks, P2M vs
P2P split). The data is structured as a **star schema** — the same structure used in
real-world BI systems — with one fact table and four dimension tables.

| Table | Type | Description |
|---|---|---|
| `fact_transactions` | Fact | 20,000 transactions: amount, status, timestamp, app, type |
| `dim_banks` | Dimension | 10 major Indian banks |
| `dim_merchants` | Dimension | 50 merchants across 10 categories |
| `dim_regions` | Dimension | 15 Indian states grouped into 5 zones |
| `dim_date` | Dimension | Calendar table (2024, day/month/weekend flags) |

**Fact table columns:** `transaction_id`, `timestamp`, `date_id`, `sender_bank_id`,
`receiver_bank_id`, `payer_app`, `merchant_id`, `region_id`, `transaction_type` (P2P/P2M),
`amount`, `device_type`, `status` (Success/Failed/Pending), `failure_reason`,
`hour_of_day`, `is_success`, `is_failed`

### Data Cleaning Applied
The raw data intentionally includes realistic issues, cleaned in `02_clean_data.py`:
- Inconsistent text casing in `payer_app` (e.g., "PHONEPE" → "PhonePe")
- ~100 duplicate transaction rows (removed via `transaction_id`)
- ~185 missing `device_type` values (filled as `"Unknown"` rather than dropped)
- ~37 negative amount entry errors (corrected via absolute value)
- Full log saved to `docs/cleaning_report.txt`

---

## 🛠️ How to Reproduce

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd upi-payments-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate the raw synthetic dataset
python scripts/01_generate_data.py

# 4. Clean the data
python scripts/02_clean_data.py

# 5. (Optional) Run EDA to regenerate summary charts
python scripts/03_eda.py
```

This produces cleaned CSVs in `data/processed/` — these are the files you import into Power BI.

---

## 📈 Building the Power BI Dashboard (Step-by-Step)

### Step 1: Import Data
1. Open Power BI Desktop → **Get Data → Text/CSV**
2. Import all 5 files from `data/processed/`: `fact_transactions.csv`, `dim_banks.csv`,
   `dim_merchants.csv`, `dim_regions.csv`, `dim_date.csv`
3. Click **Transform Data** to confirm data types (Power BI should auto-detect most; set
   `date` in `dim_date` explicitly to Date type, and `timestamp` in fact table to Date/Time)

### Step 2: Build the Data Model (Star Schema Relationships)
Go to **Model view** and create these relationships (drag field to field):

| From | To | Cardinality |
|---|---|---|
| `fact_transactions[date_id]` | `dim_date[date_id]` | Many-to-One |
| `fact_transactions[merchant_id]` | `dim_merchants[merchant_id]` | Many-to-One |
| `fact_transactions[region_id]` | `dim_regions[region_id]` | Many-to-One |
| `fact_transactions[sender_bank_id]` | `dim_banks[bank_id]` | Many-to-One |

> This star schema is the key thing that separates a "fresher" dashboard from a
> professional one — it's worth the extra 10 minutes to set up properly.

### Step 3: Create DAX Measures
In **fact_transactions**, go to **Modeling → New Measure** and add these:

```dax
Total Transactions = COUNTROWS(fact_transactions)

Total Transaction Value = SUM(fact_transactions[amount])

Success Rate = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_transactions), fact_transactions[status] = "SUCCESS"),
    COUNTROWS(fact_transactions)
)

Failure Rate = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_transactions), fact_transactions[status] = "FAILED"),
    COUNTROWS(fact_transactions)
)

Failed Transactions = 
CALCULATE(COUNTROWS(fact_transactions), fact_transactions[status] = "FAILED")

Avg Transaction Value = AVERAGE(fact_transactions[amount])

MoM Transaction Growth % = 
VAR CurrentMonth = [Total Transactions]
VAR PreviousMonth = 
    CALCULATE(
        [Total Transactions],
        DATEADD(dim_date[date], -1, MONTH)
    )
RETURN
    DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth)
```

### Step 4: Build the Report Pages
Create 3 pages:

**Page 1 — Executive Overview**
- KPI cards: Total Transactions, Total Value, Success Rate, Failed Transactions
- Line chart: Monthly transaction volume trend (use `MoM Transaction Growth %` as a tooltip)
- Donut chart: Status distribution (Success/Failed/Pending)

**Page 2 — Failure & Risk Analysis**
- Bar chart: Failed transactions by `failure_reason`
- Line/area chart: Failure rate trend by month
- Table: Failure rate by `payer_app` (identify which app has more failures)

**Page 3 — Merchant & Regional Performance**
- Bar chart: Total transaction value by `merchant_category`
- Map or bar chart: Transaction volume by `zone`/`state`
- Heatmap-style matrix: Transaction volume by hour × day of week (peak load analysis)

### Step 5: Add Slicers/Filters
Add slicers for `payer_app`, `zone`, `transaction_type`, and a date range slicer using
`dim_date[date]` — apply these to all pages via **Sync Slicers**.

### Step 6: Export & Save
Save the file as `dashboard/upi_dashboard.pbix`. Export a few screenshots to
`docs/images/` for your README/resume/LinkedIn post.

---

## 💡 Key Insights (from EDA — see `scripts/03_eda.py`)

- **Overall success rate: ~95.7%** — in line with real-world UPI benchmarks (NPCI reports 95-99%)
- **Top failure reason:** Bank server downtime — suggests failures are more infrastructure-driven than user error
- **Peak transaction hour: 7-8 PM**, consistent with evening bill payments/shopping behavior — relevant for server capacity planning
- **Healthcare and E-commerce** are the highest-value merchant categories
- **North zone** leads in transaction volume, but **Central zone** has the highest success rate

*(Run `python scripts/03_eda.py` to regenerate these numbers and charts from scratch.)*

---

## 🧰 Tech Stack

- **Python** (pandas, numpy, matplotlib) — data generation, cleaning, EDA
- **Power BI Desktop** — data modeling (star schema), DAX measures, dashboard/visuals
- **DAX** — for KPI measures and time-intelligence calculations

---

## 🚀 Possible Extensions
- Swap synthetic data for a real dataset (e.g., Kaggle "Lending Club" for the credit angle, or NPCI's published aggregate CSVs for a real benchmark comparison)
- Add a Python anomaly-detection script to flag unusual failure spikes
- Publish the report to Power BI Service and embed a live link in this README

---

## 👤 Author
[Your Name] — Business Economics student | [LinkedIn] | [Portfolio]
