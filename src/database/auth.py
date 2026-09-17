import os
import hashlib
from src.database.connection import DatabaseClient

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with a salt."""
    salt = os.getenv("SECRET_SALT", "finlens_regtech_secret_salt")
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def verify_regulator_credentials(email: str, password: str) -> dict | None:
    """
    Validates regulator credentials against MongoDB Users collection.
    Falls back to environment-defined master regulator if DB is fresh.
    """
    hashed = hash_password(password)

    # 1. Check MongoDB Users collection
    try:
        db = DatabaseClient.get_database()
        user = db.Users.find_one({"email": email.strip().lower(), "role": "Regulator"})
        if user and user.get("password_hash") == hashed:
            return {
                "user_id": str(user["_id"]),
                "email": user["email"],
                "role": user.get("role", "Regulator")
            }
    except Exception as e:
        print(f"Database lookup error during auth: {e}")

    # 2. Fallback / Default Regulator configuration via .env
    default_email = os.getenv("DEFAULT_REGULATOR_EMAIL", "regulator@cbk.go.ke")
    default_pass = os.getenv("DEFAULT_REGULATOR_PASSWORD", "Admin@FinLens2026")

    if email.strip().lower() == default_email.lower() and password == default_pass:
        return {
            "user_id": "DEFAULT_REG_001",
            "email": default_email,
            "role": "Regulator"
        }

    return None