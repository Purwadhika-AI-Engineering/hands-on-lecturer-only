"""Minimal RAG: chunk -> embed -> in-memory vector store -> similarity search."""
from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

from app import config
from app.context import RequestContext
from app.guards import data_guard
from app.llm import get_embeddings

_store: InMemoryVectorStore | None = None


def chunk_text(text: str, size: int = 700) -> list[str]:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if cur and len(cur) + len(p) > size:
            chunks.append(cur)
            cur = p
        else:
            cur = f"{cur}\n\n{p}" if cur else p
    if cur:
        chunks.append(cur)
    return chunks or ([text.strip()] if text.strip() else [])


def reset_store() -> None:
    global _store
    _store = InMemoryVectorStore(get_embeddings())


def store() -> InMemoryVectorStore:
    if _store is None:
        reset_store()
    return _store  # type: ignore[return-value]


def ingest(text: str, source: str, access: str = "public", uploaded: bool = False) -> int:
    docs = [Document(page_content=c, metadata={"source": source, "access": access, "uploaded": uploaded}) for c in chunk_text(text)]
    if docs:
        store().add_documents(docs)
    return len(docs)


def load_corpus() -> int:
    """Index the shop's own documents. The folder name decides the access level."""
    reset_store()
    n = 0
    for path in sorted((config.DATA_DIR / "docs").rglob("*.md")):
        access = "internal" if path.parent.name == "internal" else "public"
        n += ingest(path.read_text(encoding="utf-8"), path.name, access)
    return n


def retrieve(query: str, ctx: RequestContext, k: int = 3) -> list[Document]:
    docs = store().similarity_search(query, k=k * 3)  # over-fetch: guards may remove some
    docs = data_guard.filter_chunks(docs, ctx)
    return docs[:k]
