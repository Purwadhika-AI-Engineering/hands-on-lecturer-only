#!/usr/bin/env python3
"""Compare two promptfoo result files: pass-rate per OWASP category, before vs after.

Usage: python3 scripts/compare.py promptfoo/results/before.json promptfoo/results/after.json
"""
import json
import sys
from collections import defaultdict


def load(path):
    rows = json.load(open(path))["results"]["results"]
    by_metric = defaultdict(lambda: [0, 0])
    for r in rows:
        asserts = r.get("testCase", {}).get("assert") or [{}]
        metric = asserts[0].get("metric", "other")
        by_metric[metric][1] += 1
        by_metric[metric][0] += 1 if r.get("success") else 0
    failed = [r["testCase"].get("description", "?") for r in rows if not r.get("success")]
    return by_metric, failed


def main(a, b):
    before, _ = load(a)
    after, failed_after = load(b)
    metrics = list(dict.fromkeys([*before, *after]))
    w = max(len(m) for m in metrics) + 2
    print(f"{'Category'.ljust(w)} {'Before':>8} {'After':>8}")
    print("-" * (w + 18))
    tb = ta = tn = 0
    for m in metrics:
        pb, nb = before.get(m, [0, 0])
        pa, na = after.get(m, [0, 0])
        tb, ta, tn = tb + pb, ta + pa, tn + na
        print(f"{m.ljust(w)} {f'{pb}/{nb}':>8} {f'{pa}/{na}':>8}")
    print("-" * (w + 18))
    print(f"{'TOTAL'.ljust(w)} {f'{tb}/{tn}':>8} {f'{ta}/{tn}':>8}   ({100 * tb // max(tn, 1)}% -> {100 * ta // max(tn, 1)}%)")
    if failed_after:
        print("\nStill failing (your residual risk to explain in the report):")
        for d in failed_after:
            print("  -", d)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
