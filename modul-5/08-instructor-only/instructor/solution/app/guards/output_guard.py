"""REFERENCE SOLUTION - Layer 4 output guard."""
from __future__ import annotations

import re

from app import config
from app.context import RequestContext
from app.guards import GuardResult

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_PHONE = re.compile(r"(?<!\d)(?:\+62|62|0)8\d{8,12}(?!\d)")
_NIK = re.compile(r"(?<!\d)\d{16}(?!\d)")
_SECRETS = [re.compile(p, re.I) for p in (r"sk-[A-Za-z0-9_-]{16,}", r"ACME_DB_PASSWORD\s*[=:]\s*\S+", r"fake[-_][\w-]*lab[\w-]*", r"STAFF-ACME-\d+")]
_IMAGE = re.compile(r"!\[[^\]]*\]\(https?://[^)]+\)")


def _keep_internal(m: re.Match) -> str:
    return m.group(0) if m.group(0).lower().endswith("@" + config.INTERNAL_EMAIL_DOMAIN) else "[email removed]"


def filter(text: str, ctx: RequestContext) -> GuardResult:  # noqa: A001
    out = _IMAGE.sub("[image removed]", text)  # external images are a data-exfiltration channel
    out = _EMAIL.sub(_keep_internal, out)
    out = _PHONE.sub("[phone removed]", out)
    out = _NIK.sub("[id removed]", out)
    for rx in _SECRETS:
        out = rx.sub("[secret removed]", out)
    return GuardResult(True, text=out)
