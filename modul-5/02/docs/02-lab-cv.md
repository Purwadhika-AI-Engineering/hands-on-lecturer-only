# Lab 2: Containerize Model Computer Vision (menit 35-60, 25 menit)

**Hasil:** container `cv-api` berjalan di port **8001** dan mengklasifikasikan gambar.
Bedanya dengan Lab 1: **model hidup di dalam container** (bobot dibaca dari folder `models/`).

## B1. Bandingkan dengan Lab 1 (3 menit)
**Di mana:** folder `mlops-cv/`. Buka `Dockerfile`, `model.py`, `app.py`.
1. Temukan: base image (`python:3.9-slim`), `requirements.txt` (TensorFlow), `mkdir -p models`, dan `HEALTHCHECK` (memakai `python`, bukan `curl`).
2. Lihat `.dockerignore`: file `models/*.h5` sengaja **tidak** ikut masuk image.

**Yang harus terlihat:** Anda bisa menjawab: *model dimuat dari path apa?* (`models/cifar10_model.h5`) dan *apa yang terjadi bila file itu tidak ada?* (dibuat model **acak**, hanya muncul peringatan di log).

## B2. Pastikan image sudah jadi (2 menit)
```bash
docker images cv-api
```
**Yang harus terlihat:** image `cv-api` ukuran beberapa GB.
**Kalau tidak:** lihat Terminal 2 (build dari Lab 0). Masih berjalan? Tunggu. Gagal? Jalankan ulang `docker build -t cv-api ./mlops-cv`.
> 📸 **SS-B-2**: `docker images` memperlihatkan `llm-agent-service` dan `cv-api`.

## B3. Jalankan container (3 menit)
Port 8000 sudah dipakai agent, jadi pakai **8001** di host.
```bash
docker run -d --name cv-api -p 8001:8000 -v "$(pwd)/mlops-cv/models:/app/models" cv-api
docker logs cv-api
```
Windows PowerShell: ganti `$(pwd)` dengan `${PWD}`.

**Yang harus terlihat:** log berisi `Uvicorn running on http://0.0.0.0:8000` (TensorFlow butuh 10-30 detik). Bila folder `models/` kosong, log juga berisi `Model not found ... Please run train.py first.` Itu **normal** untuk sekarang.
**Kalau tidak:** `Conflict. The container name "/cv-api" is already in use` -> `docker rm -f cv-api` lalu ulangi.

## B4. Uji lewat Swagger UI (5 menit)
1. Buka http://localhost:8001/docs -> `POST /predict` -> *Try it out*.
2. Upload `samples/merah.png` (atau foto apa saja) -> *Execute*.

**Yang harus terlihat:** HTTP 200 dengan `class`, `confidence`, dan 10 nilai di `all_predictions` yang berjumlah 1.
**Kalau tidak:** 422 berarti field bukan `file`; 400 berarti file bukan gambar.
> 📸 **SS-B-4**: respons `/predict` di Swagger.

**Catatan:** tanpa model terlatih, kelasnya acak dan tidak bermakna. API tetap "sehat". Ingat ini untuk Lab 3.

## B5. Jalankan test bawaan di dalam container (3 menit)
```bash
docker exec cv-api python test.py
```
**Yang harus terlihat:** `Local prediction: ...`, `Health check: {'status': 'healthy'}`, `Prediction result: ...`, `Testing completed!`.
`docker exec` menjalankan perintah **di dalam** container yang sedang hidup.

## B6. OPSIONAL: latih model mini di dalam container (7 menit)
Dikerjakan bila waktu cukup, atau pengajar membagikan `cifar10_model.h5` (taruh di `mlops-cv/models/`, lalu `docker restart cv-api`).
```bash
docker run --rm -e TRAIN_SAMPLES=2000 -e TEST_SAMPLES=500 -e EPOCHS=2 -v "$(pwd)/mlops-cv/models:/app/models" cv-api python train.py
docker restart cv-api
docker logs cv-api
```
**Yang harus terlihat:** `Model saved to models/cifar10_model.h5`, lalu log `cv-api` berisi `Loading model from models/cifar10_model.h5`.
**Kalau tidak:** download CIFAR-10 (±170 MB) gagal karena koneksi -> minta file `.h5` dari pengajar. Akurasi model mini rendah (±20-35%); tujuan kita deployment, bukan akurasi.
> 📸 **SS-B-6**: log training dan `Loading model`.

### Done when
- [ ] `docker ps` menampilkan `llm-agent` (8000) **dan** `cv-api` (8001)
- [ ] `/predict` menjawab 200 dari container
- [ ] Anda bisa menjelaskan fungsi `-v` (volume) pada `docker run` ini
