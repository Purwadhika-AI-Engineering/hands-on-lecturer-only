"""LAYER 4 - OUTPUT GUARD  (OWASP LLM02 Sensitive Information Disclosure, LLM10 Improper Output Handling)

Last line before the user. Treat model output as untrusted input to the rest of the system.

Starter state: whatever the model says is returned as-is.

Ideas:
  - Redact PII: e-mail addresses, Indonesian phone numbers (+62 / 08...), 16-digit NIK numbers.
  - Redact secrets: API keys, passwords, anything from the system prompt that must stay hidden.
  - Remove markdown images / links to non-allowlisted domains (a classic data-exfiltration channel).
  - Presidio is a good production tool; plain regex is enough for this lab.

Return GuardResult(text=cleaned) to rewrite, or GuardResult(allowed=False, reason=...) to replace the whole answer.
"""
from app.context import RequestContext
from app.guards import GuardResult


def filter(text: str, ctx: RequestContext) -> GuardResult:  # noqa: A001
    # TODO (Lab step 2, Layer 4): implement.
    return GuardResult(allowed=True, text=text)
