# Lab 1: Containerize LLM Agent (menit 10-35, 25 menit)

**Hasil:** container `llm-agent` berjalan di port 8000 dan menjawab `/chat`.
**Model hidup di OpenAI**, container hanya berisi kode agent + API.

> Perintah di bawah memakai sintaks bash. Di PowerShell Windows pakai `curl.exe` (bukan `curl`), atau gunakan Swagger UI di `/docs`.

## A1. Kenali kode (3 menit)
**Di mana:** folder `mlops-ai-agent-handson/`.
1. Buka `agent.py`: temukan LLM, 2 Tool, dan Memory. Buka `app.py`: temukan `/chat`, `/health`, `/history`, `/reset`.
2. Buka `Dockerfile` dan cocokkan tiap baris dengan slide 23-24.

**Yang harus terlihat:** Anda bisa menjawab: *API key dibaca dari mana?* (environment variable `OPENAI_API_KEY`).

## A2. Tes lokal dulu (6 menit)
```bash
cd mlops-ai-agent-handson
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."                    # Windows PowerShell: $env:OPENAI_API_KEY="sk-..."
python app.py
```
Buka http://localhost:8000/docs.

**Yang harus terlihat:** `GET /health` -> `{"status":"healthy","agent_initialized":true}`.
**Kalau tidak:** `agent_initialized: false` berarti key tidak terbaca (set ulang di terminal yang sama). `ImportError ... RAW_SCHEMA_QUERY` berarti `requirements.txt` lama dipakai; pastikan pin `langchain-community==0.0.2` ada.
> 📸 **SS-A-2**: Swagger UI `/docs` dengan `/health` true.

Hentikan server (Ctrl+C), lalu `cd ..` dan `deactivate`.

## A3. Build image (4 menit)
```bash
docker build -t llm-agent-service ./mlops-ai-agent-handson
docker images llm-agent-service
```
**Yang harus terlihat:** image `llm-agent-service` di daftar, ukuran sekitar 1 GB.
**Kalau tidak:** `requirements.txt not found` berarti Anda salah folder; jalankan dari root repo.
> 📸 **SS-A-3**: output `docker images`.

**Tanya diri sendiri:** ubah satu baris di `app.py` lalu build ulang; langkah mana yang memakai `CACHED`?

## A4. Jalankan container (3 menit)
```bash
docker run -d --name llm-agent -p 8000:8000 -e OPENAI_API_KEY="sk-..." llm-agent-service
docker ps
docker logs llm-agent
```
**Yang harus terlihat:** `docker ps` menampilkan `llm-agent`; log berisi `Agent initialized successfully!` dan `Uvicorn running on http://0.0.0.0:8000`.
**Kalau tidak:** `port is already allocated` -> hentikan server lokal A2 atau pakai `-p 8080:8000`. Container langsung `Exited` -> baca `docker logs llm-agent`.
> 📸 **SS-A-4**: `docker ps` + log startup.

## A5. Uji agent (5 menit)
```bash
curl http://localhost:8000/health
curl -X POST "http://localhost:8000/chat?message=Calculate+15*23"
curl http://localhost:8000/history
curl -X POST http://localhost:8000/reset
```
**Yang harus terlihat:** jawaban agent berisi `345`, dan `/history` memuat percakapan.
**Kalau tidak:** `"agent_response":"Error processing message: ..."` padahal `status` tetap `success`. Itu error dari OpenAI (key salah, saldo habis, model tidak tersedia); lihat `docker logs llm-agent`.
> 📸 **SS-A-5**: jawaban `/chat` berisi 345.

## A6. Periksa kesehatan container (2 menit)
```bash
docker ps          # kolom STATUS: tunggu "(healthy)" sekitar 30 detik
docker inspect --format "{{.State.Health.Status}}" llm-agent
```
**Yang harus terlihat:** `healthy`.
**Kalau tidak:** `unhealthy` terus menerus berarti `curl` tidak ada di image (Dockerfile versi lama). Di repo ini `curl` sudah ditambahkan.

### Done when
- [ ] `/chat` menjawab 345 dari container
- [ ] `docker ps` menampilkan `(healthy)`
- [ ] Anda bisa menjelaskan kenapa key dikirim dengan `-e`, bukan ditulis di kode/image
