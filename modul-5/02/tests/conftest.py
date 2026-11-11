"""Konfigurasi bersama. Semua nilai bisa diubah lewat environment variable."""
import os
import time

import pytest
import requests

from helpers import docker_available

AGENT_URL = os.getenv("AGENT_URL", "http://localhost:8000")
CV_URL = os.getenv("CV_URL", "http://localhost:8001")
AGENT_CONTAINER = os.getenv("AGENT_CONTAINER", "llm-agent")
CV_CONTAINER = os.getenv("CV_CONTAINER", "cv-api")
AGENT_IMAGE = os.getenv("AGENT_IMAGE", "llm-agent-service")
CV_IMAGE = os.getenv("CV_IMAGE", "cv-api")


def wait_for_health(url: str, timeout: int = 60):
    """Tunggu sampai GET /health menjawab 200; kembalikan JSON-nya atau None."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{url}/health", timeout=5)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(2)
    return None


@pytest.fixture(scope="session")
def agent_url():
    if wait_for_health(AGENT_URL, 20) is None:
        pytest.fail(f"Agent tidak bisa dijangkau di {AGENT_URL}. Cek: docker ps, docker logs {AGENT_CONTAINER}, "
                    f"dan pemetaan port (-p 8000:8000).")
    return AGENT_URL


@pytest.fixture(scope="session")
def cv_url():
    if wait_for_health(CV_URL, 20) is None:
        pytest.fail(f"CV API tidak bisa dijangkau di {CV_URL}. Cek: docker ps, docker logs {CV_CONTAINER}, "
                    f"dan pemetaan port (-p 8001:8000).")
    return CV_URL


@pytest.fixture(scope="session")
def agent_ready(agent_url):
    """True bila agent berhasil dibuat (OPENAI_API_KEY terbaca)."""
    return bool(requests.get(f"{agent_url}/health", timeout=10).json().get("agent_initialized"))


@pytest.fixture
def needs_agent(agent_ready):
    if not agent_ready:
        pytest.skip("agent_initialized=false: jalankan container dengan -e OPENAI_API_KEY=...")


@pytest.fixture(scope="session")
def needs_docker():
    if not docker_available():
        pytest.skip("Docker CLI tidak tersedia / daemon tidak jalan")
