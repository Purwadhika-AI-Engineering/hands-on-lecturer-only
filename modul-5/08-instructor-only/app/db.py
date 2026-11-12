"""SQLite access with an enforceable policy.

The policy is applied through SQLite's own authorizer callback and a read-only connection,
so it holds no matter what SQL the model writes.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app import config


@dataclass
class SqlPolicy:
    read_only: bool = False
    allowed_tables: set[str] | None = None  # None = every table
    max_rows: int = 50


_READ_ACTIONS = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}


def _connect(policy: SqlPolicy) -> sqlite3.Connection:
    mode = "ro" if policy.read_only else "rw"
    conn = sqlite3.connect(f"file:{config.DB_PATH}?mode={mode}", uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    allowed = {t.lower() for t in policy.allowed_tables} if policy.allowed_tables is not None else None

    def authorizer(action, arg1, arg2, dbname, source):
        if policy.read_only and action not in _READ_ACTIONS:
            return sqlite3.SQLITE_DENY
        if allowed is not None and action == sqlite3.SQLITE_READ and (arg1 or "").lower() not in allowed:
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    conn.set_authorizer(authorizer)
    return conn


def run_query(query: str, policy: SqlPolicy) -> dict:
    """Execute ONE statement under the policy. Returns {"columns": [...], "rows": [...], "truncated": bool}."""
    conn = _connect(policy)
    try:
        cur = conn.execute(query)
        rows = cur.fetchmany(policy.max_rows + 1)
        truncated = len(rows) > policy.max_rows
        rows = rows[: policy.max_rows]
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.commit()
        return {"columns": cols, "rows": [list(r) for r in rows], "truncated": truncated, "rowcount": cur.rowcount}
    finally:
        conn.close()
