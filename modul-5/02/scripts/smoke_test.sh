#!/usr/bin/env bash
# Smoke test cepat tanpa Python. Untuk macOS / Linux / WSL / Git Bash.
# Pakai:  bash scripts/smoke_test.sh        (AGENT_URL / CV_URL bisa diganti lewat env)
AGENT_URL="${AGENT_URL:-http://localhost:8000}"
CV_URL="${CV_URL:-http://localhost:8001}"
SAMPLE="$(dirname "$0")/../samples/merah.png"
pass=0; fail=0

check() {  # check "nama" "perintah curl" "teks yang harus ada"
  out=$(eval "$2" 2>&1)
  if echo "$out" | grep -q "$3"; then echo "PASS  $1"; pass=$((pass+1))
  else echo "FAIL  $1"; echo "      jawaban: ${out:0:160}"; fail=$((fail+1)); fi
}

check "agent  GET /health"          "curl -s -m 10 $AGENT_URL/health"  '"status":"healthy"'
check "agent  POST /chat tanpa msg" "curl -s -m 10 -o /dev/null -w %{http_code} -X POST $AGENT_URL/chat" '422'
check "cv     GET /health"          "curl -s -m 10 $CV_URL/health"     '"status":"healthy"'
check "cv     POST /predict gambar" "curl -s -m 60 -X POST $CV_URL/predict -F file=@$SAMPLE" '"status":"success"'
check "cv     POST /predict teks"   "curl -s -m 60 -o /dev/null -w %{http_code} -X POST $CV_URL/predict -F file=@$0" '400'

echo "----"; echo "lulus: $pass   gagal: $fail"
[ "$fail" -eq 0 ]
