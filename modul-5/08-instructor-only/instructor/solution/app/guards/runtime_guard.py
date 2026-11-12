"""REFERENCE SOLUTION - Layer 5 runtime guard."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass

from app.context import RequestContext
from app.guards import GuardResult

MAX_INPUT = 4000
RATE_PER_MIN = 60
TOKEN_BUDGET = 60_000  # per client, since the app started

_hits: dict[str, deque] = defaultdict(deque)
_spent: dict[str, int] = defaultdict(int)


@dataclass
class Limits:
    max_input_chars: int | None = MAX_INPUT
    recursion_limit: int = 15  # model + tool steps for one request
    max_output_tokens: int | None = 1500  # gpt-5 family counts reasoning tokens here too


def check_request(ctx: RequestContext, message: str) -> GuardResult:
    if len(message) > MAX_INPUT:
        return GuardResult(False, f"input larger than {MAX_INPUT} characters")
    now = time.time()
    q = _hits[ctx.client_id]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= RATE_PER_MIN:
        return GuardResult(False, "rate limit exceeded")
    q.append(now)
    if _spent[ctx.client_id] > TOKEN_BUDGET:
        return GuardResult(False, "token budget exhausted")
    return GuardResult(True)


def limits() -> Limits:
    return Limits()


def record_usage(ctx: RequestContext, usage: dict) -> None:
    _spent[ctx.client_id] += int(usage.get("total_tokens", 0))
    if _spent[ctx.client_id] > 0.8 * TOKEN_BUDGET:
        ctx.trace.event("runtime", "budget_warning", f"{_spent[ctx.client_id]} tokens used")
