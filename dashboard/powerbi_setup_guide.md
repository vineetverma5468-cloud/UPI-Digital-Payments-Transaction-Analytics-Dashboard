# Power BI Dashboard Setup Guide

## 1. Import the cleaned data
Open Power BI Desktop and use:
- Home > Get Data > Text/CSV
- Import these files from `data/processed/`:
  - `fact_transactions.csv`
  - `dim_banks.csv`
  - `dim_merchants.csv`
  - `dim_regions.csv`
  - `dim_date.csv`

## 2. Set data types
In the Power Query editor, confirm these data types:
- `fact_transactions[date_id]` -> Whole Number
- `fact_transactions[timestamp]` -> Date/Time
- `dim_date[date]` -> Date
- `fact_transactions[amount]` -> Decimal Number
- `fact_transactions[hour_of_day]` -> Whole Number

## 3. Create the star schema
In Model view create these relationships:
- `fact_transactions[date_id]` -> `dim_date[date_id]` (many-to-one)
- `fact_transactions[merchant_id]` -> `dim_merchants[merchant_id]` (many-to-one)
- `fact_transactions[region_id]` -> `dim_regions[region_id]` (many-to-one)
- `fact_transactions[sender_bank_id]` -> `dim_banks[bank_id]` (many-to-one)

## 4. Add the DAX measures
Paste the contents from `dashboard/upi_dashboard_measures.dax` into the model.

## 5. Build report pages
### Page 1: Executive Overview
- KPI cards: Total Transactions, Total Transaction Value, Success Rate, Failed Transactions
- Line chart: `dim_date[date]` on X-axis, `Total Transactions` on Y-axis
- Donut chart: `fact_transactions[status]`
- Tooltip: `MoM Transaction Growth %`

### Page 2: Failure & Risk Analysis
- Bar chart: `failure_reason` vs. `Failed Transactions`
- Area/line chart: month trend of `Failure Rate`
- Matrix or table: `payer_app` vs. `Failure Rate`

### Page 3: Merchant & Regional Performance
- Bar chart: `merchant_category` vs. `Total Transaction Value`
- Bar/map: `zone` or `state` vs. `Total Transactions`
- Matrix: `hour_of_day` x `day_of_week` with `Total Transactions`

## 6. Add slicers
Use slicers for:
- `payer_app`
- `zone`
- `transaction_type`
- `dim_date[date]`

Enable Sync Slicers across all pages.

## 7. Final save
Save the file as:
- `dashboard/upi_dashboard.pbix`

## 8. Optional export
Export screenshots to `docs/images/`.
