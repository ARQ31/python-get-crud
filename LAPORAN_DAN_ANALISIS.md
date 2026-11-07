# Laporan Analisis & Troubleshooting Praktikum CI/CD Jenkins

## Bagian 1: Dokumentasi Kegagalan, Diagnosis, dan Perbaikan

### 1. Kegagalan Koneksi Docker Daemon pada Tahap 1 & Inkompatibilitas Mount Binary Docker pada Host Windows
- **Gejala:**
  1. Saat menjalankan pemeriksaan awal (`docker info`), muncul pesan error:
     `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.`
  2. Selain itu, pada host Windows (PowerShell), perintah panduan Linux `-v "$(which docker)":/usr/bin/docker` tidak dapat digunakan karena binary Docker di host Windows adalah executable Windows (`docker.exe`), sedangkan container `jenkins/jenkins:lts-jdk17` berjalan di atas kernel Linux dan secara bawaan belum memiliki `python3` maupun `docker` CLI.
- **Diagnosis:**
  1. Layanan Docker Desktop pada Windows belum berjalan sehingga named pipe `dockerDesktopLinuxEngine` belum aktif.
  2. Container Linux `jenkins/jenkins:lts-jdk17` membutuhkan binary Linux `docker` CLI dan `python3` di dalam image container serta akses ke `/var/run/docker.sock`.
- **Perbaikan:**
  1. Menjalankan Docker Desktop hingga Docker Engine merespons `docker info`.
  2. Membuat [`Dockerfile.jenkins`](./Dockerfile.jenkins) berbasis `jenkins/jenkins:lts-jdk17` yang menginstal paket Linux `python3`, `docker.io` (Docker CLI), dan `curl`, lalu me-mount `/var/run/docker.sock:/var/run/docker.sock` ke container `jenkins-server` pada jaringan `jenkins-net`.
- **Hasil Uji Ulang:**
  - `docker exec jenkins-server docker version` dan `docker exec jenkins-server python3 --version` berhasil dieksekusi dari dalam container Jenkins dan mampu mengakses Docker daemon host.

---

## Bagian 2: Jawaban 8 Pertanyaan Analisis

### 1. Jelaskan urutan peristiwa dari `git push` hingga container baru berjalan!
1. **Developer melakukan `git push origin main`** dari komputer lokal ke repository GitHub.
2. **GitHub memicu event `push` via Webhook** dengan mengirimkan HTTP `POST` berisi payload JSON ke URL publik HTTPS milik **ngrok** (`https://<domain-ngrok>/github-webhook/`).
3. **ngrok meneruskan (forward) request** dari internet ke layanan lokal **Jenkins** di `http://localhost:8080/github-webhook/`.
4. **Jenkins GitHub Plugin menerima notifikasi webhook**, mencocokkan repository dan branch (`*/main`), lalu memicu job pipeline `python-crud-api-pipeline` secara otomatis.
5. **Stage 1 (Checkout Code):** Jenkins menggunakan credential `github-pat-readonly` (Fine-grained PAT) untuk melakukan `git fetch/checkout` kode terbaru beserta `Jenkinsfile` dari branch `main`.
6. **Stage 2 & 3 (Syntax Verification & Automated Tests):** Jenkins menjalankan `python3 -m py_compile app.py test_app.py` dan unit test `python3 -m unittest -v test_app.py` untuk memvalidasi endpoint `/health` dan validasi input `POST /messages`.
7. **Stage 4 (Build Docker Image):** Jenkins memanggil Docker Engine melalui `/var/run/docker.sock` untuk membangun image baru `python-crud-api:${BUILD_NUMBER}` dan memberikan tag tambahan berbasis commit SHA (`python-crud-api:${COMMIT_SHA}`) serta `python-crud-api:latest`.
8. **Stage 5 (Automated Deployment):** Jenkins menghentikan dan menghapus container lama (`production-api-container`), memastikan named volume `production-api-data` tersedia, lalu menjalankan container baru dari image `python-crud-api:latest` dengan me-mount volume `production-api-data:/var/lib/backend_data`.
9. **Stage 6 (Health Check):** Jenkins menunggu aplikasi siap lalu melakukan request `curl -fsS` ke endpoint `/health` dan memverifikasi respons `HTTP 200` (`{"status": "active"}`).

---

### 2. Apa perbedaan PAT, webhook secret, dan ngrok authtoken?
| Kredensial | Fungsi Utama | Pihak yang Mengautentikasi | Arah Komunikasi |
| :--- | :--- | :--- | :--- |
| **GitHub Fine-grained PAT** | Mengautentikasi Jenkins saat mengambil (checkout/pull) source code dari repository privat GitHub melalui HTTPS. | Jenkins $\rightarrow$ GitHub Git Server | Outbound dari Jenkins ke GitHub |
| **Webhook Secret** | Memverifikasi keaslian dan integritas payload HTTP POST yang dikirim ke `/github-webhook/` menggunakan tanda tangan HMAC-SHA256 (`X-Hub-Signature-256`) agar pihak luar tidak bisa memalsukan trigger build. | GitHub Webhook $\rightarrow$ Jenkins | Inbound dari GitHub ke Jenkins |
| **ngrok Authtoken** | Mengautentikasi agen CLI `ngrok` di komputer lokal dengan akun layanan cloud ngrok untuk mengizinkan pembuatan tunnel HTTPS publik. | Agen `ngrok` lokal $\rightarrow$ Server Cloud ngrok | Outbound dari mesin lokal ke infrastruktur ngrok |

---

### 3. Mengapa PAT read-only cukup untuk checkout source code, tetapi tidak cukup untuk push kembali ke repository?
- Operasi **checkout / clone / fetch** hanya membaca objek Git (commit, tree, blob) dari repository GitHub. Oleh karena itu, sesuai prinsip *Least Privilege* (hak akses minimum), izin **Repository Contents: Read-only** (dan **Metadata: Read-only**) sudah cukup bagi Jenkins untuk mengambil source code.
- Sebaliknya, operasi **`git push`** memodifikasi state repository (menulis objek baru dan memperbarui referensi branch di server GitHub), sehingga membutuhkan izin **Contents: Read and write**. Dengan hanya memberikan izin *Read-only*, jika token Jenkins bocor, penyerang tidak dapat menyuntikkan kode berbahaya (*malicious commit*) kembali ke repository GitHub.

---

### 4. Apa risiko memasang Docker socket host (`/var/run/docker.sock`) ke container Jenkins?
- Memberikan akses ke `/var/run/docker.sock` setara dengan memberikan **akses `root` penuh terhadap host Docker (Docker daemon)**.
- Proses apa pun di dalam container Jenkins yang dapat mengakses socket tersebut dapat:
  1. Menjalankan container baru dengan flag `--privileged` atau melakukan bind-mount seluruh filesystem host (`-v /:/host`) untuk mengambil alih sistem operasi host (*container escape*).
  2. Menghentikan, menghapus, atau membaca data dari seluruh container dan volume lain yang berjalan di host yang sama.
- Oleh karena itu, pendekatan bind-mount `docker.sock` hanya layak untuk lingkungan lab tunggal yang terisolasi, bukan untuk lingkungan produksi *multi-tenant*.

---

### 5. Mengapa URL ngrok yang berubah dapat memutus integrasi webhook?
- Pada paket gratis (*free tier*) tanpa static domain, setiap kali proses `ngrok http 8080` dihentikan dan dijalankan ulang, ngrok menghasilkan subdomain acak baru (misalnya `https://abcd-1234.ngrok-free.app` berubah menjadi `https://efgh-5678.ngrok-free.app`).
- Konfigurasi **Payload URL** pada GitHub Webhook bersifat statis sesuai URL yang disimpan terakhir kali. Jika URL ngrok berubah namun konfigurasi di GitHub belum diperbarui, maka GitHub akan mengirim event `push` ke alamat tunnel lama yang sudah tidak aktif (menghasilkan error `404` atau kegagalan koneksi pada *Recent Deliveries*), sehingga Jenkins tidak menerima trigger build.

---

### 6. Mengapa data pada named volume bertahan setelah container dihapus?
- Filesystem internal sebuah container bersifat *ephemeral* (sementara) dan terikat pada siklus hidup (*lifecycle*) writable layer container tersebut; saat `docker rm` dijalankan, writable layer container ikut terhapus.
- **Docker Named Volume** (`production-api-data`) dikelola secara independen oleh Docker Engine di direktori penyimpanan host (di luar writable layer container) dan siklus hidupnya terpisah dari container.
- Ketika `docker rm production-api-container` dijalankan saat redeploy, volume `production-api-data` tidak ikut dihapus. Saat container baru dijalankan dengan `-v production-api-data:/var/lib/backend_data`, Docker memasang kembali volume yang sama ke path `/var/lib/backend_data`, sehingga file `messages.json` beserta pesan sebelumnya tetap utuh.

---

### 7. Apa perbedaan CI dan CD pada pipeline ini?
- **Continuous Integration (CI)** mencakup tahap integrasi kode otomatis dan verifikasi kualitas setiap kali ada perubahan kode:
  - *Stage 1 (Checkout Code)*: Mengambil commit terbaru dari `main`.
  - *Stage 2 (Code Syntax Verification)*: Memeriksa sintaks Python (`py_compile`).
  - *Stage 3 (Automated API Tests)*: Menjalankan unit test otomatis untuk `/health` dan validasi `POST /messages`.
  - *Stage 4 (Build Docker Image)*: Mengemas aplikasi menjadi artefak image Docker ber-tag nomor build dan commit SHA.
- **Continuous Delivery / Deployment (CD)** mencakup tahap rilis dan pembaruan layanan aplikasi secara otomatis ke lingkungan target beserta verifikasi pasca-deploy:
  - *Stage 5 (Automated Deployment)*: Mengganti container lama dengan container dari image terbaru sambil mempertahankan volume data `production-api-data`.
  - *Stage 6 (Health Check)*: Memverifikasi bahwa layanan yang baru di-deploy benar-benar hidup dan merespons `HTTP 200` pada `/health`.

---

### 8. Apa yang harus dilakukan jika tahap deploy sukses tetapi health check gagal?
Jika `docker run` berhasil (exit code 0) namun `curl /health` pada tahap Health Check gagal:
1. **Periksa status dan log container** menggunakan `docker ps -a` dan `docker logs production-api-container` untuk melihat apakah aplikasi mengalami *crash* saat startup (misalnya `SyntaxError`, `PermissionError` pada volume, atau port binding error).
2. **Periksa konektivitas jaringan dan kesiapan waktu startup (*readiness*)**: pastikan container berada di jaringan yang dapat dijangkau oleh Jenkins (`jenkins-net` atau port host `5000`), dan pastikan waktu tunggu (`sleep`/retry) cukup bagi server HTTP Python untuk mulai mendengarkan di `0.0.0.0:5000`.
3. **Lakukan Rollback ke versi image stabil sebelumnya**: jalankan kembali container menggunakan tag nomor build atau commit SHA sebelumnya yang sudah terbukti lulus health check (`docker run ... python-crud-api:<PREVIOUS_BUILD_OR_SHA>`) agar layanan tidak mengalami *downtime* berkepanjangan sambil memperbaiki bug pada commit terbaru.

