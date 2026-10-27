"""
Automated Unit Tests for CRSS Authentication & Session Engine (Practical 6)
"""

import pytest
from crss.auth import authenticate_user, generate_rsa256_jwt, verify_token
from crss.exceptions import AuthenticationError


def test_campus_sso_authentication_success():
    """Verifies successful student SSO authentication and session token generation."""
    res = authenticate_user("25C21510", "valid_password_123", auth_mode="SSO")
    assert res["status"] == "success"
    assert res["auth_type"] == "SSO"
    assert res["username"] == "25C21510"
    assert res["token"].startswith("SSO-TOKEN-25C21510")


def test_campus_sso_invalid_credentials_raises_error():
    """Verifies failed SSO login when password length is below policy."""
    with pytest.raises(AuthenticationError):
        authenticate_user("25C21510", "123", auth_mode="SSO")


def test_jwt_fallback_authentication():
    """Verifies fallback to local RSA256/HMAC JWT token generation."""
    res = authenticate_user("25C21510", "valid_password_123", auth_mode="JWT")
    assert res["status"] == "success"
    assert res["auth_type"] == "JWT"
    token = res["token"]
    assert len(token.split(".")) == 3  # Header, Payload, Signature


def test_jwt_token_verification_success():
    """Verifies that generated JWT passes cryptographic signature verification."""
    token = generate_rsa256_jwt("25C21510")
    assert verify_token(token) is True


def test_jwt_token_tampering_detected():
    """Verifies that tampered token fails signature verification."""
    token = generate_rsa256_jwt("25C21510")
    tampered_token = token[:-4] + "ABCD"
    assert verify_token(tampered_token) is False
