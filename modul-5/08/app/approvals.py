"""Tiny human-in-the-loop queue. In-memory: it resets when the app restarts."""
from __future__ import annotations

import time
import uuid

_PENDING: dict[str, dict] = {}


def create(tool: str, args: dict, session_id: str) -> str:
    aid = uuid.uuid4().hex[:8]
    _PENDING[aid] = {"id": aid, "tool": tool, "args": args, "session": session_id, "status": "pending", "ts": int(time.time())}
    return aid


def list_all() -> list[dict]:
    return list(_PENDING.values())


def decide(aid: str, approve: bool) -> dict:
    item = _PENDING.get(aid)
    if item is None:
        raise KeyError(aid)
    if item["status"] != "pending":
        return item
    if approve:
        from app import tools  # local import: avoids a cycle

        if item["tool"] == "send_email":
            a = item["args"]
            item["result"] = tools.send_email(a["to"], a["subject"], a["body"], item["session"])
        item["status"] = "approved"
    else:
        item["status"] = "rejected"
    return item


def clear() -> None:
    _PENDING.clear()
