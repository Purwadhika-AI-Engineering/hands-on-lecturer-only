"""Skenario gagal yang disengaja: container sementara di port 18xxx (tidak mengganggu container utama)."""
import socket
import uuid

import pytest
import requests

from conftest import AGENT_IMAGE, CV_IMAGE, wait_for_health
from helpers import docker, logs, png_files

pytestmark = [pytest.mark.docker, pytest.mark.slow, pytest.mark.usefixtures("needs_docker")]


@pytest.fixture
def temp_container():
    names = []

    def run(image, host_port, env=None):
        name = f"tmp-{uuid.uuid4().hex[:6]}"
        args = ["run", "-d", "--name", name, "-p", f"{host_port}:8000"]
        for k, v in (env or {}).items():
            args += ["-e", f"{k}={v}"]
        r = docker(*args, image)
        if r.returncode != 0:
            pytest.skip(f"gagal menjalankan {image}: {r.stderr.strip()[:200]}")
        names.append(name)
        return name

    yield run
    for n in names:
        docker("rm", "-f", n)


def test_agent_without_api_key(temp_container):
    """Slide 22/33: tanpa OPENAI_API_KEY -> server hidup, tapi agent_initialized=false."""
    temp_container(AGENT_IMAGE, 18000)
    health = wait_for_health("http://localhost:18000", 60)
    assert health is not None, "server tidak naik"
    assert health["agent_initialized"] is False
    r = requests.post("http://localhost:18000/chat", params={"message": "hi"}, timeout=10)
    assert r.status_code == 500 and "not initialized" in r.json()["detail"]


def test_port_conflict_is_reported():
    """Slide 33: 'Port already allocated' -> docker run harus gagal, bukan diam-diam."""
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
    s.bind(("0.0.0.0", 18001))
    s.listen(1)
    try:
        name = f"tmp-{uuid.uuid4().hex[:6]}"
        r = docker("run", "-d", "--name", name, "-p", "18001:8000", AGENT_IMAGE)
        docker("rm", "-f", name)
        assert r.returncode != 0
        assert any(k in r.stderr.lower() for k in ("already allocated", "address already in use", "not available"))
    finally:
        s.close()


def test_cv_without_model_volume_still_looks_healthy(temp_container):
    """Pelajaran penting: /health hijau TIDAK berarti model benar. Tanpa volume, API memakai bobot acak."""
    name = temp_container(CV_IMAGE, 18002)
    assert wait_for_health("http://localhost:18002", 150) is not None
    assert "Model not found" in logs(name), "image seharusnya tidak membawa model (cek mlops-cv/.dockerignore)"
    r = requests.post("http://localhost:18002/predict", files=png_files(), timeout=60)
    assert r.status_code == 200  # tetap menjawab, walau prediksinya tidak bermakna
