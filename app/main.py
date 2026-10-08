import streamlit as st
from app.views.auth.login_view import render_login_view
from app.views.auth.reset_password_view import render_reset_password_view
from app.views.superadmin.user_management_view import render_admin_dashboard
from app.views.regulator.dashboard_view import render_regulator_dashboard
from src.database.auth import validate_active_session, terminate_session

st.set_page_config(
    page_title="FinLens | RegTech Intelligence",
    page_icon="🛡️",
    layout="wide"
)

# 1. State Initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

# 2. Unauthenticated Gatekeeper
if not st.session_state["authenticated"]:
    render_login_view()
    st.stop()

# 3. Session Security Check (Timeout & Active Token Verification)
user_data = st.session_state["user"]
if not validate_active_session(user_data["email"], user_data["token"]):
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.warning("Your session has expired. Please sign in again.")
    st.stop()

# 4. Mandatory Password Reset Enforcement
if user_data.get("must_change_password", False):
    render_reset_password_view()
    st.stop()

# 5. Global Sidebar & Server-Side Termination
# Replace the existing sidebar block in app/main.py with this:
with st.sidebar:
    st.markdown("## 🛡️ FinLens\nRegTech Intelligence")
    st.divider()
    
    # Mock navigation links for UI fidelity
    st.markdown(" **Dashboard**")
    st.markdown(" Lenders")
    st.markdown(" Documents")
    st.markdown(" Risk Analysis")
    st.markdown(" Reports")
    st.markdown(" Alerts")
    
    st.write("")
    st.write("")
    st.markdown("⚙️ Settings")
    st.markdown("👥 Users")
    
    st.divider()
    
    st.write(f"👤 **{user_data['email']}**")
    st.caption(f"Role: {user_data['role']}")
    
    if st.button("Logout", use_container_width=True):
        terminate_session(user_data["email"], user_data["token"])
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        if "api_key" in st.session_state:
            del st.session_state["api_key"]
        st.rerun()

# 6. Role-Based Routing
if user_data["role"] == "SuperAdmin":
    render_admin_dashboard()
elif user_data["role"] == "Regulator":
    render_regulator_dashboard()
else:
    st.error("Unauthorized access tier.")