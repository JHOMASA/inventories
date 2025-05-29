# utils/reports.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import os
import sqlite3
from datetime import datetime

def pdf_invoice_section(df):
    st.subheader("📄 Generate Invoice PDF")
    if not df.empty:
        selected_product = st.selectbox("Select Product", df["product_name"].unique())
        batch_df = df[df["product_name"] == selected_product]
        selected_batch = st.selectbox("Select Batch", batch_df["batch_id"].unique())
        data = batch_df[batch_df["batch_id"] == selected_batch]
        business_id = data["business_id"].iloc[0] if "business_id" in data.columns else "N/A"
        if st.button("📄 Generate PDF Invoice"):
            path = generate_invoice_pdf(data, selected_product, selected_batch, st.session_state.username, business_id)
            with open(path, "rb") as f:
                st.download_button("⬇ Download PDF", f, file_name=os.path.basename(path), mime="application/pdf")

def generate_invoice_pdf(df, product_name, batch_id, username, business_id):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt="INVENTORY INVOICE", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Business: {business_id} | User: {username}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Product: {product_name} | Batch: {batch_id}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)
    headers = ['id', 'product_id', 'timestamp_in', 'timestamp_out', 'product_name', 'batch_id', 'cumulative_stock', 'stock_in', 'stock_out', 'total_stock', 'unit_price', 'total_price', 'cumulative_value', 'expiration_date', 'username', 'business_id']
    for header in headers:
        pdf.cell(38, 10, header, border=1)
    pdf.ln()
    for _, row in df.iterrows():
        for header in headers:
            pdf.cell(38, 10, str(row.get(header, ""))[:19] if 'timestamp' in header else str(row.get(header, "")), border=1)
        pdf.ln()
    pdf.cell(0, 10, txt="Thank you for using Inventory Manager!", ln=True, align='C')
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"invoice_{product_name}_{batch_id}.pdf")
    pdf.output(file_path)
    return file_path

def stock_movement_chart(df):
    st.subheader("📈 Stock Movement Over Time")
    if df.empty:
        st.info("No inventory data to display.")
        return
    df['timestamp'] = pd.to_datetime(df['timestamp_in'].fillna(df['timestamp_out']), errors='coerce')
    selected_product = st.selectbox("Product for Movement Chart", df['product_name'].unique())
    filtered = df[df['product_name'] == selected_product]
    selected_batch = st.selectbox("Select Batch", ['All'] + list(filtered['batch_id'].unique()))
    if selected_batch != 'All':
        filtered = filtered[filtered['batch_id'] == selected_batch]
    filtered = filtered.sort_values("timestamp")
    filtered['net_stock'] = filtered['stock_in'] - filtered['stock_out']
    filtered['cumulative_stock'] = filtered['net_stock'].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered['timestamp'], y=filtered['stock_in'], mode='lines+markers', name='Stock In'))
    fig.add_trace(go.Scatter(x=filtered['timestamp'], y=filtered['stock_out'], mode='lines+markers', name='Stock Out'))
    fig.add_trace(go.Scatter(x=filtered['timestamp'], y=filtered['cumulative_stock'], mode='lines+markers', name='Cumulative Stock'))

    fig.update_layout(title=f"Stock Movement for {selected_product} - {selected_batch}", xaxis_title="Date", yaxis_title="Units")
    st.plotly_chart(fig, use_container_width=True)

def inventory_log_view(df):
    st.subheader("📋 Editable Inventory Log")

    df = df.sort_values(by=['product_name', 'batch_id', 'timestamp_in', 'timestamp_out'], ascending=True).reset_index(drop=True)
    df['cumulative_stock'] = 0
    df['cumulative_value'] = 0.0

    grouped = df.groupby(['product_name', 'batch_id'])

    for (product, batch), group in grouped:
        cumulative = 0
        for idx in group.index:
            stock_in = df.at[idx, 'stock_in'] or 0
            stock_out = df.at[idx, 'stock_out'] or 0
            unit_price = df.at[idx, 'unit_price'] or 0
            cumulative += stock_in - stock_out
            df.at[idx, 'cumulative_stock'] = cumulative
            df.at[idx, 'cumulative_value'] = cumulative * unit_price

    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    if st.button("💾 Save All Changes"):
        try:
            conn = sqlite3.connect("data/inventory.db")
            cursor = conn.cursor()

            for _, row in edited_df.iterrows():
                cursor.execute("""
                    UPDATE inventory SET
                        product_name = ?,
                        batch_id = ?,
                        stock_in = ?,
                        stock_out = ?,
                        total_stock = ?,
                        cumulative_stock = ?,
                        unit_price = ?,
                        quantity = ?,
                        total_price = ?,
                        total_units = ?,
                        expiration_date = ?
                    WHERE id = ?
                """, (
                    row["product_name"], row["batch_id"], row["stock_in"], row["stock_out"],
                    row["total_stock"], row.get("cumulative_stock", 0),
                    row["unit_price"], row["quantity"], row["total_price"],
                    row["total_units"], row["expiration_date"], row["id"]
                ))

            conn.commit()
            conn.close()
            st.success("✅ All changes saved successfully.")
        except Exception as e:
            st.error(f"❌ Error saving changes: {e}")

    st.download_button(
        "⬇ Download Log CSV",
        edited_df.to_csv(index=False).encode(),
        "inventory_log.csv",
        "text/csv"
    )

def database_explorer():
    st.subheader("🧮 Database Viewer")
    conn = sqlite3.connect("data/inventory.db")
    table_choice = st.selectbox("Select Table to View", ["inventory", "users"])
    df = pd.read_sql(f"SELECT * FROM {table_choice}", conn)
    st.dataframe(df, use_container_width=True)
    st.download_button(
        f"⬇ Download {table_choice}.csv",
        df.to_csv(index=False).encode(),
        f"{table_choice}.csv",
        "text/csv"
    )
    conn.close()

def inventory_navigation(df):
    st.subheader("📦 Inventory Records Navigation")
    if df.empty:
        st.warning("No inventory data to display.")
        return

    df = df.sort_values(by=['product_name', 'batch_id', 'timestamp_in'], ascending=True)
    grouped = df.groupby(['product_id', 'product_name', 'batch_id'])

    for (prod_id, prod_name, batch_id), group in grouped:
        st.markdown(f"### 🏷️ Product: {prod_name} | Batch: {batch_id} | ID: {prod_id}")
        st.dataframe(group, use_container_width=True)
        st.markdown("---")



.
