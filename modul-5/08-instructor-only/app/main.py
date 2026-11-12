"""AcmeBot API. Pipeline: runtime -> input guard -> retrieval (data guard) -> agent (tool guard) -> output guard."""
from __future__ import annotations

import io
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pypdf import PdfReader

from app import agent, approvals, config, rag, seed
from app.context import RequestContext, set_ctx
from app.guards import GuardResult, data_guard, input_guard, output_guard, runtime_guard

log = logging.getLogger("acmebot")
REFUSAL = "Sorry, I can't help with that request."


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not config.DB_PATH.exists():
        seed.seed(reset=True)
    try:
        n = rag.load_corpus()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Could not build the knowledge base ({exc}). Is OPENAI_API_KEY set in .env? (or LLM_MODE=fake)") from exc
    log.info("knowledge base ready: %s chunks", n)
    yield


app = FastAPI(title="AcmeBot (training lab: vulnerable by design)", lifespan=lifespan)


class ChatIn(BaseModel):
    message: str
    session_id: str | None = None
    role: str = Field(default="customer", pattern="^(customer|staff)$")


def _guard(fn, layer: str, ctx: RequestContext, *args) -> GuardResult:
    """Run a guard; if it crashes, FAIL CLOSED and say why in the trace."""
    try:
        return fn(*args)
    except Exception as exc:  # noqa: BLE001
        log.exception("%s guard crashed", layer)
        ctx.trace.event(layer, "error", str(exc))
        return GuardResult(allowed=False, reason=f"{layer} guard error: {exc}")


def _response(ctx: RequestContext, answer: str, blocked_by: str | None = None, usage: dict | None = None) -> dict:
    return {
        "answer": answer,
        "blocked": blocked_by is not None,
        "blocked_by": blocked_by,
        "session_id": ctx.session_id,
        "tool_calls": ctx.trace.tool_calls,
        "guard_events": ctx.trace.guard_events,
        "usage": usage or {},
    }


@app.post("/chat")
def chat(body: ChatIn, request: Request) -> dict:
    ctx = RequestContext(role=body.role, client_id=request.client.host if request.client else "local", **({"session_id": body.session_id} if body.session_id else {}))
    set_ctx(ctx)

    r = _guard(runtime_guard.check_request, "runtime", ctx, ctx, body.message)
    if not r.allowed:
        ctx.trace.event("runtime", "blocked", r.reason)
        return _response(ctx, REFUSAL, "runtime")

    r = _guard(input_guard.check, "input", ctx, body.message, ctx)
    if not r.allowed:
        ctx.trace.event("input", "blocked", r.reason)
        return _response(ctx, REFUSAL, "input")
    message = r.text if r.text is not None else body.message

    chunks = rag.retrieve(message, ctx)
    try:
        context_text = data_guard.format_context(chunks)
    except Exception as exc:  # noqa: BLE001
        ctx.trace.event("data", "error", str(exc))
        return _response(ctx, REFUSAL, "data")

    answer, usage = agent.run(message, context_text, ctx)
    try:
        runtime_guard.record_usage(ctx, usage)
    except Exception as exc:  # noqa: BLE001
        ctx.trace.event("runtime", "error", str(exc))

    r = _guard(output_guard.filter, "output", ctx, answer, ctx)
    if not r.allowed:
        ctx.trace.event("output", "blocked", r.reason)
        return _response(ctx, REFUSAL, "output", usage)
    if r.text is not None and r.text != answer:
        ctx.trace.event("output", "rewritten", "answer was modified by the output guard")
    return _response(ctx, r.text if r.text is not None else answer, None, usage)


def _extract(filename: str, raw: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return "\n\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(raw)).pages)
    if ext in (".txt", ".md"):
        return raw.decode("utf-8", errors="replace")
    raise HTTPException(415, "Only .pdf, .txt and .md files are supported")


@app.post("/upload")
async def upload(file: UploadFile = File(...), role: str = "customer") -> dict:
    ctx = RequestContext(role=role)
    set_ctx(ctx)
    raw = await file.read()
    name = Path(file.filename or "upload").name
    text = _extract(name, raw)
    r = _guard(data_guard.screen_document, "data", ctx, text, name, ctx)
    if not r.allowed:
        raise HTTPException(400, f"Upload rejected by data guard: {r.reason}")
    clean = r.text if r.text is not None else text
    (config.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    (config.UPLOAD_DIR / name).write_bytes(raw)
    n = rag.ingest(clean, name, access="public", uploaded=True)
    return {"ingested_chunks": n, "source": name, "guard_events": ctx.trace.guard_events}


@app.get("/approvals")
def list_approvals() -> list[dict]:
    return approvals.list_all()


@app.post("/approvals/{aid}/{action}")
def decide(aid: str, action: str) -> dict:
    if action not in ("approve", "reject"):
        raise HTTPException(400, "action must be approve or reject")
    try:
        return approvals.decide(aid, action == "approve")
    except KeyError:
        raise HTTPException(404, "unknown approval id")


@app.get("/outbox")
def outbox() -> list[dict]:
    import json

    if not config.OUTBOX_PATH.exists():
        return []
    return [json.loads(line) for line in config.OUTBOX_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


@app.post("/admin/reset")
def reset() -> dict:
    """Lab helper: restore the database, clear the outbox and uploads, rebuild the knowledge base."""
    if not config.LAB_MODE:
        raise HTTPException(404)
    seed.seed(reset=True)
    approvals.clear()
    return {"status": "reset", "kb_chunks": rag.load_corpus()}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "llm_mode": config.LLM_MODE, "model": config.OPENAI_MODEL if config.LLM_MODE == "openai" else "fake"}


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")
