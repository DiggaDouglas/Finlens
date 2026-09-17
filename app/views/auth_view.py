
import sys
import os

# Add the project root to Python's path so it can find the 'app' and 'src' folders
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import streamlit as st
from src.database.auth import verify_regulator_credentials

def render_login_view():
    st.markdown("<h2 style='text-align: center;'>🛡️ FinLens Portal Login</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Automated Compliance & Risk Audit for Kenyan Digital Credit Providers</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("regulator_login_form"):
            st.subheader("Regulator Authentication")
            email = st.text_input("Official Email", placeholder="regulator@cbk.go.ke")
            password = st.text_input("Password", type="password", placeholder="••••••••••••")
            submit = st.form_submit_button("Authenticate Access", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.warning("Please supply both email and password.")
                    return

                auth_result = verify_regulator_credentials(email, password)
                if auth_result:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = auth_result
                    st.success("Identity verified. Redirecting to workspace...")
                    st.rerun()
                else:
                    st.error("Invalid credentials or unauthorized regulator account.")
