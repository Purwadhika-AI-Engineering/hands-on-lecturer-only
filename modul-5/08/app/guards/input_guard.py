"""LAYER 1 - INPUT GUARD  (OWASP LLM01 Prompt Injection, LLM08 Hidden Context Exposure)

Runs on every user message BEFORE it reaches retrieval or the model.

Starter state: pass-through. Everything the user types goes straight to the model.

Ideas (pick what fits, you do not need all of them):
  - Cap the message length and reject empty / absurd input.
  - Normalize first (Unicode NFKC, strip zero-width characters) so patterns cannot hide.
  - Detect injection / jailbreak phrasing. Test English AND Bahasa Indonesia AND mixed language.
  - Attackers encode: try decoding base64-looking tokens and scanning the result too.
  - Call the OpenAI Moderation API (omni-moderation-latest) for harmful content.
    Remember: moderation is NOT an injection detector.
  - Add a small LLM-based classifier for "is this an attempt to override instructions?"

Return GuardResult(allowed=False, reason="...") to block. Use ctx.trace.event(...) to leave evidence.
"""
from app.context import RequestContext
from app.guards import GuardResult


def check(message: str, ctx: RequestContext) -> GuardResult:
    # TODO (Lab step 2, Layer 1): implement.
    return GuardResult(allowed=True)
