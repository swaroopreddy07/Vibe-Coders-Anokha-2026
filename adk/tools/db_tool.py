# adk/tools/db_tool.py
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SQLITE_PATH = os.path.join(PROJECT_ROOT, "dev_data.sqlite")

POSTGRES_CONFIG = {
    "dbname": os.getenv("PG_DB", "resume_db"),
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASS", "postgres"),
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", 5432)),
}

def _get_student_from_sqlite(user_id: str) -> dict:
    # Create DB and seed if not exists
    if not os.path.exists(SQLITE_PATH):
        conn = sqlite3.connect(SQLITE_PATH)
        cur = conn.cursor()
        cur.execute("CREATE TABLE students (user_id TEXT PRIMARY KEY, data TEXT)")
        sample = {
            "user_id": "sanjana01",
            "name": "Sanjana",
            "email": "sanjana@example.com",
            "education": [{"degree":"BTech CSE","year":2025,"institute":"XYZ"}],
            "projects": [{"name":"Seismic Classifier","desc":"P-wave vs noise using TCN","tech":["Python","TCN"]}],
            "skills": ["Python","ML","TCN","PyTorch"],
            "experience": []
        }
        cur.execute("INSERT INTO students VALUES (?, ?)", (sample["user_id"], json.dumps(sample)))
        conn.commit()
        conn.close()

    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()
    cur.execute("SELECT data FROM students WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"error": "Student not found (sqlite)"}
    return json.loads(row[0])

def get_student_data(user_id: str) -> dict:
    """
    Try Postgres first. If connection fails, fall back to a local SQLite dev DB.
    """
    try:
        conn = psycopg2.connect(
            dbname=POSTGRES_CONFIG["dbname"],
            user=POSTGRES_CONFIG["user"],
            password=POSTGRES_CONFIG["password"],
            host=POSTGRES_CONFIG["host"],
            port=POSTGRES_CONFIG["port"],
            connect_timeout=3
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM students WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return {"error": "Student not found (postgres)"}
        # ensure JSON serializable types
        return dict(row)
    except Exception as e:
        # postgres failed — fallback to sqlite (quietly)
        return _get_student_from_sqlite(user_id)
