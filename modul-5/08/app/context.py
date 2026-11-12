"""Per-request context shared by the app, the agent tools and the guards."""
from __future__ import annotations

import contextvars
import time
import uuid
from dataclasses import dataclass, field


@dataclass
class Trace:
    """Everything that happened during one /chat request. Returned to the client."""

    tool_calls: list = field(default_factory=list)
    guard_events: list = field(default_factory=list)

    def event(self, layer: str, action: str, detail: str = "") -> None:
        self.guard_events.append({"layer": layer, "action": action, "detail": detail[:300], "t": round(time.time(), 3)})


@dataclass
class RequestContext:
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    role: str = "customer"  # "customer" or "staff"
    client_id: str = "local"  # caller identity for rate limits (client IP)
    trace: Trace = field(default_factory=Trace)


_current: contextvars.ContextVar[RequestContext | None] = contextvars.ContextVar("ctx", default=None)


def set_ctx(ctx: RequestContext) -> None:
    _current.set(ctx)


def current_ctx() -> RequestContext:
    ctx = _current.get()
    if ctx is None:  # e.g. called outside a request (tests, scripts)
        ctx = RequestContext()
        _current.set(ctx)
    return ctx
