import streamlit as st
import secrets
from datetime import datetime, timedelta, timezone
from src.database.connection import DatabaseClient
from src.database.auth import (
    hash_password, 
    log_audit_event, 
    get_all_users, 
    update_user_details, 
    admin_set_password, 
    delete_user
)

def render_admin_dashboard():
    st.title("SuperAdmin Platform Administration")
    admin_email = st.session_state["user"]["email"]

    tab_users, tab_create, tab_audit = st.tabs(["Manage Users", "Provision New User", "Audit Trail"])

    # TAB 1: User Management (Read, Update, Delete, Reset Password)
    with tab_users:
        st.subheader("Platform Accounts")
        users = get_all_users()
        
        if not users:
            st.info("No registered users found.")
        else:
            for u in users:
                user_id = u["_id"]
                email = u["email"]
                role = u.get("role", "Regulator")
                must_reset = u.get("must_change_password", False)
                created_at = u.get("created_at", "N/A")
                
                with st.expander(f"👤 {email} — **{role}**"):
                    col_info, col_actions = st.columns([2, 1])
                    
                    with col_info:
                        st.write(f"**User ID:** `{user_id}`")
                        st.write(f"**Account Status:** {' Password Reset Required' if must_reset else ' Active'}")
                        st.caption(f"Created: {created_at}")

                    with col_actions:
                        st.markdown("#### Actions")
                        
                        # --- 1. Edit User Details ---
                        with st.popover(" Edit Account"):
                            with st.form(f"edit_form_{user_id}"):
                                edit_email = st.text_input("Email", value=email)
                                edit_role = st.selectbox(
                                    "Role", 
                                    ["Regulator", "Analyst"], 
                                    index=0 if role == "Regulator" else 1
                                )
                                if st.form_submit_button("Save Changes"):
                                    if update_user_details(user_id, edit_email, edit_role, admin_email):
                                        st.success("User updated.")
                                        st.rerun()
                                    else:
                                        st.error("Failed to update.")

                        # --- 2. Change / Reset Password ---
                        with st.popover(" Reset Password"):
                            with st.form(f"reset_form_{user_id}"):
                                auto_gen = st.checkbox("Auto-generate password", value=True)
                                custom_pass = st.text_input("New Password", type="password", disabled=auto_gen)
                                if st.form_submit_button("Apply Reset"):
                                    new_pwd = secrets.token_urlsafe(10) if auto_gen else custom_pass
                                    if not new_pwd:
                                        st.error("Password cannot be empty.")
                                    elif admin_set_password(user_id, new_pwd, admin_email):
                                        st.session_state[f"temp_pwd_{user_id}"] = new_pwd
                                        st.rerun()

                        # Display new password in plain text if freshly reset
                        if f"temp_pwd_{user_id}" in st.session_state:
                            st.warning(f"New Password: `{st.session_state[f'temp_pwd_{user_id}']}`")
                            st.caption("Provide this credential to the user.")

                        # --- 3. Delete User ---
                        if email == admin_email:
                            st.caption("*(Current Account)*")
                        else:
                            with st.popover(" Delete User"):
                                st.write(f"Are you sure you want to permanently delete **{email}**?")
                                if st.button(f"Confirm Delete", key=f"del_btn_{user_id}", type="primary"):
                                    if delete_user(user_id, email, admin_email):
                                        st.success(f"User {email} deleted.")
                                        st.rerun()

    # TAB 2: Provision New User (Create)
    with tab_create:
        st.subheader("Provision New Account")
        with st.form("create_user_form"):
            new_email = st.text_input("Official Email", placeholder="officer@cbk.go.ke")
            new_role = st.selectbox("Assign Role", ["Regulator", "Analyst"])
            auto_generate = st.checkbox("Generate secure temporary password", value=True)
            custom_pass = st.text_input("Custom Password", type="password", disabled=auto_generate)
            
            submit = st.form_submit_button("Provision User")

            if submit:
                temp_pass = secrets.token_urlsafe(10) if auto_generate else custom_pass
                if not new_email or not temp_pass:
                    st.error("Email and password are required.")
                else:
                    try:
                        db = DatabaseClient.get_database()
                        norm_email = new_email.strip().lower()
                        if db.Users.find_one({"email": norm_email}):
                            st.error("An account with this email already exists.")
                        else:
                            db.Users.insert_one({
                                "email": norm_email,
                                "password_hash": hash_password(temp_pass),
                                "role": new_role,
                                "must_change_password": True,
                                "created_at": datetime.now(timezone.utc)
                            })
                            log_audit_event("USER_PROVISIONED", norm_email, "SUCCESS", f"Role: {new_role}")
                            st.success(f"Account successfully provisioned for **{norm_email}**.")
                            st.warning(f"Temporary Password: `{temp_pass}`")
                    except Exception as e:
                        st.error(f"Provisioning failed: {e}")

    # TAB 3: Audit Trail
    with tab_audit:
        st.subheader("System Security Audit Trail")
        try:
            db = DatabaseClient.get_database()
            logs = list(db.AuditLogs.find({}).sort("timestamp", -1).limit(50))
            for l in logs:
                l["_id"] = str(l["_id"])
            st.dataframe(logs, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to fetch audit records: {e}")