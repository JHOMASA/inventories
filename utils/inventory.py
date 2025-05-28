import streamlit as st
from datetime import datetime
import pytz
from utils.database import insert_inventory_record

lima_tz = pytz.timezone("America/Lima")

def add_inventory_form(df):
    st.subheader("➕ Add Inventory Movement")
    with st.form("add_stock_form"):
        product_name = st.text_input("Product Name")
        product_id = st.text_input("Product ID")
        batch_id = st.text_input("Batch ID")
        stock_in = st.number_input("Stock In", min_value=0, value=0)
        stock_out = st.number_input("Stock Out", min_value=0, value=0)
        unit_price = st.number_input("Unit Price", min_value=0.0, format="%.2f")
        quantity = st.number_input("Quantity", min_value=1, value=1)

        requires_expiration = st.radio("Expiration Date Required?", ("Yes", "No"))
        expiration_date = st.date_input("Expiration Date") if requires_expiration == "Yes" else None

        submitted = st.form_submit_button("✅ Record Entry")
        if submitted:
            now = datetime.now(lima_tz)
            total_units = stock_in - stock_out
            total_price = unit_price * quantity
            batch_df = df[(df["product_name"] == product_name) & (df["batch_id"] == batch_id)]
            prev_stock = batch_df["total_stock"].iloc[-1] if not batch_df.empty else 0
            new_stock = prev_stock + total_units

            data = {
                "timestamp_in": now.strftime("%Y-%m-%d %H:%M:%S") if stock_in > 0 else None,
                "timestamp_out": now.strftime("%Y-%m-%d %H:%M:%S") if stock_out > 0 else None,
                "product_id": product_id,
                "product_name": product_name,
                "batch_id": batch_id,
                "stock_in": stock_in,
                "stock_out": stock_out,
                "total_stock": new_stock,
                "unit_price": unit_price,
                "quantity": quantity,
                "total_price": total_price,
                "total_units": total_units,
                "expiration_date": expiration_date.strftime("%Y-%m-%d") if expiration_date else None,
                "username": st.session_state.username,
                "business_id": "biz01"  # Update to use session or profile later
            }

            insert_inventory_record(data)
            st.success(f"📦 Entry for {product_name} (Batch {batch_id}) saved.")
            st.rerun()
