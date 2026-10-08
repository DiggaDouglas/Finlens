import os
import bcrypt
import secrets
from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
from src.database.connection import DatabaseClient

SESSION_TIMEOUT_MINUTES = 30

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Verifies a password against the stored bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def log_audit_event(action: str, email: str, status: str, details: str = ""):
    """Appends an immutable entry to the AuditLogs collection."""
    try:
        db = DatabaseClient.get_database()
        db.AuditLogs.insert_one({
            "action": action,
            "user_email": email.strip().lower(),
            "status": status,
            "details": details,
            "timestamp": datetime.now(timezone.utc)
        })
    except Exception as e:
        print(f"Failed to record audit log: {e}")

def verify_credentials(email: str, password: str) -> dict | None:
    norm_email = email.strip().lower()
    try:
        db = DatabaseClient.get_database()
        user = db.Users.find_one({"email": norm_email})
        
        if user and check_password(password, user.get("password_hash", "")):
            session_token = secrets.token_hex(32)
            now = datetime.now(timezone.utc)
            
            db.Users.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "last_login": now,
                    "session_token": session_token,
                    "last_activity": now
                }}
            )
            log_audit_event("USER_LOGIN", norm_email, "SUCCESS")
            return {
                "user_id": str(user["_id"]),
                "email": user["email"],
                "role": user.get("role", "Regulator"),
                "token": session_token,
                "must_change_password": user.get("must_change_password", False)
            }
        
        log_audit_event("USER_LOGIN", norm_email, "FAILED", "Invalid credentials")
    except Exception as e:
        log_audit_event("USER_LOGIN", norm_email, "ERROR", str(e))
    return None

def validate_active_session(email: str, token: str) -> bool:
    """Validates token presence, single-session integrity, and timeout limits."""
    try:
        db = DatabaseClient.get_database()
        user = db.Users.find_one({"email": email.strip().lower(), "session_token": token})
        
        if not user:
            return False
            
        last_activity = user.get("last_activity", user.get("last_login"))
        if not last_activity:
            return False

        # Ensure last_activity is timezone-aware (MongoDB returns naive UTC by default)
        if last_activity.tzinfo is None:
            last_activity = last_activity.replace(tzinfo=timezone.utc)
            
        now = datetime.now(timezone.utc)
        
        if now - last_activity > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            terminate_session(email, token, reason="TIMEOUT")
            return False
            
        # Refresh last activity timestamp
        db.Users.update_one({"_id": user["_id"]}, {"$set": {"last_activity": now}})
        return True
    except Exception as e:
        print(f"Session validation error: {e}")
        return False

def terminate_session(email: str, token: str, reason: str = "LOGOUT"):
    try:
        db = DatabaseClient.get_database()
        db.Users.update_one(
            {"email": email.strip().lower(), "session_token": token},
            {"$unset": {"session_token": "", "last_activity": ""}}
        )
        log_audit_event("USER_LOGOUT", email, "SUCCESS", f"Reason: {reason}")
    except Exception as e:
        print(f"Error terminating session: {e}")

def update_user_password(email: str, new_password: str) -> bool:
    """Updates password upon initial login and revokes tokens."""
    norm_email = email.strip().lower()
    try:
        db = DatabaseClient.get_database()
        new_hash = hash_password(new_password)
        db.Users.update_one(
            {"email": norm_email},
            {
                "$set": {
                    "password_hash": new_hash,
                    "must_change_password": False,
                    "password_updated_at": datetime.now(timezone.utc)
                },
                "$unset": {"session_token": ""}
            }
        )
        log_audit_event("PASSWORD_CHANGE", norm_email, "SUCCESS")
        return True
    except Exception as e:
        log_audit_event("PASSWORD_CHANGE", norm_email, "FAILED", str(e))
        return False

# --- Admin CRUD Operations ---

def get_all_users() -> list:
    db = DatabaseClient.get_database()
    users = list(db.Users.find({}, {"password_hash": 0, "session_token": 0}))
    for u in users:
        u["_id"] = str(u["_id"])
    return users

def update_user_details(user_id: str, new_email: str, new_role: str, admin_email: str) -> bool:
    try:
        db = DatabaseClient.get_database()
        db.Users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"email": new_email.strip().lower(), "role": new_role}}
        )
        log_audit_event("ADMIN_USER_UPDATE", admin_email, "SUCCESS", f"Updated user {user_id} to {new_email} ({new_role})")
        return True
    except Exception as e:
        log_audit_event("ADMIN_USER_UPDATE", admin_email, "FAILED", str(e))
        return False

def admin_set_password(user_id: str, new_password: str, admin_email: str) -> bool:
    try:
        db = DatabaseClient.get_database()
        new_hash = hash_password(new_password)
        db.Users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "password_hash": new_hash,
                    "must_change_password": True,
                    "password_updated_at": datetime.now(timezone.utc)
                },
                "$unset": {"session_token": ""}
            }
        )
        log_audit_event("ADMIN_PASSWORD_RESET", admin_email, "SUCCESS", f"Reset password for user {user_id}")
        return True
    except Exception as e:
        log_audit_event("ADMIN_PASSWORD_RESET", admin_email, "FAILED", str(e))
        return False

def delete_user(user_id: str, target_email: str, admin_email: str) -> bool:
    try:
        db = DatabaseClient.get_database()
        db.Users.delete_one({"_id": ObjectId(user_id)})
        log_audit_event("ADMIN_USER_DELETE", admin_email, "SUCCESS", f"Deleted user {target_email}")
        return True
    except Exception as e:
        log_audit_event("ADMIN_USER_DELETE", admin_email, "FAILED", str(e))
        return False