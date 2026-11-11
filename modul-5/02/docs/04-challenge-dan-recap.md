# Mini Challenge & Recap (menit 80-90)

## D1. Tambah Tool baru (wajib, 7 menit) - challenge slide 35
1. Di `mlops-ai-agent-handson/agent.py` tambahkan Tool `Word Counter` (mis. fungsi yang menghitung kata) ke daftar `self.tools`.
2. **Build ulang** image, hentikan container lama, jalankan di **port 8080**:
```bash
docker build -t llm-agent-service ./mlops-ai-agent-handson
docker rm -f llm-agent
docker run -d --name llm-agent -p 8080:8000 -e OPENAI_API_KEY="sk-..." llm-agent-service
```
3. Buka http://localhost:8080/docs dan panggil `/chat` yang memicu tool baru. Jalankan ulang tes dengan `AGENT_URL=http://localhost:8080 pytest -m agent`.

**Yang harus terlihat:** jawaban memakai tool baru; tes tetap lulus.
**Kalau tidak:** jawaban lama muncul berarti image belum di-build ulang (container lama tidak ikut berubah).

## D2. Bonus: container CV non-root
Tes `test_cv_runs_as_non_root` sedang XFAIL. Ubah `mlops-cv/Dockerfile` (contoh Dockerfile agent: `adduser` + `USER`), build ulang, jalankan ulang tes. Hasil yang diharapkan: **XPASS**.

## Recap
Alur: **kode -> Dockerfile -> image -> container -> client -> tes**.
- Tes lokal dulu, baru Docker. Rahasia lewat `-e`, bukan ke image.
- Model remote (agent) vs model lokal (CV): beda soal volume, ukuran image, startup.
- `/health` hijau ≠ model benar. Uji kontrak, kegagalan, dan beban.
- Berikutnya: Docker Compose, push ke registry, deploy ke cloud.

## Catch-up pack
Tertinggal di Lab 1/2? Dari root repo:
```bash
cp .env.example .env        # isi OPENAI_API_KEY (boleh dikosongkan)
docker compose up -d --build
docker compose ps
```
Ini menjalankan `llm-agent` (8000) dan `cv-api` (8001) dengan nama persis seperti lab, sehingga Anda bisa langsung lompat ke Lab 3. Bersihkan dengan `docker compose down`. (Compose dibahas di materi berikutnya; anggap ini "lihat dulu".)
