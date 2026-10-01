import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from bson.objectid import ObjectId
from src.database.auth import (
    hash_password,
    check_password,
    verify_credentials,
    validate_active_session,
    terminate_session,
    update_user_password,
    admin_set_password,
    delete_user,
    SESSION_TIMEOUT_MINUTES
)


# --- 1. Cryptographic Hashing Tests ---

def test_hash_password_generates_valid_bcrypt():
    password = "SuperSecurePassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")


def test_check_password_verification():
    password = "FinLens@CBK2026"
    hashed = hash_password(password)
    assert check_password(password, hashed) is True
    assert check_password("WrongPassword!", hashed) is False


# --- 2. Credential Verification & Authentication Tests ---

@patch("src.database.auth.DatabaseClient.get_database")
def test_verify_credentials_success(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    
    raw_pass = "ValidPass123"
    hashed_pass = hash_password(raw_pass)
    fake_user_id = ObjectId()
    
    mock_db.Users.find_one.return_value = {
        "_id": fake_user_id,
        "email": "regulator@cbk.go.ke",
        "password_hash": hashed_pass,
        "role": "Regulator",
        "must_change_password": False
    }
    
    result = verify_credentials("regulator@cbk.go.ke", raw_pass)
    
    assert result is not None
    assert result["email"] == "regulator@cbk.go.ke"
    assert result["role"] == "Regulator"
    assert len(result["token"]) == 64  # secrets.token_hex(32) produces a 64-char string
    assert result["must_change_password"] is False
    
    # Verify DB state was updated with session and login timestamp
    mock_db.Users.update_one.assert_called_once()
    mock_db.AuditLogs.insert_one.assert_called_once()


@patch("src.database.auth.DatabaseClient.get_database")
def test_verify_credentials_invalid_password(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    
    mock_db.Users.find_one.return_value = {
        "_id": ObjectId(),
        "email": "regulator@cbk.go.ke",
        "password_hash": hash_password("CorrectPassword"),
        "role": "Regulator"
    }
    
    result = verify_credentials("regulator@cbk.go.ke", "WrongPassword")
    assert result is None


@patch("src.database.auth.DatabaseClient.get_database")
def test_verify_credentials_user_not_found(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_db.Users.find_one.return_value = None
    
    result = verify_credentials("nonexistent@cbk.go.ke", "Password123")
    assert result is None


# --- 3. Session Lifecycle & Timeout Tests ---

@patch("src.database.auth.DatabaseClient.get_database")
def test_validate_active_session_valid(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    fake_id = ObjectId()
    
    # Active within the timeout window
    mock_db.Users.find_one.return_value = {
        "_id": fake_id,
        "email": "officer@cbk.go.ke",
        "session_token": "valid_token_123",
        "last_activity": datetime.now(timezone.utc) - timedelta(minutes=5)
    }
    
    is_valid = validate_active_session("officer@cbk.go.ke", "valid_token_123")
    assert is_valid is True
    # Activity timestamp should have refreshed
    mock_db.Users.update_one.assert_called_once()


@patch("src.database.auth.terminate_session")
@patch("src.database.auth.DatabaseClient.get_database")
def test_validate_active_session_expired_timeout(mock_get_db, mock_terminate):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    
    # Inactive past the timeout limit
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=SESSION_TIMEOUT_MINUTES + 5)
    mock_db.Users.find_one.return_value = {
        "_id": ObjectId(),
        "email": "officer@cbk.go.ke",
        "session_token": "expired_token_123",
        "last_activity": expired_time
    }
    
    is_valid = validate_active_session("officer@cbk.go.ke", "expired_token_123")
    assert is_valid is False
    mock_terminate.assert_called_once_with("officer@cbk.go.ke", "expired_token_123", reason="TIMEOUT")


@patch("src.database.auth.DatabaseClient.get_database")
def test_terminate_session_revokes_token(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    
    terminate_session("regulator@cbk.go.ke", "active_token_xyz")
    
    # Must unset session_token and last_activity
    mock_db.Users.update_one.assert_called_once_with(
        {"email": "regulator@cbk.go.ke", "session_token": "active_token_xyz"},
        {"$unset": {"session_token": "", "last_activity": ""}}
    )


# --- 4. Password Modification & Reset Tests ---

@patch("src.database.auth.DatabaseClient.get_database")
def test_update_user_password_success(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    
    success = update_user_password("user@cbk.go.ke", "NewStrongPassword2026!")
    assert success is True
    
    # Must update password hash, toggle must_change_password to False, and revoke active token
    called_args = mock_db.Users.update_one.call_args[0]
    update_doc = called_args[1]
    
    assert update_doc["$set"]["must_change_password"] is False
    assert "$unset" in update_doc and "session_token" in update_doc["$unset"]


# --- 5. SuperAdmin Administrative Operations ---

@patch("src.database.auth.DatabaseClient.get_database")
def test_admin_set_password_forces_reset_flag(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    fake_user_id = str(ObjectId())
    
    success = admin_set_password(fake_user_id, "TempAdminAssigned123", "admin@finlens.go.ke")
    assert success is True
    
    called_args = mock_db.Users.update_one.call_args[0]
    update_doc = called_args[1]
    
    # Flag must be True so user is forced to change credentials upon login
    assert update_doc["$set"]["must_change_password"] is True


@patch("src.database.auth.DatabaseClient.get_database")
def test_delete_user_executes_and_logs(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    fake_user_id = str(ObjectId())
    
    success = delete_user(fake_user_id, "terminated@cbk.go.ke", "admin@finlens.go.ke")
    assert success is True
    
    mock_db.Users.delete_one.assert_called_once_with({"_id": ObjectId(fake_user_id)})
    mock_db.AuditLogs.insert_one.assert_called_once()