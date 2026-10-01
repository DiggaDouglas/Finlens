import streamlit as st
from src.database.auth import update_user_password

def render_reset_password_view():
    st.markdown("<h2 style='text-align: center;'>🔒 Mandatory Password Reset</h2>", unsafe_allow_html=True)
    st.info("You are using a temporary credential. Please create a permanent password to proceed.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("reset_form"):
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            submit = st.form_submit_button("Update Password & Proceed to Login", use_container_width=True)
            
            if submit:
                if len(new_password) < 8:
                    st.error("Password must be at least 8 characters long.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    user_email = st.session_state["user"]["email"]
                    if update_user_password(user_email, new_password):
                        # Cleanly terminate the authenticated temporary state and route to login
                        st.session_state["authenticated"] = False
                        st.session_state["user"] = None
                        st.session_state["password_reset_success"] = True
                        st.rerun()
                    else:
                        st.error("An error occurred while updating your password.")