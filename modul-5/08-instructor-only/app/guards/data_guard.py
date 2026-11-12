"""LAYER 2 - DATA / RAG GUARD  (OWASP LLM01 indirect injection, LLM05 Poisoning, LLM09 Vector & Embedding)

Three hooks. Retrieved text is DATA, never instructions.

1. screen_document(): runs when a file is uploaded, before it is indexed.
   Starter: accepts everything, including hidden text.
   Ideas: strip invisible / zero-width characters, detect instruction-like text
   ("ignore previous instructions", "use the send_email tool"), quarantine suspicious files.

2. filter_chunks(): runs after similarity search, before anything is shown to the model.
   Starter: returns every chunk, including internal-only documents, for every user.
   Ideas: access control by role. A "customer" must never receive chunks marked access="internal".

3. format_context(): turns chunks into the text placed in the prompt.
   Starter: raw concatenation, so the model cannot tell data from instructions.
   Ideas: wrap each chunk in clearly delimited untrusted-data blocks, add a reminder that
   content inside is reference material only, include the source name so answers can cite it.
"""
from langchain_core.documents import Document

from app.context import RequestContext
from app.guards import GuardResult


def screen_document(text: str, source: str, ctx: RequestContext) -> GuardResult:
    # TODO (Lab step 2, Layer 2): implement.
    return GuardResult(allowed=True, text=text)


def filter_chunks(chunks: list[Document], ctx: RequestContext) -> list[Document]:
    # TODO (Lab step 2, Layer 2): enforce access control (chunk.metadata["access"]).
    return chunks


def format_context(chunks: list[Document]) -> str:
    # TODO (Lab step 2, Layer 2): delimit retrieved content as untrusted data.
    return "\n\n".join(c.page_content for c in chunks)
