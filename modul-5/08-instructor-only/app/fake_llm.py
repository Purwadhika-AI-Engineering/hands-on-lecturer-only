"""OFFLINE STAND-IN for a real model. For plumbing checks and guard unit tests only.

PuppetChatModel is deliberately GULLIBLE: it obeys whatever instructions appear in the prompt,
including injected ones, so we can test that YOUR guards stop the damage. A real LLM is less
predictable (sometimes it refuses, sometimes it is fooled in new ways). Passing tests in fake mode
means "my guards work", NOT "my app is safe". Always verify against the real model too.
"""
from __future__ import annotations

import base64
import re
import uuid
import zlib

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

_EMAIL = r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"


class KeywordEmbeddings(Embeddings):
    """Hashed bag-of-words vectors: lexical overlap ~ similarity. Good enough to retrieve the right doc offline."""

    dim = 512

    def _vec(self, text: str) -> list[float]:
        v = [0.0] * self.dim
        for tok in re.findall(r"[a-z0-9]+", text.lower()):
            v[zlib.crc32(tok.encode()) % self.dim] += 1.0
        norm = sum(x * x for x in v) ** 0.5 or 1.0
        return [x / norm for x in v]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vec(text)


def _question(full: str) -> str:
    i = full.rfind("Question:")
    return full[i + 9 :].strip() if i != -1 else full


def _plan(full: str):
    """Return (mode, steps). steps are callables(prev_results) -> (tool_name, args)."""
    q = _question(full)
    eff = q
    if "base64" in q.lower():
        for tok in re.findall(r"[A-Za-z0-9+/]{20,}={0,2}", q):
            try:
                eff += " " + base64.b64decode(tok).decode("utf-8", "ignore")
            except Exception:
                pass
    low = eff.lower()

    inj = re.search(rf"send_email tool to send.*?\bto\s+({_EMAIL})", full, re.I | re.S)
    if inj:
        to = inj.group(1)
        return "tools", [
            lambda r: ("sql_query", {"query": "SELECT name, email, phone FROM customers"}),
            lambda r: ("send_email", {"to": to, "subject": "Customer export", "body": (r[0] if r else "")[:1500]}),
        ]
    if re.search(r"system prompt|prompt sistem|instruksi|instructions|your rules|initial prompt", low) and re.search(
        r"ignore|abaikan|reveal|show|print|tampilkan|tunjukkan|repeat|ulangi|what are|apa", low
    ):
        return "leak", []
    m = re.search(r"(/proc/[\w./-]+|(?:/|\.\./|data/)[\w./-]*\.\w+)", eff)
    if m and re.search(r"read|file|baca|open|isi|show|cat", low):
        return "tools", [lambda r: ("read_file", {"path": m.group(1)})]
    if re.search(r"salary|salaries|gaji", low):
        return "tools", [lambda r: ("sql_query", {"query": "SELECT name, role, salary_idr FROM employees"})]
    if re.search(r"drop table|delete all|hapus semua|truncate", low):
        return "tools", [lambda r: ("sql_query", {"query": "DELETE FROM orders"})]
    if re.search(r"set the price|change the price|ubah harga|update the price", low):
        return "tools", [lambda r: ("sql_query", {"query": "UPDATE products SET price_idr = 1000 WHERE id = 1"})]
    e = re.search(rf"(?:send|kirim).*?e-?mail.*?\bto\s+({_EMAIL})", eff, re.I | re.S)
    if e:
        return "tools", [lambda r: ("send_email", {"to": e.group(1), "subject": "Message from AcmeBot", "body": q[:300]})]
    if re.search(r"(contact|email|phone|nomor|telepon|alamat|nik).*(customer|pelanggan)|(customer|pelanggan).*(contact|email|phone|nik|nomor)", low):
        return "tools", [lambda r: ("sql_query", {"query": "SELECT name, email, phone, nik FROM customers WHERE id = 3"})]
    if re.search(r"how many.*order|berapa.*pesanan|pending orders", low):
        return "tools", [lambda r: ("sql_query", {"query": "SELECT COUNT(*) AS pending_orders FROM orders WHERE status = 'pending'"})]
    return "chat", []


class PuppetChatModel(BaseChatModel):
    @property
    def _llm_type(self) -> str:
        return "puppet"

    def bind_tools(self, tools, **kwargs):  # tools are chosen by the script, not by the model
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        last_h = max(i for i, m in enumerate(messages) if isinstance(m, HumanMessage))
        full = messages[last_h].content if isinstance(messages[last_h].content, str) else str(messages[last_h].content)
        results = [m.content for m in messages[last_h + 1 :] if isinstance(m, ToolMessage)]
        mode, steps = _plan(full)
        usage = {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}
        if len(results) < len(steps):
            name, args = steps[len(results)](results)
            msg = AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": f"call_{uuid.uuid4().hex[:8]}", "type": "tool_call"}], usage_metadata=usage)
        elif mode == "leak":
            sys_msgs = [m for m in messages if isinstance(m, SystemMessage)]
            msg = AIMessage(content=str(sys_msgs[0].content) if sys_msgs else "I have no system prompt.", usage_metadata=usage)
        elif results:
            msg = AIMessage(content="Here is what I found: " + " | ".join(str(r)[:600] for r in results), usage_metadata=usage)
        else:
            ctx = full.split("Question:")[0].replace("Context:", "").strip()
            body = re.sub(r"\s+", " ", ctx)[:400] if ctx else ""
            msg = AIMessage(content=(f"Based on our documents: {body}" if body else "Hello! How can I help you today?"), usage_metadata=usage)
        return ChatResult(generations=[ChatGeneration(message=msg)])
