# utils/reports.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import os
import sqlite3
from datetime import datetime

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
        pdf.cell(38, 10, str(row.get("id", "")), border=1)
        pdf.cell(38, 10, str(row.get("product_id", "")), border=1)
        pdf.cell(38, 10, str(row.get("timestamp_in", ""))[:19], border=1)
        pdf.cell(38, 10, str(row.get("timestamp_out", ""))[:19], border=1)
        pdf.cell(38, 10, str(row.get("product_name", "")), border=1)
        pdf.cell(38, 10, str(row.get("batch_id", "")), border=1)
        pdf.cell(38, 10, str(row.get("cumulative_stock", "")), border=1)
        pdf.cell(38, 10, str(row.get("stock_in", "")), border=1)
        pdf.cell(38, 10, str(row.get("stock_out", "")), border=1)
        pdf.cell(38, 10, str(row.get("total_stock", "")), border=1)
        pdf.cell(38, 10, str(row.get("unit_price", "")), border=1)
        pdf.cell(38, 10, str(row.get("total_price", "")), border=1)
        pdf.cell(38, 10, str(row.get("cumulative_value", "")), border=1)
        pdf.cell(38, 10, str(row.get("expiration_date", "")), border=1)
        pdf.cell(38, 10, str(row.get("username", "")), border=1)
        pdf.cell(38, 10, str(row.get("business_id", "")), border=1)
        pdf.ln()
    pdf.cell(0, 10, txt="Thank you for using Inventory Manager!", ln=True, align='C')
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"invoice_{product_name}_{batch_id}.pdf")
    pdf.output(file_path)
    return file_path

# Remaining code (stock_movement_chart, inventory_log_view, show_product_summary, database_explorer) remains unchanged.
