from db import get_db
from services import email_service


def create_event(title, description, event_date, category_id, neighborhood_id, user_id, address=None):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
            if not cur.fetchone():
                raise LookupError("Korisnik nije pronađen.")
            cur.execute(
                """
                INSERT INTO events (title, description, event_date, category_id, neighborhood_id, user_id, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (title, description, event_date, category_id, neighborhood_id, user_id, address),
            )
            return cur.fetchone()[0]


def _build_events_query(viewer_user_id, city_id, neighborhood_id, category_id, user_id, status="approved"):
    query = """
        SELECT
            e.id, e.title, e.description, e.event_date,
            cat.name AS category,
            n.name  AS neighborhood,
            c.name  AS city,
            e.user_id,
            e.address,
            (SELECT COUNT(*) FROM event_participants ep WHERE ep.event_id = e.id) AS attendee_count,
            EXISTS (
                SELECT 1 FROM event_participants ep
                WHERE ep.event_id = e.id AND ep.user_id = %s
            ) AS is_joined,
            e.status
        FROM events e
        JOIN categories cat ON e.category_id = cat.id
        JOIN neighborhoods n  ON e.neighborhood_id = n.id
        JOIN cities c         ON n.city_id = c.id
        WHERE 1=1
    """
    params = [viewer_user_id or -1]
    if status is not None:
        query += " AND e.status = %s"; params.append(status)
    if city_id:
        query += " AND c.id = %s"; params.append(city_id)
    if neighborhood_id:
        query += " AND n.id = %s"; params.append(neighborhood_id)
    if category_id:
        query += " AND cat.id = %s"; params.append(category_id)
    if user_id:
        query += " AND e.user_id = %s"; params.append(user_id)
    query += " ORDER BY e.event_date ASC, e.id DESC"
    return query, params


def _row_to_dict(row):
    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "event_date": row[3].isoformat() if row[3] else None,
        "category": row[4],
        "neighborhood": row[5],
        "city": row[6],
        "user_id": row[7],
        "address": row[8],
        "attendee_count": row[9],
        "is_joined": row[10],
        "status": row[11] if len(row) > 11 else "approved",
    }


def get_events(viewer_user_id=None, city_id=None, neighborhood_id=None, category_id=None, user_id=None):
    query, params = _build_events_query(viewer_user_id, city_id, neighborhood_id, category_id, user_id)
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return [_row_to_dict(r) for r in cur.fetchall()]


def get_event(event_id, viewer_user_id=None):
    query = """
        SELECT
            e.id, e.title, e.description, e.event_date,
            cat.name AS category,
            n.name  AS neighborhood,
            c.name  AS city,
            e.user_id,
            e.address,
            (SELECT COUNT(*) FROM event_participants ep WHERE ep.event_id = e.id) AS attendee_count,
            EXISTS (
                SELECT 1 FROM event_participants ep
                WHERE ep.event_id = e.id AND ep.user_id = %s
            ) AS is_joined,
            e.status,
            u.first_name || ' ' || u.last_name AS organizer_name,
            u.email AS organizer_email
        FROM events e
        JOIN categories cat ON e.category_id = cat.id
        JOIN neighborhoods n  ON e.neighborhood_id = n.id
        JOIN cities c         ON n.city_id = c.id
        LEFT JOIN users u     ON e.user_id = u.id
        WHERE e.id = %s
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, [viewer_user_id or -1, event_id])
            row = cur.fetchone()
    if not row:
        return None
    d = _row_to_dict(row)
    d["organizer_name"] = row[12]
    d["organizer_email"] = row[13]
    return d


def get_events_by_status(status="pending"):
    query = """
        SELECT
            e.id, e.title, e.description, e.event_date,
            cat.name AS category,
            n.name  AS neighborhood,
            c.name  AS city,
            e.user_id,
            e.address,
            (SELECT COUNT(*) FROM event_participants ep WHERE ep.event_id = e.id) AS attendee_count,
            FALSE AS is_joined,
            e.status
        FROM events e
        JOIN categories cat ON e.category_id = cat.id
        JOIN neighborhoods n  ON e.neighborhood_id = n.id
        JOIN cities c         ON n.city_id = c.id
        WHERE e.status = %s
        ORDER BY e.id DESC
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query, [status])
            return [_row_to_dict(r) for r in cur.fetchall()]


def set_event_status(event_id, status):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE events SET status = %s WHERE id = %s RETURNING id;",
                (status, event_id),
            )
            if not cur.fetchone():
                raise LookupError("Event nije pronađen.")


def join_event(event_id, user_id):
    event_info = None
    user_info = None
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.id, e.user_id, e.title, e.event_date,
                       n.name, c.name
                FROM events e
                JOIN neighborhoods n ON e.neighborhood_id = n.id
                JOIN cities c ON n.city_id = c.id
                WHERE e.id = %s;
                """,
                (event_id,),
            )
            event = cur.fetchone()
            if not event:
                raise LookupError("Event nije pronađen.")
            if event[1] == user_id:
                raise ValueError("Vlasnik eventa ne može se dodatno prijaviti na vlastiti event.")
            cur.execute(
                "SELECT 1 FROM event_participants WHERE event_id = %s AND user_id = %s;",
                (event_id, user_id),
            )
            if cur.fetchone():
                raise ValueError("Već si prijavljen na ovaj event.")
            cur.execute(
                "INSERT INTO event_participants (event_id, user_id) VALUES (%s, %s);",
                (event_id, user_id),
            )
            cur.execute(
                "SELECT first_name, email FROM users WHERE id = %s;",
                (user_id,),
            )
            user_info = cur.fetchone()
            event_info = event

    if event_info and user_info:
        title = event_info[2]
        date_str = event_info[3].strftime("%-d. %-m. %Y.") if event_info[3] else "–"
        location = f"{event_info[4]}, {event_info[5]}"
        email_service.send_join_confirmation(
            user_info[1], user_info[0], title, date_str, location
        )


def leave_event(event_id, user_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM event_participants WHERE event_id = %s AND user_id = %s;",
                (event_id, user_id),
            )
            if cur.rowcount == 0:
                raise LookupError("Prijava na event nije pronađena.")


def delete_event(event_id, user_id):
    participants = []
    event_title = None
    event_date_str = None
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, title, event_date FROM events WHERE id = %s;",
                (event_id,),
            )
            row = cur.fetchone()
            if not row:
                raise LookupError("Event nije pronađen.")
            if row[0] != user_id:
                raise PermissionError("Samo vlasnik može obrisati event.")
            event_title = row[1]
            event_date_str = row[2].strftime("%-d. %-m. %Y.") if row[2] else "–"
            cur.execute(
                """
                SELECT u.first_name, u.email
                FROM event_participants ep
                JOIN users u ON u.id = ep.user_id
                WHERE ep.event_id = %s;
                """,
                (event_id,),
            )
            participants = cur.fetchall()
            cur.execute("DELETE FROM events WHERE id = %s;", (event_id,))

    for first_name, email in participants:
        email_service.send_event_cancelled(email, first_name, event_title, event_date_str)
