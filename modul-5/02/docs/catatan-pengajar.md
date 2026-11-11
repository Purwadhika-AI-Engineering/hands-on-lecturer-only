# Catatan Pengajar

## Status verifikasi (baca dulu)
Repo ini dites di lingkungan **tanpa Docker dan tanpa akses ke OpenAI/CIFAR-10**. Artinya:

| Sudah dites | Belum dites (wajib dry-run Anda) |
|---|---|
| Dependency agent terpasang dengan `pip` di Python 3.11 dan `import agent` berhasil | `docker build` kedua image dan `docker run` |
| App agent jalan; 9 tes agent lulus dengan LLM tiruan; skenario tanpa key (`agent_initialized=false`, `/chat` 500) | Panggilan **nyata** ke OpenAI dengan `gpt-4.1-mini` |
| App CV dengan TensorFlow 2.15 + numpy 1.24.3 di Python 3.9; 16 tes CV lulus; `load_test.py`, `smoke_test.sh` | Tes `-m docker` dan `-m slow` (22 tes; kodenya belum pernah dijalankan terhadap Docker nyata) |
| `train.py` hasil perbaikan jalan dengan data sintetis | Training CIFAR-10 sungguhan (download diblokir) |

**Dry-run minimum (±25 menit):** ikuti Lab 1, Lab 2 dan Lab 3 dari awal di mesin bersih; catat selisih. Peserta biasanya butuh 1,3-1,5 kali waktu Anda.

## Perubahan dari project referensi
Project referensi tidak bisa berjalan apa adanya per 11 November 2026. Perubahan dibuat sekecil mungkin:

| File | Masalah | Perubahan |
|---|---|---|
| `mlops-ai-agent-handson/agent.py` | `OpenAI(...)` memakai `gpt-3.5-turbo-instruct`, **dimatikan OpenAI 28 Sep 2026** -> `/chat` gagal | Ganti ke `ChatOpenAI`, nama model dari env `OPENAI_MODEL` (default `gpt-4.1-mini`) |
| `mlops-ai-agent-handson/requirements.txt` | Tanpa pin, pip memasang `langchain-community`/`langchain-core` yang tidak cocok dengan `langchain==0.0.350`: `import agent` gagal (`RAW_SCHEMA_QUERY`), container crash saat start | Tambah `langchain-community==0.0.2`, `langchain-core==0.1.3` |
| `mlops-ai-agent-handson/Dockerfile` | `HEALTHCHECK` memakai `curl`, `python:3.11-slim` tidak punya curl -> selalu `unhealthy` | Tambah `curl` di `apt-get install` |
| `mlops-cv/train.py` | Me-resize 50.000 gambar ke 224x224 sekaligus ≈ 30 GB RAM -> crash | Resize per batch lewat `tf.data`; `TRAIN_SAMPLES`, `TEST_SAMPLES`, `EPOCHS` lewat env (default 5000/1000/3) |
| `mlops-cv/` (baru) | README menyebut `docker-compose.yml` yang tidak ada; tidak ada `.dockerignore` | Tambah keduanya; `.dockerignore` mengecualikan `models/*.h5` |
| `mlops-cv/Dockerfile` | Tidak ada HEALTHCHECK | Tambah HEALTHCHECK berbasis `python` (bahan Lab 3) |
| `model.py`, `app.py`, `test.py`, `requirements.txt` (CV); `app.py`, `.dockerignore` (agent) | - | **Tidak diubah** |

## Keputusan yang perlu Anda ambil
1. **Model default `gpt-4.1-mini`.** Berfungsi hari ini, tetapi OpenAI mengumumkan penutupannya **14 Januari 2027**. Model baru (mis. `gpt-6-luna`) belum saya uji dengan stack LangChain 0.0.350: model reasoning menolak `temperature`, dan `stop` pada agent ReAct belum terverifikasi. Untuk angkatan berikutnya, uji `-e OPENAI_MODEL=...` atau naikkan versi LangChain `[VERIFIKASI]`.
2. **OpenAI API key = berbayar** (biaya per sesi sangat kecil, tapi bukan free-tier). Bila banyak peserta tak punya key, tes `-m llm` otomatis `SKIPPED`; yang hilang hanya `/chat`. Saya bisa menambahkan mode LLM tiruan (`MOCK_LLM=1`) bila Anda mau lab bebas biaya.
3. **Model CV.** Tanpa `cifar10_model.h5`, prediksi acak. Sebaiknya Anda melatih sekali sebelum kelas, mis. `docker run --rm -e TRAIN_SAMPLES=20000 -e EPOCHS=5 -v "$(pwd)/mlops-cv/models:/app/models" cv-api python train.py` (lama di CPU; ±1 jam), lalu bagikan file `.h5` (±130 MB, tidak masuk git).
4. **Build TensorFlow di wifi kelas** lambat. Lab 0 S5 memulai build lebih awal; pertimbangkan membagikan image via `docker save`/`load` atau registry.

## Sinkronisasi dengan deck
- Slide 2 menyebut hands-on 40 menit; sekarang 90 menit (rundown di README).
- Slide 20: `OpenAI(...)` -> `ChatOpenAI(model_name=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), temperature=0.7)`; catatan "LLM remote" tetap benar.
- Slide 23: `apt-get install -y gcc` -> `gcc curl`. Catatan slide 24 tentang curl tidak lagi perlu.
- Slide 30 ("Where does the model live?") cocok sebagai jembatan Lab 1 -> Lab 2.
- Slide 38/39: Docker Compose disebut materi lanjutan; di repo hanya muncul sebagai catch-up pack.

## Catatan teknis
- Agent hanya mengembalikan teks `Error processing message: ...` dengan HTTP 200 saat OpenAI gagal. Ini sengaja tidak diubah dan dipakai sebagai bahan diskusi di Lab 3.
- Panggilan `/chat` memakai `eval()` pada Calculator (sudah disebut di deck); container tidak membuat kode aman.
- Port: agent 8000, CV 8001 (sengaja berbeda agar peserta menghadapi *port mapping* nyata).
- Mac M-series: image dibangun arm64; TensorFlow 2.15 di arm64 `[VERIFIKASI]`.
- Shot list di [shot-list.md](shot-list.md); slot `SS-...` menunggu screenshot dari dry-run Anda.
