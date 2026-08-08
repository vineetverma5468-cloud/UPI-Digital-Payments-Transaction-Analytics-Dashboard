# Power BI Visual Layout Guide

## Page 1 — Executive Overview
- Top row: 4 KPI cards
  - Total Transactions
  - Total Transaction Value
  - Success Rate
  - Failed Transactions
- Row 2 left: line chart for monthly trend
  - X-axis: `dim_date[date]` (month level)
  - Y-axis: `Total Transactions`
  - Tooltip: `MoM Transaction Growth %`
- Row 2 right: donut chart for status distribution
  - Legend: `fact_transactions[status]`
  - Values: `Total Transactions`
- Bottom row: two small cards or bar charts
  - Avg Transaction Value
  - Pending Transactions

## Page 2 — Failure & Risk Analysis
- Top left: bar chart
  - X-axis: `failure_reason`
  - Y-axis: `Failed Transactions`
- Top right: area chart
  - X-axis: `dim_date[month_name]`
  - Y-axis: `Failure Rate`
- Bottom full width: table or matrix
  - Rows: `payer_app`
  - Values: `Failed Transactions`, `Failure Rate`, `Total Transactions`

## Page 3 — Merchant & Regional Performance
- Top left: bar chart
  - X-axis: `merchant_category`
  - Y-axis: `Total Transaction Value`
- Top right: clustered bar chart
  - X-axis: `zone`
  - Y-axis: `Total Transactions`
- Bottom left: matrix
  - Rows: `hour_of_day`
  - Columns: `day_of_week`
  - Values: `Total Transactions`
- Bottom right: map or state-level bar chart
  - `state` vs. `Total Transactions`

## Filters and slicers
Add slicers for:
- `payer_app`
- `zone`
- `transaction_type`
- `dim_date[date]`

Sync those slicers across all pages.

## Styling
Use the provided theme file:
- `dashboard/upi_theme.json`

Set page background to light gray and use blue/green accent colors for KPIs and performance visuals.
