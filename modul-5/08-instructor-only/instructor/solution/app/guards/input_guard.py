"""REFERENCE SOLUTION - Layer 1 input guard."""
from __future__ import annotations

import base64
import os
import re
import unicodedata

from app.context import RequestContext
from app.guards import GuardResult

MAX_CHARS = 4000
_ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿"), None)

PATTERNS = [
    r"(ignore|disregard|forget)\s+(all\s+|any\s+)?(the\s+)?(previous|prior|above|earlier)\s+(instructions?|rules?|prompts?)",
    r"(abaikan|lupakan|kesampingkan)\s+(semua\s+|seluruh\s+)?(instruksi|perintah|aturan)",
    r"(reveal|show|print|repeat|display|leak|output|tell me)\s+(me\s+)?(your|the)\s+(system|initial|hidden|developer)\s+(prompt|instructions?|message)",
    r"(tampilkan|tunjukkan|ungkapkan|bocorkan|ulangi|cetak)\b.{0,40}(system prompt|prompt sistem|instruksi\s+(sistem|awal|rahasia))",
    r"\bsystem prompt\b|\bprompt sistem\b",
    r"developer mode|jailbreak|do anything now|\bDAN\b",
    r"(you are now|kamu sekarang|anda sekarang)\b",
]
_COMPILED = [re.compile(p, re.I) for p in PATTERNS]


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).translate(_ZERO_WIDTH)


def _decoded_variants(text: str) -> list[str]:
    out = []
    for tok in re.findall(r"[A-Za-z0-9+/]{20,}={0,2}", text):
        try:
            out.append(base64.b64decode(tok, validate=False).decode("utf-8", "ignore"))
        except Exception:  # noqa: BLE001
            pass
    return out


def _hit(text: str) -> str | None:
    for rx in _COMPILED:
        if rx.search(text):
            return rx.pattern[:60]
    return None


def check(message: str, ctx: RequestContext) -> GuardResult:
    if not message.strip():
        return GuardResult(False, "empty message")
    if len(message) > MAX_CHARS:
        return GuardResult(False, f"message longer than {MAX_CHARS} characters")
    clean = _normalize(message)
    for candidate in [clean, *_decoded_variants(clean)]:
        hit = _hit(candidate)
        if hit:
            return GuardResult(False, f"injection pattern: {hit}")
    if os.getenv("ENABLE_MODERATION") == "1" and os.getenv("OPENAI_API_KEY"):
        try:  # moderation covers harmful content only, it is NOT an injection detector
            from openai import OpenAI

            res = OpenAI().moderations.create(model="omni-moderation-latest", input=clean)
            if res.results[0].flagged:
                return GuardResult(False, "flagged by moderation")
        except Exception as exc:  # noqa: BLE001 - availability trade-off: fail open, but leave evidence
            ctx.trace.event("input", "moderation_unavailable", str(exc))
    return GuardResult(True, text=clean)
