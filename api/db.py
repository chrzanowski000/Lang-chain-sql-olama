
import sqlite3
from typing import List, Any

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.environ.get("SQLITE_PATH", "./shop.db")
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def run_select(sql: str, params: List[Any] = None):
    params = params or []
    with get_conn() as conn:
        cur = conn.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
    return rows

def run_exec(sql: str, params: List[Any] = None):
    params = params or []
    with get_conn() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return {"rows_affected": cur.rowcount}
