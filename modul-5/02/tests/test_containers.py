"""Tes level container: yang tidak bisa dilihat dari API saja (docker inspect, exec, logs, stats)."""
import time

import pytest
import requests

from conftest import (AGENT_CONTAINER, AGENT_IMAGE, AGENT_URL, CV_CONTAINER, CV_IMAGE, CV_URL,
                      wait_for_health)
from helpers import container_exists, docker, inspect, logs, parse_mem_usage

pytestmark = [pytest.mark.docker, pytest.mark.usefixtures("needs_docker")]

SERVICES = [
    pytest.param(AGENT_CONTAINER, AGENT_IMAGE, id="agent"),
    pytest.param(CV_CONTAINER, CV_IMAGE, id="cv"),
]
MB = 1024 ** 2


def require_container(name):
    if not container_exists(name):
        pytest.skip(f"container '{name}' tidak ada (belum dijalankan / nama berbeda)")


@pytest.mark.parametrize("container,image", SERVICES)
def test_container_is_running(container, image):
    require_container(container)
    assert inspect(container, "{{.State.Running}}") == "true"


@pytest.mark.parametrize("container,image", SERVICES)
def test_port_is_published(container, image):
    require_container(container)
    r = docker("port", container, "8000/tcp")
    assert r.returncode == 0 and r.stdout.strip(), "port 8000 container belum dipetakan ke host (-p)"


@pytest.mark.parametrize("container,image", SERVICES)
def test_container_becomes_healthy(container, image):
    require_container(container)
    if inspect(container, "{{if .State.Health}}yes{{end}}") != "yes":
        pytest.skip("image ini tidak punya HEALTHCHECK")
    status = ""
    for _ in range(60):  # maksimal ~2 menit (TensorFlow lambat start)
        status = inspect(container, "{{.State.Health.Status}}")
        if status == "healthy":
            return
        time.sleep(2)
    last = inspect(container, "{{json .State.Health.Log}}")
    pytest.fail(f"status terakhir: {status}. Log healthcheck: {last[:400]}")


@pytest.mark.parametrize("container,image", SERVICES)
def test_logs_show_server_started(container, image):
    require_container(container)
    assert "Uvicorn running" in logs(container)


@pytest.mark.parametrize("container,image", SERVICES)
def test_image_has_no_baked_secret(container, image):
    r = docker("image", "inspect", "--format", "{{json .Config.Env}}", image)
    if r.returncode != 0:
        pytest.skip(f"image '{image}' tidak ditemukan")
    assert "OPENAI_API_KEY" not in r.stdout, "API key ter-bake di image! Kirim lewat -e saat docker run"
    hist = docker("history", "--no-trunc", image).stdout
    assert "OPENAI_API_KEY=" not in hist and "sk-" not in hist


def test_agent_runs_as_non_root():
    require_container(AGENT_CONTAINER)
    r = docker("exec", AGENT_CONTAINER, "id", "-un")
    assert r.stdout.strip() == "appuser"


@pytest.mark.xfail(reason="Tantangan D2: Dockerfile CV belum membuat user non-root. Perbaiki -> tes ini jadi XPASS.")
def test_cv_runs_as_non_root():
    require_container(CV_CONTAINER)
    assert docker("exec", CV_CONTAINER, "id", "-un").stdout.strip() != "root"


@pytest.mark.parametrize("container,image,limit_mb", [
    pytest.param(AGENT_CONTAINER, AGENT_IMAGE, 1500, id="agent"),
    pytest.param(CV_CONTAINER, CV_IMAGE, 5000, id="cv"),
])
def test_image_size_budget(container, image, limit_mb):
    r = docker("image", "inspect", "--format", "{{.Size}}", image)
    if r.returncode != 0:
        pytest.skip(f"image '{image}' tidak ditemukan")
    size_mb = int(r.stdout.strip()) / MB
    print(f"\nukuran image {image}: {size_mb:.0f} MB")
    assert size_mb < limit_mb


@pytest.mark.parametrize("container,limit_mb", [
    pytest.param(AGENT_CONTAINER, 800, id="agent"),
    pytest.param(CV_CONTAINER, 3000, id="cv"),
])
def test_memory_budget(container, limit_mb):
    require_container(container)
    r = docker("stats", "--no-stream", "--format", "{{.MemUsage}}", container)
    used = parse_mem_usage(r.stdout) / MB
    print(f"\nmemori {container}: {used:.0f} MiB")
    assert used < limit_mb


def test_cv_model_file_present():
    require_container(CV_CONTAINER)
    r = docker("exec", CV_CONTAINER, "ls", "/app/models")
    if "cifar10_model.h5" not in r.stdout:
        pytest.xfail("Model belum dilatih / belum di-mount: API tetap jalan dengan bobot ACAK (prediksi tidak bermakna)")


@pytest.mark.slow
def test_cv_survives_restart():
    require_container(CV_CONTAINER)
    assert docker("restart", CV_CONTAINER, timeout=120).returncode == 0
    assert wait_for_health(CV_URL, 120) is not None, "CV API tidak kembali sehat setelah restart"
    from helpers import png_files
    r = requests.post(f"{CV_URL}/predict", files=png_files(), timeout=60)
    assert r.status_code == 200


@pytest.mark.slow
@pytest.mark.llm
def test_agent_forgets_history_after_restart(agent_ready):
    """Pertanyaan diskusi slide 36: memory agent hidup di dalam proses, bukan di disk."""
    require_container(AGENT_CONTAINER)
    if not agent_ready:
        pytest.skip("agent belum terinisialisasi (butuh API key)")
    requests.post(f"{AGENT_URL}/reset", timeout=10)
    requests.post(f"{AGENT_URL}/chat", params={"message": "My name is Budi."}, timeout=90)
    assert "Budi" in requests.get(f"{AGENT_URL}/history", timeout=10).json()["chat_history"]
    assert docker("restart", AGENT_CONTAINER, timeout=120).returncode == 0
    assert wait_for_health(AGENT_URL, 90) is not None
    hist = requests.get(f"{AGENT_URL}/history", timeout=10).json()["chat_history"]
    assert "Budi" not in hist, "riwayat chat seharusnya hilang setelah container restart"
