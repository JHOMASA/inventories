# utils/dashboard.py
import streamlit as st
import pandas as pd

def show_dashboard(df):
    st.title("📊 Business Dashboard")
    col1, col2, col3 = st.columns(3)

    total_products = df['product_name'].nunique()
    total_value = df['total_price'].sum()
    upcoming_expiry = df[pd.to_datetime(df['expiration_date'], errors='coerce') < pd.Timestamp.now() + pd.Timedelta(days=7)].shape[0]

    col1.metric("📦 Total Products", total_products)
    col2.metric("💰 Inventory Value", f"${total_value:,.2f}")
    col3.metric("⚠️ Expiring Soon", upcoming_expiry)

    st.markdown("---")
