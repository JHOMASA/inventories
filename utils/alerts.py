# utils/alerts.py
import streamlit as st
import pandas as pd

def show_expiration_alerts(df):
    st.subheader("🔔 Expiration Alerts (Next 7 Days)")
    df["expiration_date"] = pd.to_datetime(df["expiration_date"], errors="coerce")
    today = pd.Timestamp.today()
    alerts = df[(df["expiration_date"].notna()) & (df["expiration_date"] <= today + pd.Timedelta(days=7))]
    if not alerts.empty:
        st.warning("⚠️ Items nearing expiration:")
        st.dataframe(alerts[["product_name", "batch_id", "expiration_date", "total_stock"]])
    else:
        st.success("✅ No items expiring soon.")

def show_low_stock_alerts(df):
    st.subheader("🚨 Low Stock Alerts (Below 10%)")
    if 'total_stock' in df.columns:
        grouped = df.groupby(['product_name', 'batch_id']).agg(
            latest_stock=('total_stock', 'last'),
            max_stock=('total_stock', 'max')
        ).reset_index()
        grouped['stock_percentage'] = (grouped['latest_stock'] / grouped['max_stock']) * 100
        low_stock = grouped[grouped['stock_percentage'] < 10]
        if not low_stock.empty:
            st.warning("⚠️ Low stock items:")
            st.dataframe(low_stock[['product_name', 'batch_id', 'latest_stock', 'max_stock', 'stock_percentage']])
        else:
            st.success("✅ Stock levels are sufficient.")
