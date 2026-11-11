# MLOps Hands-On: Menjalankan Model AI di Container Docker

Repository hands-on (±90 menit) setelah pemaparan **"2 - Running AI Models in Containers with Docker"**.
Program: Job Connector (JC) AI Engineering, Module 5 (AI Deployment).

Setelah sesi ini peserta bisa **membungkus dua jenis layanan AI ke dalam container Docker, menjalankannya, lalu mengujinya secara sistematis**:

| | Layanan 1: LLM Agent | Layanan 2: Computer Vision |
|---|---|---|
| Folder | `mlops-ai-agent-handson/` | `mlops-cv/` |
| Model hidup di mana? | Di OpenAI (remote) | Di dalam container / volume |
| Port host | **8000** | **8001** |
| Nama image / container | `llm-agent-service` / `llm-agent` | `cv-api` / `cv-api` |

## Rundown 90 menit

| Menit | Blok | Panduan |
|---|---|---|
| 0-10 | Lab 0: Persiapan & cek Docker | [docs/00-persiapan.md](docs/00-persiapan.md) |
| 10-35 | Lab 1: Containerize LLM Agent | [docs/01-lab-agent.md](docs/01-lab-agent.md) |
| 35-60 | Lab 2: Containerize model CV | [docs/02-lab-cv.md](docs/02-lab-cv.md) |
| 60-80 | Lab 3: Testing hasil deployment | [docs/03-lab-testing.md](docs/03-lab-testing.md) |
| 80-87 | Mini challenge | [docs/04-challenge-dan-recap.md](docs/04-challenge-dan-recap.md) |
| 87-90 | Recap & diskusi | idem |

Tertinggal? Pakai **catch-up pack**: `docker compose up -d --build` di root repo (lihat [Catch-up](docs/04-challenge-dan-recap.md#catch-up-pack)).
Macet? Lihat [docs/troubleshooting.md](docs/troubleshooting.md).
Pengajar: baca [docs/catatan-pengajar.md](docs/catatan-pengajar.md) dulu.

## Struktur repo

```
.
├── mlops-ai-agent-handson/   # Layanan 1 (FastAPI + LangChain + OpenAI)
├── mlops-cv/                 # Layanan 2 (FastAPI + TensorFlow, CIFAR-10)
│   └── models/               # taruh cifar10_model.h5 di sini (tidak masuk git)
├── tests/                    # test deployment (pytest, smoke, load test)
├── scripts/smoke_test.sh     # smoke test cepat tanpa Python
├── samples/                  # gambar contoh untuk upload manual di /docs
├── docker-compose.yml        # catch-up pack (jalankan kedua layanan sekaligus)
├── .env.example
└── docs/                     # panduan lab (Bahasa Indonesia)
```

## Prasyarat singkat

Docker Desktop (jalan, `docker version` tidak error), Python 3.9+ untuk menjalankan test, OpenAI API key (hanya untuk Lab 1 bagian chat; biaya sangat kecil), dan ±6 GB ruang disk bebas. Detail di Lab 0.

## Asal project

Dua project di repo ini berasal dari referensi pengajar. Beberapa perbaikan kecil ditambahkan agar bisa berjalan per November 2026; daftar lengkap ada di [docs/catatan-pengajar.md](docs/catatan-pengajar.md#perubahan-dari-project-referensi).
