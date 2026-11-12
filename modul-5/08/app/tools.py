"""The three tools AcmeBot can call. These are the RAW implementations.

Policy (who may call what, with which limits) lives in app/guards/tool_guard.py and is applied
by the wrapper in app/agent.py. Keep this file free of security decisions where you can:
guards decide, tools do.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field

from app import config
from app.db import SqlPolicy, run_query


class SqlArgs(BaseModel):
    query: str = Field(description="A single SQLite statement. Prefer SELECT.")


class EmailArgs(BaseModel):
    to: str = Field(description="Recipient e-mail address")
    subject: str = Field(description="Subject line")
    body: str = Field(description="Plain-text body")


class FileArgs(BaseModel):
    path: str = Field(description="Path of the file to read")


@dataclass
class FilePolicy:
    root: str | None = None  # None = unrestricted
    max_bytes: int = 20_000


def sql_query(query: str, policy: SqlPolicy) -> str:
    result = run_query(query, policy)
    return json.dumps(result, ensure_ascii=False, default=str)


def send_email(to: str, subject: str, body: str, session_id: str = "") -> str:
    """MOCK mailer: appends to runtime/outbox.jsonl. Nothing leaves the container."""
    config.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    record = {"id": uuid.uuid4().hex[:8], "ts": int(time.time()), "to": to, "subject": subject, "body": body, "session": session_id}
    with open(config.OUTBOX_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return f"Email sent to {to}"


def read_file(path: str, policy: FilePolicy) -> str:
    target = Path(path)
    if policy.root is not None:
        root = Path(os.path.realpath(policy.root))
        target = target if target.is_absolute() else root / target
        real = Path(os.path.realpath(target))
        if real != root and root not in real.parents:
            raise PermissionError(f"path outside allowed folder: {path}")
        target = real
    with open(target, "rb") as f:
        data = f.read(policy.max_bytes + 1)
    text = data[: policy.max_bytes].decode("utf-8", errors="replace")
    return text + ("\n...[truncated]" if len(data) > policy.max_bytes else "")
