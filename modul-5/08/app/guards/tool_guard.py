"""LAYER 3 - TOOL GUARD  (OWASP LLM03 Excessive Agency; Agentic ASI02 Tool Misuse, ASI03 Privilege Abuse)

The model decides which tool to call and with what arguments. Assume the model has been fooled.
Ask of every tool: what is the worst it can do if the model is fooled?

Starter state: every tool call is allowed, the database is read/write on every table,
read_file can read any path on the server, and send_email can mail anyone with no review.

Three hooks:

authorize(name, args, ctx) -> ToolDecision
    Called before EVERY tool call. Allow, deny, or require human approval.
    Ideas: recipient domain allowlist for send_email, human approval for anything that
    leaves the company, a cap on tool calls per request.

sql_policy() -> SqlPolicy
    Applied by the database layer (SQLite authorizer), so it cannot be argued away by a prompt.
    Fields: read_only (bool), allowed_tables (set[str] | None = all), max_rows (int)

file_policy() -> FilePolicy
    root=None means "read anything". Set a root folder and the file tool refuses to leave it
    (symlinks and ../ included).
"""
from app.context import RequestContext
from app.db import SqlPolicy
from app.guards import ToolDecision
from app.tools import FilePolicy


def authorize(name: str, args: dict, ctx: RequestContext) -> ToolDecision:
    # TODO (Lab step 2, Layer 3): implement.
    return ToolDecision(allow=True)


def sql_policy() -> SqlPolicy:
    # TODO (Lab step 2, Layer 3): least privilege for the database.
    return SqlPolicy(read_only=False, allowed_tables=None, max_rows=50)


def file_policy() -> FilePolicy:
    # TODO (Lab step 2, Layer 3): confine the file tool to one folder.
    return FilePolicy(root=None)
