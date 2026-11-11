# Tests untuk Hasil Deployment

```bash
pip install -r requirements.txt
pytest -m "agent or cv" -v            # kontrak API (butuh container jalan)
pytest -m "docker and not slow" -v    # inspeksi container (butuh Docker CLI)
pytest -m slow -v                     # skenario gagal + restart (3-5 menit)
python load_test.py --requests 40 --concurrency 4
```
Lewati tes berbayar: `pytest -m "not llm"`. Ganti target: `AGENT_URL`, `CV_URL`, `AGENT_CONTAINER`, `CV_CONTAINER`, `AGENT_IMAGE`, `CV_IMAGE`, `CV_LATENCY_BUDGET_S`.
Tidak butuh TensorFlow/LangChain: tes hanya bicara HTTP dan Docker CLI.
