# UPI Transaction Analytics Dashboard

A professional, git-ready analytics dashboard for digital payments built with Python and Streamlit. The project uses a realistic public-data-style UPI transaction schema, cleans the data, and presents operational insights through an interactive dashboard that can be run locally or deployed to a cloud-hosting service.

![Status](https://img.shields.io/badge/status-live-brightgreen)
![Stack](https://img.shields.io/badge/stack-Python%20%2B%20Streamlit%20%2B%20Plotly-blue)
![Data](https://img.shields.io/badge/data-public%20style%20UPI%20dataset-orange)

---

## Overview

This project analyzes a realistic public-data-style UPI transaction dataset to track:
- transaction volume and value trends
- payment success and failure patterns
- peak load times by hour of day
- merchant-category performance
- regional distribution and zone performance
- failure reasons and operational risk drivers

The application is designed for portfolio presentation, GitHub hosting, and easy deployment with a clean production-style workflow.

---

## Business Questions

1. What is the trend in monthly transaction volume and value?
2. What is the success rate and where are the failures concentrated?
3. Which merchant categories generate the highest payment value?
4. Which regions and zones drive the most transaction activity?
5. What are the peak load hours for infrastructure planning?
6. Which failure reasons require operational attention?

---

## Project Structure

```text
UPI-Digital-Payments-Transaction-Analytics-Dashboard/
├── app.py                      # Streamlit dashboard application
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview and setup instructions
├── README-streamlit.md         # Streamlit-specific quick start
├── .gitignore
├── data/
│   ├── raw/                    # Raw generated data with quality issues
│   └── processed/              # Cleaned CSVs for analysis and visualization
├── docs/
│   ├── cleaning_report.txt     # Data cleaning summary
│   └── images/                 # Generated EDA charts
├── scripts/
│   ├── 01_generate_data.py     # Realistic public-style data generation
│   ├── 02_clean_data.py        # Cleaning logic and validation
│   └── 03_eda.py               # Summary charts and insights
└── .venv/ or environment setup
```

---

## Data Model

The project uses a realistic public-data-style star schema:

- fact_transactions
- dim_banks
- dim_merchants
- dim_regions
- dim_date

Key fields include:
- transaction_id
- timestamp
- date_id
- payer_app
- merchant_id
- region_id
- transaction_type
- amount
- status
- failure_reason
- hour_of_day

---

## Data Cleaning

The cleaning pipeline handles:
- duplicate transactions
- inconsistent app naming
- missing device types
- negative or invalid amounts
- missing failure reasons
- timestamp normalization

The full cleaning log is saved to [docs/cleaning_report.txt](docs/cleaning_report.txt).

---

## Run the Project

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate data

```bash
python scripts/01_generate_data.py
```

### 3. Clean data

```bash
python scripts/02_clean_data.py
```

### 4. Run EDA charts

```bash
python scripts/03_eda.py
```

### 5. Launch dashboard

```bash
streamlit run app.py
```

Then open the local URL displayed in the terminal, typically:

```text
http://localhost:8501
```

---

## Portfolio-Ready Features

- interactive dashboard built in Streamlit
- real-time filtering by app, zone, and transaction type
- KPI cards for performance monitoring
- Plotly visualizations for transaction trends and risk analysis
- clean repository layout suitable for GitHub and deployment

---

## Tech Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Plotly
- Streamlit

---

## Author

Vineet Verma

---

## Deployment Options

This project is ready for deployment on:
- Streamlit Community Cloud
- Render
- Hugging Face Spaces
- Railway
- any standard Python hosting platform

