import streamlit as st
from utils.auth import login_section, register_section
from utils.dashboard import show_dashboard
from utils.database import create_tables, get_user_inventory
from utils.alerts import show_expiration_alerts, show_low_stock_alerts
from utils.reports import pdf_invoice_section, stock_movement_chart, inventory_log_view, database_explorer, inventory_navigation

# ---------- INITIAL SETUP ----------
st.set_page_config(page_title="📦 Inventory Manager", layout="wide")
create_tables()

# ---------- SESSION INIT ----------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ---------- LOGIN / REGISTER ----------
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Register"])
    with tab1:
        login_section()
    with tab2:
        register_section()
    st.stop()

# ---------- MAIN DASHBOARD ----------
st.sidebar.success(f"Logged in as {st.session_state.username}")
menu = st.sidebar.radio("📂 Navigate", ["Dashboard", "Add Inventory", "Reports", "Alerts", "Database"])
df = get_user_inventory(st.session_state.username)

if menu == "Dashboard":
    show_dashboard(df)

elif menu == "Add Inventory":
    from utils.inventory import add_inventory_form
    add_inventory_form(df)

elif menu == "Reports":
    pdf_invoice_section(df)
    stock_movement_chart(df)
    inventory_log_view(df)

elif menu == "Alerts":
    show_expiration_alerts(df)
    show_low_stock_alerts(df)

elif menu == "Database":
    database_explorer()
