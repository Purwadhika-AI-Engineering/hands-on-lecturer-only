"""Load test mini untuk CV API.  Contoh:  python load_test.py --requests 40 --concurrency 4"""
import argparse
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from helpers import make_image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8001")
    ap.add_argument("--requests", type=int, default=30)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--p95-budget", type=float, default=0, help="detik; 0 = tidak dicek")
    a = ap.parse_args()

    img = make_image()
    requests.post(f"{a.url}/predict", files={"file": ("w.png", img, "image/png")}, timeout=120)  # warm-up

    def one(_):
        t = time.perf_counter()
        try:
            code = requests.post(f"{a.url}/predict", files={"file": ("x.png", img, "image/png")}, timeout=120).status_code
        except requests.RequestException:
            code = 0
        return code, time.perf_counter() - t

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        res = list(ex.map(one, range(a.requests)))
    wall = time.perf_counter() - t0

    lat = sorted(t for _, t in res)
    errors = sum(1 for c, _ in res if c != 200)
    p95 = lat[max(0, int(len(lat) * 0.95) - 1)]
    print(f"request      : {a.requests} (concurrency {a.concurrency})")
    print(f"error        : {errors}")
    print(f"throughput   : {a.requests / wall:.1f} req/s")
    print(f"latensi p50  : {statistics.median(lat) * 1000:.0f} ms")
    print(f"latensi p95  : {p95 * 1000:.0f} ms")
    print(f"latensi max  : {lat[-1] * 1000:.0f} ms")
    if errors or (a.p95_budget and p95 > a.p95_budget):
        sys.exit(1)


if __name__ == "__main__":
    main()
