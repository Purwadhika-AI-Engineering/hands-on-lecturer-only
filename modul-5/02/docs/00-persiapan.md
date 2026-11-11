# Lab 0: Persiapan & Cek Docker (menit 0-10)

**Hasil:** Docker berjalan, repo siap, API key tersedia, dan build image CV sudah berjalan di terminal ke-2.

## S1. Cek Docker
**Di mana:** Terminal (macOS/Linux) atau PowerShell (Windows).
1. Jalankan `docker version` lalu `docker run hello-world`.

**Yang harus terlihat:** blok *Client* dan *Server* tanpa error, dan pesan `Hello from Docker!`.
**Kalau tidak:** `Cannot connect to the Docker daemon` berarti Docker Desktop belum jalan; buka aplikasinya dan tunggu ikon berhenti beranimasi.
> 📸 **SS-S-1**: output `docker run hello-world`.

## S2. Siapkan repo
1. `git clone <url-repo>` lalu `cd mlops-docker-handson` (atau ekstrak zip).
2. Cek isi: `docker compose version` tidak wajib, tapi repo harus berisi folder `mlops-ai-agent-handson`, `mlops-cv`, `tests`.

## S3. Siapkan OpenAI API key
1. Siapkan key dari platform.openai.com. Simpan di catatan pribadi, **jangan** ditempel ke chat kelas atau screenshot.
2. Tanpa key pun Anda tetap bisa mengerjakan semua lab kecuali tes `-m llm` (bagian chat dengan agent).

## S4. Siapkan test environment (sekali saja)
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r tests/requirements.txt
```
**Yang harus terlihat:** `pytest --version` menampilkan versi.

## S5. Mulai build image CV di Terminal ke-2 (biarkan berjalan)
Build TensorFlow butuh beberapa menit; kita mulai sekarang supaya siap saat Lab 2.
```bash
docker build -t cv-api ./mlops-cv
```
**Yang harus terlihat:** langkah `[x/y]` berjalan; **jangan ditutup**. Lanjut ke Lab 1 di terminal pertama.
**Kalau tidak:** `no space left on device` -> `docker system prune` (hati-hati, menghapus image yang tidak dipakai).
> 📸 **SS-S-5**: build CV sedang berjalan.

### Done when
- [ ] `docker run hello-world` sukses
- [ ] `pytest --version` jalan
- [ ] build `cv-api` berjalan di terminal 2
