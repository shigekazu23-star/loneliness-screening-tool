# ---- M1 Authentication & Authorization ----
# Password hashing with bcrypt, stateless JWT session tokens, and
# role-based access control (older_adult / caregiver), as specified in
# the Unit 3 module breakdown. Stateless tokens keep the API layer
# horizontally scalable (scalability NFR).

import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
from flask import g, jsonify, request

JWT_SECRET = os.environ.get(
    "LST_JWT_SECRET", "dev-only-secret-change-in-production-0123456789"
)
JWT_ALGORITHM = "HS256"
TOKEN_TTL_HOURS = 8

ROLES = ("older_adult", "caregiver")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"), password_hash.encode("utf-8")
    )


def issue_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def require_auth(*allowed_roles):
    """Decorator enforcing a valid token and, optionally, specific roles.

    Usage: @require_auth() for any authenticated user, or
    @require_auth("caregiver") to restrict by role (RBAC).
    """

    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return jsonify({"error": "missing bearer token"}), 401
            try:
                payload = decode_token(header[len("Bearer "):])
            except jwt.PyJWTError:
                return jsonify({"error": "invalid or expired token"}), 401
            if allowed_roles and payload["role"] not in allowed_roles:
                return jsonify({"error": "forbidden for this role"}), 403
            g.user_id = int(payload["sub"])
            g.role = payload["role"]
            return view(*args, **kwargs)

        return wrapper

    return decorator
