"""
db.py — PostgreSQL metadata store via psycopg2.

Tables:
  documents  — one row per uploaded PDF (S3 key, filename, upload time)
  chunks     — one row per embedded chunk (links to documents + Qdrant point id)
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        dbname=os.getenv("POSTGRES_DB", "bog_assist"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id          SERIAL PRIMARY KEY,
                    filename    TEXT NOT NULL UNIQUE,
                    s3_key      TEXT NOT NULL,
                    meeting_no  TEXT,
                    uploaded_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id          SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                    qdrant_id   TEXT NOT NULL,
                    page        INTEGER,
                    item_no     TEXT,
                    created_at  TIMESTAMPTZ DEFAULT NOW()
                );
            """)
    conn.close()
    print("✅ PostgreSQL tables ready")


# ─── DOCUMENTS ────────────────────────────────────────────────────────────────

def insert_document(filename: str, s3_key: str, meeting_no: str | None) -> int:
    """Insert a document record and return its id."""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO documents (filename, s3_key, meeting_no)
                VALUES (%s, %s, %s)
                ON CONFLICT (filename) DO UPDATE
                    SET s3_key = EXCLUDED.s3_key,
                        meeting_no = EXCLUDED.meeting_no,
                        uploaded_at = NOW()
                RETURNING id;
            """, (filename, s3_key, meeting_no))
            doc_id = cur.fetchone()[0]
    conn.close()
    return doc_id


def get_all_documents():
    conn = get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM documents ORDER BY uploaded_at DESC;")
        rows = cur.fetchall()
    conn.close()
    return rows


def document_exists(filename: str) -> bool:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM documents WHERE filename = %s;", (filename,))
        exists = cur.fetchone() is not None
    conn.close()
    return exists


# ─── CHUNKS ───────────────────────────────────────────────────────────────────

def insert_chunks(doc_id: int, chunk_records: list[dict]):
    """
    chunk_records: list of {qdrant_id, page, item_no}
    """
    if not chunk_records:
        return
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.executemany("""
                INSERT INTO chunks (document_id, qdrant_id, page, item_no)
                VALUES (%s, %s, %s, %s);
            """, [
                (doc_id, r["qdrant_id"], r.get("page"), r.get("item_no"))
                for r in chunk_records
            ])
    conn.close()


def get_qdrant_ids_for_document(doc_id: int) -> list[str]:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT qdrant_id FROM chunks WHERE document_id = %s;", (doc_id,))
        ids = [row[0] for row in cur.fetchall()]
    conn.close()
    return ids


def delete_document(doc_id: int):
    """Cascade deletes chunks too."""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM documents WHERE id = %s;", (doc_id,))
    conn.close()
