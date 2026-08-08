from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "processed"

st.set_page_config(page_title="UPI Transaction Analytics Dashboard", page_icon="💸", layout="wide")
st.title("UPI / Digital Payments Transaction Analytics Dashboard")

@st.cache_data
def load_data():
    fact = pd.read_csv(DATA_DIR / "fact_transactions.csv")
    merchants = pd.read_csv(DATA_DIR / "dim_merchants.csv")
    regions = pd.read_csv(DATA_DIR / "dim_regions.csv")
    dates = pd.read_csv(DATA_DIR / "dim_date.csv")

    merged = fact.merge(merchants, on="merchant_id", how="left")
    merged = merged.merge(regions, on="region_id", how="left")
    merged = merged.merge(dates, left_on="date_id", right_on="date_id", how="left")
    return merged


data = load_data()

status_counts = data["status"].value_counts().rename_axis("status").reset_index(name="count")

# KPI cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Transactions", f"{len(data):,}")
col2.metric("Transaction Value", f"₹{data['amount'].sum():,.2f}")
col3.metric("Success Rate", f"{(data['is_success'].mean() * 100):.2f}%")
col4.metric("Failed Transactions", f"{data['is_failed'].sum():,}")

# Filters
st.sidebar.header("Filters")
selected_app = st.sidebar.multiselect("Payer App", sorted(data["payer_app"].dropna().unique()))
selected_zone = st.sidebar.multiselect("Zone", sorted(data["zone"].dropna().unique()))
selected_type = st.sidebar.multiselect("Transaction Type", sorted(data["transaction_type"].dropna().unique()))

if selected_app:
    data = data[data["payer_app"].isin(selected_app)]
if selected_zone:
    data = data[data["zone"].isin(selected_zone)]
if selected_type:
    data = data[data["transaction_type"].isin(selected_type)]

# Charts
chart_col1, chart_col2 = st.columns([2, 1])
with chart_col1:
    month_series = data.assign(month=pd.to_datetime(data["timestamp"]).dt.to_period("M").astype(str))
    monthly = month_series.groupby("month").size().reset_index(name="transactions")
    fig_line = px.line(monthly, x="month", y="transactions", markers=True, title="Monthly Transaction Volume")
    st.plotly_chart(fig_line, use_container_width=True)

with chart_col2:
    fig_pie = px.pie(status_counts, names="status", values="count", title="Transaction Status Mix")
    st.plotly_chart(fig_pie, use_container_width=True)

chart_col3, chart_col4 = st.columns(2)
with chart_col3:
    failure_reason = data[data["status"] == "Failed"]["failure_reason"].value_counts().reset_index()
    failure_reason.columns = ["failure_reason", "count"]
    fig_bar = px.bar(failure_reason, x="failure_reason", y="count", title="Failed Transactions by Reason")
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col4:
    merchant_value = data.groupby("merchant_category")["amount"].sum().reset_index().sort_values("amount", ascending=False)
    fig_merch = px.bar(merchant_value, x="merchant_category", y="amount", title="Value by Merchant Category")
    st.plotly_chart(fig_merch, use_container_width=True)

chart_col5, chart_col6 = st.columns(2)
with chart_col5:
    hourly = data.groupby("hour_of_day").size().reset_index(name="transactions")
    fig_hour = px.bar(hourly, x="hour_of_day", y="transactions", title="Transaction Load by Hour")
    st.plotly_chart(fig_hour, use_container_width=True)

with chart_col6:
    zone_volume = data.groupby("zone").size().reset_index(name="transactions")
    fig_zone = px.bar(zone_volume, x="zone", y="transactions", title="Volume by Zone")
    st.plotly_chart(fig_zone, use_container_width=True)

# Insights section
st.subheader("Key Insights")
insight_col1, insight_col2, insight_col3 = st.columns(3)
insight_col1.metric("Overall Success Rate", f"{(data['is_success'].mean() * 100):.2f}%")
insight_col2.metric("Peak Hour", f"{int(data['hour_of_day'].mode().iloc[0]):02d}:00")
insight_col3.metric("Top Zone", data.groupby("zone").size().idxmax())

# Data preview
st.subheader("Data Preview")
st.dataframe(data.head(10), use_container_width=True)
