"""Tes kontrak API untuk container computer vision (port 8001)."""
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
import requests

from helpers import CIFAR10_CLASSES, jpeg_files, make_image, png_files

pytestmark = pytest.mark.cv
LATENCY_BUDGET_S = float(os.getenv("CV_LATENCY_BUDGET_S", "5"))


def predict(url, files, timeout=60):
    return requests.post(f"{url}/predict", files=files, timeout=timeout)


def test_root_and_health(cv_url):
    assert requests.get(f"{cv_url}/", timeout=10).status_code == 200
    assert requests.get(f"{cv_url}/health", timeout=10).json() == {"status": "healthy"}


def test_predict_png_schema(cv_url):
    r = predict(cv_url, png_files())
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "success" and body["filename"] == "test.png"
    p = body["prediction"]
    assert p["class"] in CIFAR10_CLASSES
    assert 0.0 <= p["confidence"] <= 1.0
    assert set(p["all_predictions"]) == set(CIFAR10_CLASSES)
    assert abs(sum(p["all_predictions"].values()) - 1.0) < 1e-3, "probabilitas softmax harus berjumlah 1"
    assert p["confidence"] == pytest.approx(max(p["all_predictions"].values()))


def test_predict_jpeg(cv_url):
    assert predict(cv_url, jpeg_files()).status_code == 200


@pytest.mark.parametrize("kw", [
    {"mode": "L"},                      # grayscale
    {"mode": "RGBA"},                   # transparansi
    {"mode": "P"},                      # palette
    {"size": (8, 8)},                   # sangat kecil
    {"size": (2000, 1500)},             # besar (di-resize ke 224x224)
], ids=["grayscale", "rgba", "palette", "tiny", "large"])
def test_predict_image_variants(cv_url, kw):
    assert predict(cv_url, png_files(**kw)).status_code == 200


def test_predict_is_deterministic(cv_url):
    files = lambda: png_files(color=(10, 90, 200))
    a = predict(cv_url, files()).json()["prediction"]
    b = predict(cv_url, files()).json()["prediction"]
    assert a["class"] == b["class"]
    assert a["confidence"] == pytest.approx(b["confidence"], abs=1e-5)


def test_non_image_upload_is_400(cv_url):
    r = predict(cv_url, {"file": ("catatan.txt", b"ini bukan gambar", "text/plain")})
    assert r.status_code == 400
    assert r.json()["status"] == "error"


def test_empty_file_is_400(cv_url):
    assert predict(cv_url, {"file": ("kosong.png", b"", "image/png")}).status_code == 400


def test_missing_file_is_422(cv_url):
    assert requests.post(f"{cv_url}/predict", timeout=10).status_code == 422


def test_wrong_field_name_is_422(cv_url):
    files = {"image": ("test.png", make_image(), "image/png")}  # seharusnya "file"
    assert predict(cv_url, files).status_code == 422


def test_get_predict_not_allowed(cv_url):
    assert requests.get(f"{cv_url}/predict", timeout=10).status_code == 405


def test_latency_warm(cv_url):
    predict(cv_url, png_files())  # pemanasan (request pertama lebih lambat)
    times = []
    for _ in range(5):
        t = time.perf_counter()
        assert predict(cv_url, png_files()).status_code == 200
        times.append(time.perf_counter() - t)
    med = statistics.median(times)
    print(f"\nlatensi median (warm): {med * 1000:.0f} ms")
    assert med < LATENCY_BUDGET_S, f"median {med:.2f}s melewati anggaran {LATENCY_BUDGET_S}s"


def test_concurrent_requests(cv_url):
    with ThreadPoolExecutor(max_workers=6) as ex:
        codes = list(ex.map(lambda _: predict(cv_url, png_files(), timeout=120).status_code, range(12)))
    assert codes == [200] * 12
