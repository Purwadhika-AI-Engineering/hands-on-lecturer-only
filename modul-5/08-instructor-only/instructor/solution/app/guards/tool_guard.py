"""REFERENCE SOLUTION - Layer 3 tool guard (least agency)."""
from __future__ import annotations

import re

from app import config
from app.context import RequestContext
from app.db import SqlPolicy
from app.guards import ToolDecision
from app.tools import FilePolicy

MAX_TOOL_CALLS = 5
_ADDR = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def authorize(name: str, args: dict, ctx: RequestContext) -> ToolDecision:
    if len(ctx.trace.tool_calls) > MAX_TOOL_CALLS:  # the current call is already in the list
        return ToolDecision(False, f"more than {MAX_TOOL_CALLS} tool calls in one request")
    if name == "send_email":
        to = str(args.get("to", "")).strip().lower()
        found = _ADDR.findall(to)
        if len(found) != 1 or found[0] != to:
            return ToolDecision(False, "send_email accepts exactly one recipient address")
        if not to.endswith("@" + config.INTERNAL_EMAIL_DOMAIN):
            return ToolDecision(False, f"recipient outside @{config.INTERNAL_EMAIL_DOMAIN} is not allowed")
        return ToolDecision(True, needs_approval=True)  # human-in-the-loop for anything that leaves the app
    return ToolDecision(True)


def sql_policy() -> SqlPolicy:
    return SqlPolicy(read_only=True, allowed_tables={"products", "orders"}, max_rows=20)


def file_policy() -> FilePolicy:
    return FilePolicy(root=str(config.DATA_DIR / "public_files"))
