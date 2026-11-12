"""Model factory. Real OpenAI models by default; a scripted fake for offline plumbing checks."""
from __future__ import annotations

from app import config

_override = None  # tests may inject a model


def set_model_override(model) -> None:
    global _override
    _override = model


def get_chat_model(max_output_tokens: int | None = None):
    if _override is not None:
        return _override
    if config.LLM_MODE == "fake":
        from app.fake_llm import PuppetChatModel

        return PuppetChatModel()
    from langchain_openai import ChatOpenAI

    kwargs: dict = {"model": config.OPENAI_MODEL}
    if max_output_tokens:
        kwargs["max_tokens"] = max_output_tokens
    if config.OPENAI_MODEL.startswith("gpt-5"):
        kwargs["reasoning_effort"] = config.OPENAI_REASONING_EFFORT  # keeps classroom latency low
    return ChatOpenAI(**kwargs)


def get_embeddings():
    if config.LLM_MODE == "fake":
        from app.fake_llm import KeywordEmbeddings

        return KeywordEmbeddings()
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(model=config.EMBEDDING_MODEL)
