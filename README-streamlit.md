# Streamlit Dashboard Guide

This project is built for a clean, professional web dashboard experience using Streamlit.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Recommended workflow

1. Generate the synthetic dataset
2. Clean the raw data
3. Run the EDA summary script
4. Launch the Streamlit dashboard

## Commands

```bash
python scripts/01_generate_data.py
python scripts/02_clean_data.py
python scripts/03_eda.py
streamlit run app.py
```

## Deployment

This dashboard is suitable for:
- Streamlit Community Cloud
- Render
- Railway
- Hugging Face Spaces

## Project purpose

The dashboard focuses on UPI transaction analytics, operational health, failure analysis, merchant trends, and regional performance using a realistic synthetic dataset.
