# Troubleshooting

Kebiasaan pertama: **`docker logs <nama-container>`**.

| Gejala | Kemungkinan penyebab | Coba |
|---|---|---|
| `Cannot connect to the Docker daemon` | Docker Desktop belum jalan | Buka Docker Desktop, tunggu siap |
| `port is already allocated` | Port host dipakai | Ganti `-p 8080:8000`, atau `docker ps` lalu `docker rm -f` yang lama |
| `container name ... already in use` | Nama container masih ada | `docker rm -f <nama>` |
| Container langsung `Exited` | Error saat startup | `docker logs <nama>` |
| `agent_initialized: false` | `OPENAI_API_KEY` tidak dikirim | `docker run ... -e OPENAI_API_KEY=...` |
| `/chat` 200 tapi isi `Error processing message` | Error dari OpenAI (key, saldo, model) | `docker logs llm-agent`; coba `-e OPENAI_MODEL=<model lain>` |
| `ImportError ... RAW_SCHEMA_QUERY` | `requirements.txt` tanpa pin `langchain-community` | Pakai `requirements.txt` repo ini |
| Status `unhealthy` (agent) | `curl` tidak ada di image | Pakai Dockerfile repo ini |
| Status `starting` lama (CV) | TensorFlow lambat start | Tunggu hingga ±60 detik |
| Prediksi CV selalu sama / acak | Model belum dilatih / volume tidak ter-mount | Lab 2 B6; cek `-v` dan `docker exec cv-api ls /app/models` |
| `422` di `/predict` | Nama field bukan `file` | Pakai `-F file=@gambar.png` |
| `curl` di PowerShell aneh | `curl` adalah alias `Invoke-WebRequest` | Pakai `curl.exe` atau Swagger `/docs` |
| `no space left on device` | Disk Docker penuh | `docker system prune` |
| Out of memory / container mati sendiri | RAM Docker kecil | Docker Desktop > Settings > Resources > Memory ≥ 4 GB |
| Build TensorFlow sangat lama | Koneksi lambat, banyak peserta | Mulai build lebih awal (Lab 0 S5), atau minta pengajar membagikan image |
| `exec format error` / crash di Mac M-series | Image platform amd64 dijalankan di arm64 | Jangan paksa `--platform linux/amd64` |
