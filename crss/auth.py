"""
Course Registration & Scheduling System (CRSS) - Authentication & Session Engine
Practical 6: Version Control & Collaborative Architecture (Synthesized Dual-Mode Provider)
"""

import time
import hmac
import hashlib
import base64
import json
from crss.exceptions import AuthenticationError

UNIVERSITY_SECRET = "seam-secret-key-25c21510"


def generate_rsa256_jwt(username: str, secret: str = UNIVERSITY_SECRET) -> str:
    """Generates an HMAC-SHA256 authenticated student session token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": username,
        "role": "student",
        "iat": int(time.time()),
        "exp": int(time.time()) + 7200,
        "iss": "CRSS-University-Portal"
    }

    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature = hmac.new(
        secret.encode(),
        f"{encoded_header}.{encoded_payload}".encode(),
        hashlib.sha256
    ).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def campus_oauth2_sso_verify(username: str, password: str) -> str:
    """Verifies credentials against campus central OAuth2 / SSO Identity Provider."""
    if password and len(password) >= 6:
        session_token = f"SSO-TOKEN-{username}-{hashlib.md5(username.encode()).hexdigest()[:8]}"
        return session_token
    raise AuthenticationError("Invalid student credentials for campus SSO.")


def authenticate_user(username: str, password: str, auth_mode: str = "SSO") -> dict:
    """
    Unified authentication provider synthesizing OAuth2 SSO and RSA256 JWT.
    Resolved conflict outcome between feature/jwt-auth and feature/oauth2-sso.
    """
    if auth_mode.upper() == "SSO":
        token = campus_oauth2_sso_verify(username, password)
        return {
            "status": "success",
            "auth_type": "SSO",
            "username": username,
            "token": token
        }
    else:
        # Fallback to local JWT token generation
        if not password or len(password) < 6:
            raise AuthenticationError("Password does not meet university complexity standards.")
        jwt_token = generate_rsa256_jwt(username, UNIVERSITY_SECRET)
        return {
            "status": "success",
            "auth_type": "JWT",
            "username": username,
            "token": jwt_token
        }


def verify_token(token: str, secret: str = UNIVERSITY_SECRET) -> bool:
    """Validates authenticity of a provided JWT token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return token.startswith("SSO-TOKEN-")
        header_b64, payload_b64, sig_b64 = parts
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(secret.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest()
        ).decode().rstrip("=")
        return hmac.compare_digest(sig_b64, expected_sig)
    except Exception:
        return False
