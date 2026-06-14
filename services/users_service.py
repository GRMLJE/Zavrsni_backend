from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db


def register_user(first_name, last_name, email, password):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s;", (email,))
            if cur.fetchone():
                raise ValueError("Korisnik s tim emailom već postoji.")
            password_hash = generate_password_hash(password)
            cur.execute(
                """
                INSERT INTO users (first_name, last_name, email, password_hash)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (first_name, last_name, email, password_hash),
            )
            return cur.fetchone()[0]


def authenticate_user(email, password):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, first_name, last_name, email, password_hash, role, created_at FROM users WHERE email = %s;",
                (email,),
            )
            row = cur.fetchone()
    if not row:
        raise ValueError("Neispravan email ili lozinka.")
    user_id, first_name, last_name, user_email, password_hash, role, created_at = row
    if not check_password_hash(password_hash, password):
        raise ValueError("Neispravan email ili lozinka.")
    return {
        "id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": user_email,
        "role": role,
        "created_at": created_at.isoformat() if created_at else None,
    }


def get_user(user_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, first_name, last_name, email, role, created_at FROM users WHERE id = %s;",
                (user_id,),
            )
            row = cur.fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "email": row[3],
        "role": row[4],
        "created_at": row[5].isoformat() if row[5] else None,
    }
