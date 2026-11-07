# Python CRUD REST API — CI/CD Pipeline with Jenkins, Docker & GitHub Webhook

Proyek praktikum Cloud Computing (Teknik Telekomunikasi) untuk membangun pipeline CI/CD otomatis menggunakan **GitHub**, **Jenkins**, **Docker Engine**, dan **ngrok**.

## Fitur & Arsitektur

1. **Python REST API (`app.py`)**
   - `GET /` atau `GET /health` — Health check (`HTTP 200`, `{"status": "active", "service": "Backend API"}`)
   - `GET /messages` — Mengambil daftar seluruh pesan beserta jumlah total (`HTTP 200`)
   - `POST /messages` — Menyimpan pesan baru dengan timestamp UTC `created_at` (`HTTP 201`) dan validasi input kosong/panjang > 500 karakter (`HTTP 400`)
   - `DELETE /messages?index=<n>` — Menghapus pesan berdasarkan indeks (`HTTP 200` atau `HTTP 404` jika di luar jangkauan)
2. **Persistensi Data (`production-api-data`)**
   - Data disimpan di `/var/lib/backend_data/messages.json` yang dipasang ke Docker Named Volume `production-api-data`, sehingga data tetap bertahan meskipun container dihapus dan dibuat ulang saat redeploy.
3. **CI/CD Pipeline (`Jenkinsfile`)**
   - **Stage 1 — Checkout Code**: Mengambil kode terbaru dari branch `main` di GitHub.
   - **Stage 2 — Code Syntax Verification**: Memeriksa sintaks dengan `python3 -m py_compile`.
   - **Stage 3 — Automated API Tests (Tugas D)**: Menjalankan unit test otomatis (`test_app.py`) untuk menguji `/health` dan validasi `POST /messages` sebelum build image.
   - **Stage 4 — Build Docker Image (Tugas D)**: Membangun image Docker dengan tag `${BUILD_NUMBER}`, commit SHA (`git rev-parse --short HEAD`), dan `latest`.
   - **Stage 5 — Automated Deployment**: Menghentikan container lama, mempertahankan volume `production-api-data`, dan menjalankan container baru pada jaringan `jenkins-net`.
   - **Stage 6 — Health Check**: Memverifikasi endpoint `/health` menghasilkan HTTP 200.

## Cara Menjalankan & Menguji Secara Manual

```bash
# 1. Jalankan unit test lokal
python -m unittest -v test_app.py

# 2. Bangun Docker image manual
docker build -t python-crud-api:manual .

# 3. Buat volume persistensi dan jalankan container
docker volume create production-api-data
docker run -d --name production-api-container \
  -p 5000:5000 \
  -v production-api-data:/var/lib/backend_data \
  python-crud-api:manual

# 4. Uji endpoint
curl -i http://localhost:5000/health
curl -i http://localhost:5000/messages
curl -i -X POST http://localhost:5000/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"Pesan pertama dari praktikum"}'
curl -i -X DELETE "http://localhost:5000/messages?index=0"
```


<!-- Webhook automated trigger test: 2026-11-08 06:56:03 -->
