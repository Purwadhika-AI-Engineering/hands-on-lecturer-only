"""Tes kontrak API untuk container LLM agent (port 8000)."""
import pytest
import requests

pytestmark = pytest.mark.agent


def test_root(agent_url):
    r = requests.get(f"{agent_url}/", timeout=10)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert set(body["endpoints"]) >= {"chat", "health", "history"}


def test_health_shape(agent_url):
    body = requests.get(f"{agent_url}/health", timeout=10).json()
    assert body["status"] == "healthy"
    assert isinstance(body["agent_initialized"], bool)


def test_agent_is_initialized(agent_ready):
    if not agent_ready:
        pytest.skip("agent_initialized=false -> API key tidak terbaca (lihat Lab 3, skenario tanpa key)")


def test_chat_requires_message(agent_url):
    # 'message' adalah query parameter, bukan JSON body -> tanpa itu FastAPI menjawab 422
    r = requests.post(f"{agent_url}/chat", timeout=10)
    assert r.status_code == 422


def test_unknown_route_is_404(agent_url):
    assert requests.get(f"{agent_url}/tidak-ada", timeout=10).status_code == 404


def test_reset_then_history_empty(agent_url, needs_agent):
    assert requests.post(f"{agent_url}/reset", timeout=10).json()["status"] == "success"
    hist = requests.get(f"{agent_url}/history", timeout=10).json()
    assert hist["status"] == "success"
    assert "No conversation history" in hist["chat_history"]


@pytest.mark.llm
def test_chat_calculator(agent_url, needs_agent):
    requests.post(f"{agent_url}/reset", timeout=10)
    r = requests.post(f"{agent_url}/chat", params={"message": "Calculate 15*23"}, timeout=90)
    assert r.status_code == 200
    answer = r.json()["agent_response"]
    # PERHATIAN: status "success" bisa berbohong. agent.chat() menangkap error dan
    # mengembalikannya sebagai teks, jadi HTTP 200 tetap muncul walau OpenAI menolak.
    assert not answer.startswith("Error processing message"), f"LLM gagal dipanggil: {answer}"
    assert "345" in answer


@pytest.mark.llm
def test_history_records_conversation(agent_url, needs_agent):
    requests.post(f"{agent_url}/reset", timeout=10)
    requests.post(f"{agent_url}/chat", params={"message": "Calculate 15*23"}, timeout=90)
    hist = requests.get(f"{agent_url}/history", timeout=10).json()["chat_history"]
    assert "Human:" in hist and "AI:" in hist
    assert "15" in hist


@pytest.mark.llm
def test_agent_remembers_within_session(agent_url, needs_agent):
    requests.post(f"{agent_url}/reset", timeout=10)
    requests.post(f"{agent_url}/chat", params={"message": "My name is Budi."}, timeout=90)
    r = requests.post(f"{agent_url}/chat", params={"message": "What is my name?"}, timeout=90)
    assert "Budi" in r.json()["agent_response"]
