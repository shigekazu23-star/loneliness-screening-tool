# ---- M5 Storage / Data access (repository pattern on SQLite) ----
# All SQL lives here. The application layer talks to these functions only,
# so the database engine can be replaced (SQLite -> PostgreSQL) without
# touching the core logic, as required by the scalability NFR in the
# Unit 3 design. Data minimization: only username, role, display name,
# consent records, item answers, scores, and flags are stored.

import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.environ.get(
    "LST_DB_PATH",
    os.path.join(os.path.dirname(__file__), "lst.db"),
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('older_adult', 'caregiver')),
    display_name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS consents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    version TEXT NOT NULL,
    granted_at TEXT NOT NULL,
    revoked_at TEXT
);

CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    q1 INTEGER NOT NULL,
    q2 INTEGER NOT NULL,
    q3 INTEGER NOT NULL,
    score INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    level TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS caregiver_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caregiver_id INTEGER NOT NULL REFERENCES users(id),
    older_adult_id INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL,
    UNIQUE (caregiver_id, older_adult_id)
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection(db_path: str = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


# ---- users ----

def create_user(conn, username, password_hash, role, display_name):
    cur = conn.execute(
        "INSERT INTO users (username, password_hash, role, display_name, "
        "created_at) VALUES (?, ?, ?, ?, ?)",
        (username, password_hash, role, display_name, _now()),
    )
    conn.commit()
    return cur.lastrowid


def find_user_by_username(conn, username):
    return conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()


def find_user_by_id(conn, user_id):
    return conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()


# ---- consents (M2: versioned, revocable) ----

def grant_consent(conn, user_id, version):
    cur = conn.execute(
        "INSERT INTO consents (user_id, version, granted_at) VALUES (?, ?, ?)",
        (user_id, version, _now()),
    )
    conn.commit()
    return cur.lastrowid


def revoke_consent(conn, user_id):
    conn.execute(
        "UPDATE consents SET revoked_at = ? "
        "WHERE user_id = ? AND revoked_at IS NULL",
        (_now(), user_id),
    )
    conn.commit()


def active_consent(conn, user_id):
    return conn.execute(
        "SELECT * FROM consents WHERE user_id = ? AND revoked_at IS NULL "
        "ORDER BY granted_at DESC LIMIT 1",
        (user_id,),
    ).fetchone()


# ---- responses and flags ----

def save_response(conn, user_id, answers, score):
    cur = conn.execute(
        "INSERT INTO responses (user_id, q1, q2, q3, score, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, answers["q1"], answers["q2"], answers["q3"], score, _now()),
    )
    conn.commit()
    return cur.lastrowid


def score_history(conn, user_id):
    rows = conn.execute(
        "SELECT score, created_at FROM responses WHERE user_id = ? "
        "ORDER BY created_at ASC, id ASC",
        (user_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def save_flag(conn, user_id, level, reason):
    cur = conn.execute(
        "INSERT INTO flags (user_id, level, reason, created_at) "
        "VALUES (?, ?, ?, ?)",
        (user_id, level, reason, _now()),
    )
    conn.commit()
    return cur.lastrowid


def latest_flag(conn, user_id):
    row = conn.execute(
        "SELECT level, reason, created_at FROM flags WHERE user_id = ? "
        "ORDER BY created_at DESC, id DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    return dict(row) if row else None


# ---- caregiver links (M1 RBAC support) ----

def link_caregiver(conn, caregiver_id, older_adult_id):
    cur = conn.execute(
        "INSERT OR IGNORE INTO caregiver_links "
        "(caregiver_id, older_adult_id, created_at) VALUES (?, ?, ?)",
        (caregiver_id, older_adult_id, _now()),
    )
    conn.commit()
    return cur.lastrowid


def linked_older_adults(conn, caregiver_id):
    rows = conn.execute(
        "SELECT u.id, u.username, u.display_name FROM caregiver_links l "
        "JOIN users u ON u.id = l.older_adult_id "
        "WHERE l.caregiver_id = ?",
        (caregiver_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def is_linked(conn, caregiver_id, older_adult_id):
    row = conn.execute(
        "SELECT 1 FROM caregiver_links "
        "WHERE caregiver_id = ? AND older_adult_id = ?",
        (caregiver_id, older_adult_id),
    ).fetchone()
    return row is not None
