"""LAYER 5 - RUNTIME GUARD  (OWASP LLM06 Unbounded Consumption)

Wraps every other layer: how much, how fast, how long. This is also where your bill is protected.

Starter state: no rate limit, no size limit, a huge agent step budget, no output token cap.

Hooks:
check_request(ctx, message) -> GuardResult
    Called first. Rate limit per session, reject oversized input, enforce a budget.
limits() -> Limits
    max_input_chars, recursion_limit (max agent steps), max_output_tokens
record_usage(ctx, usage)
    Called after the agent finishes with {"input_tokens", "output_tokens", "total_tokens"}.
    Ideas: keep a per-session token budget and alert / block when it is exceeded.
"""
from dataclasses import dataclass

from app.context import RequestContext
from app.guards import GuardResult


@dataclass
class Limits:
    max_input_chars: int | None = None
    recursion_limit: int = 100
    max_output_tokens: int | None = None


def check_request(ctx: RequestContext, message: str) -> GuardResult:
    # TODO (Lab step 2, Layer 5): implement.
    return GuardResult(allowed=True)


def limits() -> Limits:
    # TODO (Lab step 2, Layer 5): set sane limits.
    return Limits()


def record_usage(ctx: RequestContext, usage: dict) -> None:
    # TODO (Lab step 2, Layer 5): track spend per session.
    return None
