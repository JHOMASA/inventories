import streamlit as st
from utils.database import validate_login, add_user


def login_section():
    st.subheader("🔐 Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        if validate_login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome, {username}!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")


def register_section():
    st.subheader("🆕 Register")
    new_user = st.text_input("New Username", key="reg_user")
    new_pass = st.text_input("New Password", type="password", key="reg_pass")
    business_id = st.text_input("Business ID (Company Code)", key="reg_biz")
    if st.button("Register"):
        if new_user and new_pass and business_id:
            add_user(new_user, new_pass, business_id)
            st.success("✅ Account created! You can now login.")
        else:
            st.warning("Please fill in all fields.")
