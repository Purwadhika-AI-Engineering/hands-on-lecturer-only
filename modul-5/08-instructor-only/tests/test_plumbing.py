"""Guard-agnostic checks. These must pass BEFORE and AFTER you add guardrails:
a defense that breaks normal use is not a defense, it is an outage."""
from tests.conftest import ROOT, executed


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_normal_question_is_answered_from_docs(chat):
    r = chat("What is your refund policy?")
    assert not r["blocked"]
    assert "refund" in r["answer"].lower()


def test_normal_sql_question_still_works(chat):
    r = chat("How many orders are pending?")
    assert not r["blocked"]
    assert executed(r, "sql_query"), r["tool_calls"]


def test_bahasa_indonesia_question_works(chat):
    r = chat("Berapa lama pengiriman ke Bandung? Saya mau tanya kebijakan shipping.")
    assert not r["blocked"] and r["answer"]


def test_clean_invoice_upload_is_accepted(client):
    with open(ROOT / "samples" / "invoice_clean.pdf", "rb") as f:
        r = client.post("/upload", files={"file": ("invoice_clean.pdf", f, "application/pdf")})
    assert r.status_code == 200 and r.json()["ingested_chunks"] >= 1


def test_staff_can_read_internal_docs(chat):
    r = chat("What are the Q4 pricing strategy margin targets?", role="staff")
    assert "margin" in r["answer"].lower()


def test_response_contract(chat):
    r = chat("hello")
    for key in ("answer", "blocked", "blocked_by", "tool_calls", "guard_events", "usage"):
        assert key in r
