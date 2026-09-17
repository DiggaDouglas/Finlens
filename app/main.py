import streamlit as st
from app.views.auth_view import render_login_view

st.set_page_config(
    page_title="FinLens | RegTech Intelligence",
    page_icon="🛡️",
    layout="wide"
)

# 1. Initialize Authentication Session State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

# 2. Gatekeeper: If not logged in, enforce login view
if not st.session_state["authenticated"]:
    render_login_view()
    st.stop()

# 3. Authenticated View: Regulator Workspace
with st.sidebar:
    st.markdown("### FinLens Auditor")
    st.write(f"Logged in as: **{st.session_state['user']['email']}**")
    st.caption(f"Role: {st.session_state['user']['role']}")
    
    if st.button("Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.rerun()

st.title("Digital Lending Compliance Dashboard")
st.success("Regulator session active. Document upload and risk audit views are accessible.")