import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, status TEXT, retries INTEGER)")
    conn.commit()
    return conn

def add_job(conn, job_id):
    conn.execute("INSERT OR IGNORE INTO jobs VALUES (?, ?, ?)", (job_id, "pending", 0))
    conn.commit()

def mark_done(conn, job_id):
    conn.execute("UPDATE jobs SET status='done' WHERE id=?", (job_id,))
    conn.commit()

def mark_failed(conn, job_id):
    conn.execute("UPDATE jobs SET retries=retries+1 WHERE id=?", (job_id,))
    conn.commit()
