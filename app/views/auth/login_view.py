import streamlit as st
import time
from src.database.auth import verify_credentials

def render_login_view():
    st.markdown("<h2 style='text-align: center;'>🛡️ FinLens Portal Login</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Automated Compliance & Risk Audit for Kenyan Digital Credit Providers</p>", unsafe_allow_html=True)
    
    # Inform user if redirected from a completed password reset
    if st.session_state.pop("password_reset_success", False):
        st.success("Password successfully configured! Please log in with your new credentials.")

    if "login_attempts" not in st.session_state:
        st.session_state["login_attempts"] = 0
    if "lockout_until" not in st.session_state:
        st.session_state["lockout_until"] = 0

    # Rate limiting: 30-second lockout gate
    if time.time() < st.session_state["lockout_until"]:
        remaining = int(st.session_state["lockout_until"] - time.time())
        st.error(f"Access temporarily suspended due to repeated failures. Retry in {remaining} seconds.")
        st.stop()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Sign In")
            email = st.text_input("Official Email", placeholder="regulator@cbk.go.ke")
            password = st.text_input("Password", type="password", placeholder="••••••••••••")
            submit = st.form_submit_button("Authenticate Access", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.warning("Please enter your credentials.")
                    return
                
                # Check strike limit
                if st.session_state["login_attempts"] >= 3:
                    st.session_state["lockout_until"] = time.time() + 30  # 30-second lockout
                    st.session_state["login_attempts"] = 0
                    st.error("Too many failed attempts. Locked out for 30 seconds.")
                    st.rerun()

                auth_result = verify_credentials(email, password)
                if auth_result:
                    st.session_state["login_attempts"] = 0
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = auth_result
                    st.session_state["api_key"] = auth_result["token"]
                    st.rerun()
                else:
                    st.session_state["login_attempts"] += 1
                    left = 3 - st.session_state["login_attempts"]
                    st.error(f"Invalid credentials. Attempts remaining: {left}")