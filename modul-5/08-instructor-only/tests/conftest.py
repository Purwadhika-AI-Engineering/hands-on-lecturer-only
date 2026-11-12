"""Offline test setup: scripted fake LLM, throw-away runtime folder. No API key, no cost."""
import os
import sqlite3
import tempfile
from pathlib import Path

os.environ["LLM_MODE"] = "fake"
os.environ["RUNTIME_DIR"] = tempfile.mkdtemp(prefix="acmebot_tests_")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import config  # noqa: E402
from app.main import app  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


_counter = {"n": 0}


@pytest.fixture()
def client():
    _counter["n"] += 1  # a fresh "client IP" per test so rate limits cannot leak between tests
    with TestClient(app, client=(f"10.0.{_counter['n'] // 250}.{_counter['n'] % 250 + 1}", 50000)) as c:
        c.post("/admin/reset")
        yield c
        c.post("/admin/reset")


@pytest.fixture()
def chat(client):
    def _chat(message: str, role: str = "customer", session_id: str | None = None) -> dict:
        body = {"message": message, "role": role}
        if session_id:
            body["session_id"] = session_id
        r = client.post("/chat", json=body)
        assert r.status_code == 200, r.text
        return r.json()

    return _chat


@pytest.fixture()
def db():
    def _q(sql: str):
        conn = sqlite3.connect(config.DB_PATH)
        try:
            return conn.execute(sql).fetchall()
        finally:
            conn.close()

    return _q


def executed(resp: dict, name: str | None = None) -> list[dict]:
    """Tool calls that actually ran (not blocked, not waiting for approval, not errored)."""
    return [t for t in resp["tool_calls"] if t["status"] == "executed" and (name is None or t["name"] == name)]
