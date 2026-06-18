import os
from functools import wraps

import jwt
from flask import g, jsonify, request

from db import get_db

_SECRET = os.environ.get("JWT_SECRET", "dev-secret-promijeni-u-produkciji")


def create_token(user_id: int) -> str:
    return jwt.encode({"user_id": user_id}, _SECRET, algorithm="HS256")


def _decode_token():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, jsonify({"error": "Autentifikacija je obavezna."}), 401
    try:
        payload = jwt.decode(auth[7:], _SECRET, algorithms=["HS256"])
        return payload["user_id"], None, None
    except jwt.InvalidTokenError:
        return None, jsonify({"error": "Nevažeći ili istekli token."}), 401


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id, err, status = _decode_token()
        if err:
            return err, status
        g.user_id = user_id
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id, err, status = _decode_token()
        if err:
            return err, status
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT role FROM users WHERE id = %s;", (user_id,))
                row = cur.fetchone()
        if not row or row[0] != "admin":
            return jsonify({"error": "Pristup zabranjen."}), 403
        g.user_id = user_id
        return f(*args, **kwargs)
    return decorated
