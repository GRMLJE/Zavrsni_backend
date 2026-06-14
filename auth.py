import os
from functools import wraps

import jwt
from flask import g, jsonify, request

_SECRET = os.environ.get("JWT_SECRET", "dev-secret-promijeni-u-produkciji")


def create_token(user_id: int) -> str:
    return jwt.encode({"user_id": user_id}, _SECRET, algorithm="HS256")


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Autentifikacija je obavezna."}), 401
        token = auth[7:]
        try:
            payload = jwt.decode(token, _SECRET, algorithms=["HS256"])
            g.user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"error": "Nevažeći ili istekli token."}), 401
        return f(*args, **kwargs)
    return decorated
