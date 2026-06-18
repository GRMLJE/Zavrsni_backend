#!/usr/bin/env python3
"""
Migration script — creates all tables and seeds initial data.
Run from the Backend directory or via Docker:
  python migrate.py
Reads the same env vars as the app: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD.
Safe to re-run: uses IF NOT EXISTS and ON CONFLICT DO NOTHING.
"""

import os
import sys
import psycopg2

def get_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        database=os.environ.get("DB_NAME", "postgres"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
        sslmode=os.environ.get("DB_SSLMODE", "prefer"),
    )


DDL = """
-- Sequences
CREATE SEQUENCE IF NOT EXISTS public.activities_id_seq AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
CREATE SEQUENCE IF NOT EXISTS public.cities_id_seq     AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
CREATE SEQUENCE IF NOT EXISTS public.neighborhoods_id_seq AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
CREATE SEQUENCE IF NOT EXISTS public.events_id_seq     AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
CREATE SEQUENCE IF NOT EXISTS public.users_id_seq      AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

-- Tables
CREATE TABLE IF NOT EXISTS public.categories (
    id         integer  NOT NULL DEFAULT nextval('public.activities_id_seq'),
    name       text     NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT activities_pkey PRIMARY KEY (id)
);
ALTER SEQUENCE public.activities_id_seq OWNED BY public.categories.id;

CREATE TABLE IF NOT EXISTS public.cities (
    id   integer NOT NULL DEFAULT nextval('public.cities_id_seq'),
    name text    NOT NULL,
    CONSTRAINT cities_pkey PRIMARY KEY (id)
);
ALTER SEQUENCE public.cities_id_seq OWNED BY public.cities.id;

CREATE TABLE IF NOT EXISTS public.neighborhoods (
    id      integer NOT NULL DEFAULT nextval('public.neighborhoods_id_seq'),
    name    text    NOT NULL,
    city_id integer NOT NULL,
    CONSTRAINT neighborhoods_pkey PRIMARY KEY (id),
    CONSTRAINT fk_city FOREIGN KEY (city_id) REFERENCES public.cities(id) ON DELETE CASCADE
);
ALTER SEQUENCE public.neighborhoods_id_seq OWNED BY public.neighborhoods.id;

CREATE TABLE IF NOT EXISTS public.users (
    id               integer   NOT NULL DEFAULT nextval('public.users_id_seq'),
    first_name       text      NOT NULL,
    last_name        text      NOT NULL,
    email            text      NOT NULL,
    password_hash    text      NOT NULL,
    role             text      NOT NULL DEFAULT 'user',
    joined_event_ids integer[] NOT NULL DEFAULT '{}',
    created_at       timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_pkey      PRIMARY KEY (id),
    CONSTRAINT users_email_key UNIQUE (email)
);
ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;

CREATE TABLE IF NOT EXISTS public.events (
    id              integer NOT NULL DEFAULT nextval('public.events_id_seq'),
    title           text    NOT NULL,
    description     text,
    event_date      date    NOT NULL,
    category_id     integer NOT NULL,
    neighborhood_id integer NOT NULL,
    user_id         integer,
    attendee_count  integer NOT NULL DEFAULT 0,
    address         text,
    CONSTRAINT events_pkey       PRIMARY KEY (id),
    CONSTRAINT fk_activity       FOREIGN KEY (category_id)     REFERENCES public.categories(id),
    CONSTRAINT fk_neighborhood   FOREIGN KEY (neighborhood_id) REFERENCES public.neighborhoods(id),
    CONSTRAINT fk_user           FOREIGN KEY (user_id)         REFERENCES public.users(id) ON DELETE SET NULL
);
ALTER SEQUENCE public.events_id_seq OWNED BY public.events.id;

CREATE TABLE IF NOT EXISTS public.event_participants (
    event_id  integer   NOT NULL,
    user_id   integer   NOT NULL,
    joined_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT event_participants_pkey        PRIMARY KEY (event_id, user_id),
    CONSTRAINT fk_event_participants_event    FOREIGN KEY (event_id) REFERENCES public.events(id) ON DELETE CASCADE,
    CONSTRAINT fk_event_participants_user     FOREIGN KEY (user_id)  REFERENCES public.users(id)  ON DELETE CASCADE
);
"""

SEED_CATEGORIES = [
    (1, "Yoga / Meditacija"),
    (2, "Glazba / Koncert"),
    (3, "Sport i rekreacija"),
    (4, "Radionica / Edukacija"),
    (5, "Kultura i izložbe"),
    (6, "Hrana i piće"),
    (7, "Zabava / Party"),
    (8, "Volontiranje"),
    (9, "Outdoor / Priroda"),
    (10, "Wellness"),
    (11, "Tržnica / Sajam"),
    (12, "Djeca i obitelj"),
    (13, "Film i mediji"),
]

SEED_CITIES = [
    (1, "Zagreb"),
]

SEED_NEIGHBORHOODS = [
    "Donji Grad",
    "Gornji Grad - Medveščak",
    "Trnje",
    "Maksimir",
    "Peščenica - Žitnjak",
    "Novi Zagreb - Istok",
    "Novi Zagreb - Zapad",
    "Trešnjevka - Sjever",
    "Trešnjevka - Jug",
    "Črnomerec",
    "Gornja Dubrava",
    "Donja Dubrava",
    "Sesvete",
    "Stenjevec",
    "Brezovica",
    "Podsused - Vrapče",
    "Podsljeme",
    "Jarun",
    "Špansko",
    "Prečko",
    "Vrbani",
    "Siget",
    "Kajzerica",
    "Klara",
    "Remetinec",
    "Savica",
    "Borongaj",
    "Ravnice",
    "Žitnjak",
    "Mirogoj",
    "Šalata",
    "Malešnica",
    "Lanište",
    "Kustošija",
    "Podsused",
    "Markuševac",
    "Gračani",
    "Remete",
    "Retkovec",
    "Sloboština",
    "Dubec",
    "Gajnice",
    "Vrapče",
    "Šestine",
    "Horvati",
    "Lučko",
    "Resnik",
    "Stupnik",
    "Buzin",
    "Dugave",
]

SEED_EVENTS = [
    {
        "id": 1,
        "title": "Koncert Crvena Jabuka",
        "description": "Dolorem ipsum",
        "event_date": "2026-08-14",
        "category_id": 3,
        "neighborhood_name": "Trešnjevka - Sjever",
        "user_id": None,
        "attendee_count": 0,
        "address": None,
    }
]


def run():
    print("Connecting to database...")
    try:
        conn = get_conn()
    except Exception as e:
        print(f"ERROR: Could not connect — {e}")
        sys.exit(1)

    cur = conn.cursor()

    print("Creating tables and sequences...")
    cur.execute(DDL)

    print("Applying schema migrations...")
    cur.execute("""
        ALTER TABLE public.events
            ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'pending';
        UPDATE public.events SET status = 'approved' WHERE status = 'pending';
        UPDATE public.categories SET name = 'Yoga / Meditacija' WHERE id = 1;
        UPDATE public.categories SET name = 'Glazba / Koncert' WHERE id = 2;
        UPDATE public.categories SET name = 'Sport i rekreacija' WHERE id = 3;
        UPDATE public.categories SET name = 'Radionica / Edukacija' WHERE id = 4;
    """)

    print("Seeding categories...")
    for cat_id, name in SEED_CATEGORIES:
        cur.execute(
            """
            INSERT INTO public.categories (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (cat_id, name),
        )
    cur.execute("SELECT setval('public.activities_id_seq', MAX(id)) FROM public.categories")

    print("Seeding cities...")
    for city_id, name in SEED_CITIES:
        cur.execute(
            "INSERT INTO public.cities (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
            (city_id, name),
        )
    cur.execute("SELECT setval('public.cities_id_seq', MAX(id)) FROM public.cities")

    print("Seeding neighborhoods (all Zagreb kvarts)...")
    cur.execute("SELECT id FROM public.cities WHERE name = 'Zagreb' LIMIT 1")
    row = cur.fetchone()
    if row is None:
        print("ERROR: Zagreb not found after insert.")
        sys.exit(1)
    zagreb_id = row[0]

    for name in SEED_NEIGHBORHOODS:
        cur.execute(
            """
            INSERT INTO public.neighborhoods (name, city_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            (name, zagreb_id),
        )
    cur.execute("SELECT setval('public.neighborhoods_id_seq', MAX(id)) FROM public.neighborhoods")

    print("Seeding events...")
    for ev in SEED_EVENTS:
        cur.execute(
            "SELECT id FROM public.neighborhoods WHERE name = %s AND city_id = %s LIMIT 1",
            (ev["neighborhood_name"], zagreb_id),
        )
        nb = cur.fetchone()
        if nb is None:
            print(f"  WARNING: neighborhood '{ev['neighborhood_name']}' not found, skipping event '{ev['title']}'")
            continue
        neighborhood_id = nb[0]

        cur.execute(
            """
            INSERT INTO public.events (id, title, description, event_date, category_id, neighborhood_id, user_id, attendee_count, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                ev["id"],
                ev["title"],
                ev["description"],
                ev["event_date"],
                ev["category_id"],
                neighborhood_id,
                ev["user_id"],
                ev["attendee_count"],
                ev["address"],
            ),
        )
    cur.execute("SELECT setval('public.events_id_seq', GREATEST(MAX(id), 1)) FROM public.events")

    conn.commit()
    cur.close()
    conn.close()
    print("Migration complete.")


if __name__ == "__main__":
    run()
