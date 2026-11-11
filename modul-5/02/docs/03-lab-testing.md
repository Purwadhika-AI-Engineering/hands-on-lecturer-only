# Lab 3: Testing Hasil Deployment (menit 60-80, 20 menit)

**Hasil:** Anda punya bukti terukur bahwa kedua container benar-benar **sehat, sesuai kontrak API, aman, dan tahan skenario gagal**, bukan sekadar "kelihatannya jalan".

Ada 4 lapis pengujian, dari cepat ke dalam:

| Lapis | Pertanyaan | Alat |
|---|---|---|
| 1. Smoke | Apakah hidup? | `scripts/smoke_test.sh` |
| 2. Kontrak API | Apakah jawabannya benar bentuknya, termasuk saat input salah? | `pytest -m "agent or cv"` |
| 3. Container | Apakah container sehat, aman, hemat? | `pytest -m "docker and not slow"` |
| 4. Skenario gagal & beban | Apa yang terjadi saat key hilang, port bentrok, restart, banyak request? | `pytest -m slow`, `load_test.py` |

Prasyarat: `llm-agent` (8000) dan `cv-api` (8001) berjalan, dan venv test aktif (Lab 0, S4). Semua perintah dari root repo kecuali disebut lain.

## C1. Smoke test (2 menit)
```bash
bash scripts/smoke_test.sh          # Windows: pakai Git Bash/WSL, atau lompat ke C2
```
**Yang harus terlihat:** lima baris `PASS`, lalu `lulus: 5   gagal: 0`.
**Kalau tidak:** baris `FAIL` menampilkan jawaban server. Cek `docker ps` dan nomor port.
> 📸 **SS-C-1**: hasil smoke test.

## C2. Tes kontrak API (4 menit)
```bash
cd tests
pytest -m "agent or cv" -v
```
**Yang harus terlihat:** semua `PASSED`. Tanpa API key, tes agent yang butuh LLM menjadi `SKIPPED` dengan alasan; itu wajar.
**Kalau tidak:** pesan `... tidak bisa dijangkau` berarti container mati atau port salah. Ubah dengan `AGENT_URL=http://localhost:8080 pytest ...` bila perlu.
> 📸 **SS-C-2**: ringkasan pytest.

Baca satu tes dan jawab: `test_chat_calculator` memeriksa bahwa jawaban **tidak** diawali `Error processing message`. Kenapa status `success` saja tidak cukup?

## C3. Tes level container (4 menit)
```bash
pytest -m "docker and not slow" -v
```
**Yang harus terlihat:** lulus untuk: container running, port terpetakan, `healthy`, tidak ada secret di image, agent berjalan sebagai `appuser`, ukuran image & memori dalam anggaran. Dua hasil **XFAIL** diharapkan:
- `test_cv_model_file_present`: model CV belum dilatih (Lab 2 B6 belum dikerjakan).
- `test_cv_runs_as_non_root`: container CV berjalan sebagai root (ini tantangan D2).

**Kalau tidak:** `SKIPPED ... container tidak ada` berarti nama container berbeda dari `llm-agent` / `cv-api`.
> 📸 **SS-C-3**: hasil tes container dengan 2 XFAIL.

## C4. Skenario gagal (5 menit)
```bash
pytest -m slow -v
```
Tes ini membuat container sementara (port 18000-18002, otomatis dihapus) dan me-restart container Anda. Perlu 3-5 menit (TensorFlow lambat start); selagi menunggu, jawab pertanyaan di bawah.

**Yang harus terlihat:**
- **Tanpa API key:** container naik, `/health` tetap 200 tetapi `agent_initialized=false`, `/chat` menjawab 500.
- **Port bentrok:** `docker run` gagal dengan pesan *port is already allocated*.
- **CV tanpa volume model:** `/health` hijau dan `/predict` tetap menjawab 200, padahal bobotnya acak. **Health check tidak menjamin model benar.**
- **Restart CV:** kembali sehat dan tetap bisa prediksi.
- **Restart agent** (hanya bila punya key): riwayat chat **hilang** (menjawab diskusi slide 36).

**Kalau tidak:** `SKIPPED ... gagal menjalankan` berarti image belum ada; cek `docker images`.
> 📸 **SS-C-4**: hasil `pytest -m slow`.

## C5. Beban ringan & pemakaian resource (3 menit)
```bash
python load_test.py --requests 40 --concurrency 4
docker stats --no-stream
```
**Yang harus terlihat:** `error: 0`, throughput dan latensi p50/p95 tercetak; `docker stats` menampilkan CPU dan MEM tiap container.
> 📸 **SS-C-5**: output load test + `docker stats`.

Coba ulangi dengan `--concurrency 16`. Apa yang berubah pada p95? Kenapa?

## Lembar jawab singkat (catat, dibahas di recap)
1. Tes mana yang akan Anda taruh di pipeline CI/CD, dan mana yang tidak (karena mahal/lambat/berbayar)?
2. Apa beda *health check hijau* dengan *model benar*? Tes apa yang akan membuktikan model benar?
3. Kenapa tes memakai gambar sintetis alih-alih foto asli?
4. Setelah restart, data apa yang hilang dan data apa yang bertahan? Kenapa?

### Done when
- [ ] C1-C3 lulus (kecuali 2 XFAIL yang diharapkan)
- [ ] Anda sudah melihat minimal 2 skenario gagal di C4 dan bisa menjelaskan penyebabnya
- [ ] Anda punya angka latensi p50/p95 dari C5
