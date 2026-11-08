# Paket Bukti & Laporan Analisis Praktikum CI/CD Jenkins

- **Nama Praktikan**: Ahmad Faisal Hafidz (`ARQ31`)
- **URL Repository GitHub**: `https://github.com/ARQ31/python-get-crud`
- **URL Tunnel ngrok**: `https://retired-cover-giddiness.ngrok-free.dev/github-webhook/`
- **Nama Job Jenkins**: `python-crud-api-pipeline`

---

## 1. Bukti GitHub, Jenkins, dan Tugas A & D (Build #1 & Build #2)

### Ringkasan Eksekusi Build Jenkins
| Build | Pemicu (Trigger) | Commit SHA (`main`) | Tag Image Docker | Image ID | Container ID Hasil Deploy | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **#1** | Manual (`Build Now` oleh Ahmad Faisal Hafidz) | `f9803c88b0e8e0b8f5e5650b6e81d6a2daf6fde0` (`f9803c8`) | `python-crud-api:1`, `python-crud-api:f9803c8`, `python-crud-api:latest` | `ce1945a00b8e` | `03da2f8a4d6e` | **SUCCESS** |
| **#2** | Otomatis (`Started by GitHub push by ARQ31`) | `bc65727be0e6d2acd55c2677bbf77da22b0acada` (`bc65727`) | `python-crud-api:2`, `python-crud-api:bc65727`, `python-crud-api:latest` | `ce1945a00b8e` | `58a08ecf5c4e` | **SUCCESS** |

### Console Output Jenkins — Build #2 (Otomatis via GitHub Webhook)
```text
Started by GitHub push by ARQ31
Obtained Jenkinsfile from git https://github.com/ARQ31/python-get-crud.git
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins in /var/jenkins_home/workspace/python-crud-api-pipeline
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Declarative: Checkout SCM)
[Pipeline] checkout
using credential github-pat-readonly
 > git fetch --tags --force --progress -- https://github.com/ARQ31/python-get-crud.git +refs/heads/*:refs/remotes/origin/* # timeout=10
 > git rev-parse refs/remotes/origin/main^{commit} # timeout=10
Checking out Revision bc65727be0e6d2acd55c2677bbf77da22b0acada (refs/remotes/origin/main)
 > git checkout -f bc65727be0e6d2acd55c2677bbf77da22b0acada # timeout=10
Commit message: "ci: trigger automated Jenkins build via GitHub push webhook"
[Pipeline] }
[Pipeline] stage
[Pipeline] { (1. Checkout Code)
[Pipeline] echo
Checking out source code from GitHub
[Pipeline] checkout
Checking out Revision bc65727be0e6d2acd55c2677bbf77da22b0acada (refs/remotes/origin/main)
[Pipeline] sh
+ git rev-parse HEAD
bc65727be0e6d2acd55c2677bbf77da22b0acada
+ git rev-parse --short HEAD
bc65727
[Pipeline] }
[Pipeline] stage
[Pipeline] { (2. Code Syntax Verification)
[Pipeline] sh
+ python3 -m py_compile app.py test_app.py
[Pipeline] }
[Pipeline] stage
[Pipeline] { (3. Automated API Tests)
[Pipeline] sh
+ python3 -m unittest -v test_app.py
test_health_endpoint (test_app.BackendAPITestCase.test_health_endpoint) ... [07/Nov/2026 23:57:48] "GET /health HTTP/1.1" 200 -
ok
test_post_message_empty_validation (test_app.BackendAPITestCase.test_post_message_empty_validation) ... [07/Nov/2026 23:57:48] "POST /messages HTTP/1.1" 400 -
ok
test_post_message_too_long_validation (test_app.BackendAPITestCase.test_post_message_too_long_validation) ... [07/Nov/2026 23:57:48] "POST /messages HTTP/1.1" 400 -
ok
test_post_message_valid (test_app.BackendAPITestCase.test_post_message_valid) ... [07/Nov/2026 23:57:48] "POST /messages HTTP/1.1" 201 -
ok

----------------------------------------------------------------------
Ran 4 tests in 0.526s

OK
[Pipeline] }
[Pipeline] stage
[Pipeline] { (4. Build Docker Image)
[Pipeline] sh
+ git rev-parse --short HEAD
+ COMMIT_SHA=bc65727
+ echo Building image for BUILD_NUMBER=2, COMMIT_SHA=bc65727
Building image for BUILD_NUMBER=2, COMMIT_SHA=bc65727
+ docker build -t python-crud-api:2 .
Successfully built ce1945a00b8e
Successfully tagged python-crud-api:2
+ docker tag python-crud-api:2 python-crud-api:bc65727
+ docker tag python-crud-api:2 python-crud-api:latest
+ docker images python-crud-api
IMAGE                     ID             DISK USAGE   CONTENT SIZE   EXTRA
python-crud-api:1         ce1945a00b8e        187MB         45.6MB   U    
python-crud-api:2         ce1945a00b8e        187MB         45.6MB   U    
python-crud-api:bc65727   ce1945a00b8e        187MB         45.6MB   U    
python-crud-api:f9803c8   ce1945a00b8e        187MB         45.6MB   U    
python-crud-api:latest    ce1945a00b8e        187MB         45.6MB   U    
python-crud-api:manual    1b252c6a53af        187MB         45.6MB        
[Pipeline] }
[Pipeline] stage
[Pipeline] { (5. Automated Deployment)
[Pipeline] sh
+ docker network inspect jenkins-net
+ docker stop production-api-container
production-api-container
+ docker rm production-api-container
production-api-container
+ docker volume create production-api-data
production-api-data
+ docker run -d --name production-api-container --network jenkins-net -p 5000:5000 -v production-api-data:/var/lib/backend_data python-crud-api:latest
58a08ecf5c4e29c0959cb78c9b16b8fc5cedfdd958c8ba7c89e084d71a4e2e56
+ docker ps --filter name=production-api-container
CONTAINER ID   IMAGE                    COMMAND           CREATED                  STATUS                  PORTS                                         NAMES
58a08ecf5c4e   python-crud-api:latest   "python app.py"   Less than a second ago   Up Less than a second   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp   production-api-container
[Pipeline] }
[Pipeline] stage
[Pipeline] { (6. Health Check)
[Pipeline] sh
+ sleep 3
+ curl -fsS http://production-api-container:5000/health
{"status": "active", "service": "Backend API"}
+ docker logs --tail 20 production-api-container
Backend API listening on 0.0.0.0:5000
[07/Nov/2026 23:57:56] "GET /health HTTP/1.1" 200 -
[Pipeline] }
[Pipeline] stage
[Pipeline] { (Declarative: Post Actions)
[Pipeline] echo
Pipeline completed successfully.
[Pipeline] }
[Pipeline] End of Pipeline
Finished: SUCCESS
```

---

## 2. Bukti Webhook GitHub & Operasi API (`curl`) — Tugas B & C

### A. Bukti Pengiriman Webhook via ngrok (Tugas B)
```text
=== ngrok Webhook Events ===
Event: push | Delivery: 01561be4-db07-11f1-8079-f173cef301f6 | Status: 200 OK
Event: ping | Delivery: d15a70b6-db06-11f1-8c32-13f37c590712 | Status: 200 OK

=== Jenkins Webhook Log ===
INFO o.j.p.g.w.s.DefaultPushGHEventSubscriber#onEvent: Received PushEvent for https://github.com/ARQ31/python-get-crud from 9.234.98.176 ⇒ https://retired-cover-giddiness.ngrok-free.dev:8080/github-webhook/
INFO o.j.p.g.w.s.DefaultPushGHEventSubscriber$1#run: Poked python-crud-api-pipeline
INFO c.c.jenkins.GitHubPushTrigger$1#run: SCM changes detected in python-crud-api-pipeline. Triggering #2
```

### B. Bukti 6 Skenario Pengujian HTTP CRUD pada API
```text
[1] Health (GET /health):
HTTP/1.0 200 OK
Content-Type: application/json; charset=utf-8
{"status": "active", "service": "Backend API"}

[2] Daftar kosong (GET /messages):
HTTP/1.0 200 OK
Content-Type: application/json; charset=utf-8
{"messages": [], "total": 0}

[3] Buat pesan valid (POST /messages):
HTTP/1.0 201 Created
Content-Type: application/json; charset=utf-8
{"status": "created", "message": {"message": "Pesan pertama dari praktikum", "created_at": "2026-11-07T23:07:47.032237+00:00"}}

[4] Validasi input kosong (POST /messages):
HTTP/1.0 400 Bad Request
Content-Type: application/json; charset=utf-8
{"error": "message must not be empty"}

[5] Hapus pesan (DELETE /messages?index=0) & verifikasi GET:
HTTP/1.0 200 OK
Content-Type: application/json; charset=utf-8
{"status": "deleted", "removed": {"message": "Pesan pertama dari praktikum", "created_at": "2026-11-07T23:07:47.032237+00:00"}}
--- Setelah DELETE ---
HTTP/1.0 200 OK
{"messages": [], "total": 0}

[6] Indeks di luar daftar (DELETE /messages?index=999):
HTTP/1.0 404 Not Found
Content-Type: application/json; charset=utf-8
{"error": "Message not found"}
```

### C. Bukti Persistensi Pesan Sebelum dan Sesudah Redeploy (Tugas C)

1. **Sebelum Redeploy (Build #1 — Container ID: `03da2f8a4d6e`)**:
   ```text
   CONTAINER ID   NAMES                      IMAGE                    STATUS
   03da2f8a4d6e   production-api-container   python-crud-api:latest   Up 26 seconds

   --- POST Pesan 1 ---
   HTTP/1.0 201 Created
   {"status": "created", "message": {"message": "Pesan Uji Persistensi 1 - Sebelum Redeploy (Container 03da2f8a4d6e)", "created_at": "2026-11-07T23:50:17.367824+00:00"}}

   --- POST Pesan 2 ---
   HTTP/1.0 201 Created
   {"status": "created", "message": {"message": "Pesan Uji Persistensi 2 - Sebelum Redeploy (Container 03da2f8a4d6e)", "created_at": "2026-11-07T23:50:17.389760+00:00"}}

   --- GET /messages Sebelum Redeploy ---
   HTTP/1.0 200 OK
   {"messages": [{"message": "Pesan Uji Persistensi 1 - Sebelum Redeploy (Container 03da2f8a4d6e)", "created_at": "2026-11-07T23:50:17.367824+00:00"}, {"message": "Pesan Uji Persistensi 2 - Sebelum Redeploy (Container 03da2f8a4d6e)", "created_at": "2026-11-07T23:50:17.389760+00:00"}], "total": 2}
   ```

2. **Sesudah Redeploy Otomatis (Build #2 — Container ID Berubah menjadi: `58a08ecf5c4e`)**:
   ```text
   CONTAINER ID   NAMES                      IMAGE                    STATUS
   58a08ecf5c4e   production-api-container   python-crud-api:latest   Up 9 seconds

   --- GET /messages Sesudah Redeploy ---
   HTTP/1.0 200 OK
   {"messages": [{"message": "Pesan Uji Persistensi 1 - Sebelum Redeploy (Container 03da2f8a4d6e)", "created_at": "2026-11-07T23:50:17.367824+00:00"}, {"message": "Pesan Uji Persistensi 2 - Sebelum Redeploy (Container 03da2f8a4d6e)", "created_at": "2026-11-07T23:50:17.389760+00:00"}], "total": 2}
   ```
   > **Kesimpulan Persistensi**: Container lama (`03da2f8a4d6e`) dihentikan dan dihapus (`docker stop` & `docker rm`), lalu digantikan oleh container baru (`58a08ecf5c4e`), namun ke-2 pesan yang dibuat sebelum redeploy tetap tersedia (`"total": 2`) karena tersimpan di Docker Named Volume `production-api-data` (`/var/lib/backend_data/messages.json`).

---

## 3. Dokumentasi Kegagalan, Diagnosis, dan Perbaikan (Troubleshooting)

### Kasus 1: Kegagalan Eksekusi `docker` CLI di Dalam Container Jenkins & Opsi Plugin Belum Aktif
- **Gejala:**
  1. Saat memverifikasi `docker exec jenkins-server docker --version` pada container `jenkins/jenkins:lts-jdk17`, muncul error:
     `OCI runtime exec failed: exec failed: unable to start container process: exec: "docker": executable file not found in $PATH`.
  2. Saat membuka halaman konfigurasi job `http://localhost:8080/job/python-crud-api-pipeline/configure`, opsi **`GitHub hook trigger for GITScm polling`** dan **`Pipeline script from SCM`** belum muncul.
- **Diagnosis:**
  1. Pada sistem operasi host Windows (Docker Desktop), binary Docker di host adalah file `.exe` Windows sehingga tidak bisa di-mount langsung ke `/usr/bin/docker` di dalam container Linux `jenkins/jenkins:lts-jdk17`. Selain itu, instalasi `apt-get install --no-install-recommends docker.io` pada Debian 13 (Trixie) hanya menginstal daemon tanpa paket `docker-cli`.
  2. Pada sisi Jenkins UI, plugin `git`, `github`, dan `workflow-cps` baru saja mengunduh pembaruan dependensi `jackson2-api` dan memerlukan *restart* layanan Jenkins agar plugin dimuat penuh ke memori.
- **Perbaikan:**
  1. Memperbarui [`Dockerfile.jenkins`](./Dockerfile.jenkins) menggunakan multi-stage copy `COPY --from=docker:cli /usr/local/bin/docker /usr/bin/docker` serta menginstal `python3` dan `curl`.
  2. Menjalankan `jenkins-plugin-cli --plugins workflow-aggregator git github` dan melakukan `docker restart jenkins-server`.
- **Hasil Uji Ulang:**
  - `docker exec jenkins-server docker version` berhasil menampilkan Client `29.9.3` dan terhubung ke Server Docker Engine `29.8.2`.
  - Setelah `jenkins-server` di-restart, opsi `GitHub hook trigger for GITScm polling` dan `Pipeline script from SCM` aktif, serta Build #1 dan Build #2 berjalan sukses (`Finished: SUCCESS`).

---

## 4. Jawaban 8 Pertanyaan Analisis

### 1. Jelaskan urutan peristiwa dari `git push` hingga container baru berjalan!
1. **Developer melakukan `git push origin main`** dari komputer lokal ke repository GitHub (`https://github.com/ARQ31/python-get-crud.git`).
2. **GitHub mengirim event `push` melalui Webhook** via HTTP `POST` ke URL publik HTTPS **ngrok** (`https://retired-cover-giddiness.ngrok-free.dev/github-webhook/`).
3. **ngrok meneruskan (forward) paket HTTP** ke layanan lokal **Jenkins** di `http://localhost:8080/github-webhook/`.
4. **Jenkins GitHub Plugin menerima event push**, mencocokkan URL repository dan branch `*/main`, lalu memicu build baru pada job `python-crud-api-pipeline`.
5. **Stage 1 (Checkout Code):** Jenkins menggunakan credential `github-pat-readonly` (Fine-grained PAT) untuk melakukan checkout commit terbaru beserta `Jenkinsfile`.
6. **Stage 2 & 3 (Syntax Verification & Automated API Tests):** Jenkins memvalidasi sintaks Python (`python3 -m py_compile app.py test_app.py`) dan menjalankan unit test otomatis (`python3 -m unittest -v test_app.py`) untuk `/health` dan validasi `POST /messages`.
7. **Stage 4 (Build Docker Image):** Jenkins memanggil Docker Engine melalui `/var/run/docker.sock` untuk membangun image `python-crud-api:${BUILD_NUMBER}` dan memberi tag tambahan `python-crud-api:${COMMIT_SHA}` serta `python-crud-api:latest`.
8. **Stage 5 (Automated Deployment):** Jenkins menghentikan dan menghapus container lama (`production-api-container`), memastikan volume `production-api-data` tersedia, dan menjalankan container baru pada jaringan `jenkins-net` dengan me-mount `production-api-data:/var/lib/backend_data`.
9. **Stage 6 (Health Check):** Jenkins melakukan `curl -fsS http://production-api-container:5000/health` dan memastikan respons `HTTP 200` (`{"status": "active", "service": "Backend API"}`).

### 2. Apa perbedaan PAT, webhook secret, dan ngrok authtoken?
| Kredensial | Fungsi Utama | Pihak yang Mengautentikasi | Arah Komunikasi |
| :--- | :--- | :--- | :--- |
| **GitHub Fine-grained PAT** | Mengautentikasi Jenkins saat melakukan `git fetch/checkout` source code dari repository privat GitHub melalui HTTPS. | Jenkins $\rightarrow$ GitHub Server | Outbound dari Jenkins ke GitHub |
| **Webhook Secret** | Memverifikasi keaslian dan integritas payload HTTP POST yang dikirim ke `/github-webhook/` menggunakan HMAC-SHA256 (`X-Hub-Signature-256`) agar pihak luar tidak dapat memalsukan trigger build. | GitHub Webhook $\rightarrow$ Jenkins | Inbound dari GitHub ke Jenkins |
| **ngrok Authtoken** | Mengautentikasi agen CLI `ngrok` di mesin lokal dengan akun cloud ngrok untuk mengizinkan pembuatan tunnel HTTPS publik. | Agen `ngrok` lokal $\rightarrow$ Cloud ngrok | Outbound dari mesin lokal ke server ngrok |

### 3. Mengapa PAT read-only cukup untuk checkout source code, tetapi tidak cukup untuk push kembali ke repository?
- Operasi **checkout / fetch / clone** hanya membaca objek Git (commit, tree, blob) dari server GitHub. Sesuai prinsip *Least Privilege* (hak akses minimum), izin **Repository Contents: Read-only** (dan **Metadata: Read-only**) sudah cukup bagi Jenkins untuk mengambil source code.
- Sebaliknya, operasi **`git push`** menulis objek baru dan mengubah referensi branch di repository GitHub sehingga membutuhkan izin **Contents: Read and write**. Dengan membatasi PAT hanya *Read-only*, apabila kredensial di Jenkins bocor, pihak yang tidak berwenang tetap tidak bisa memodifikasi atau menyuntikkan kode ke repository GitHub.

### 4. Apa risiko memasang Docker socket host (`/var/run/docker.sock`) ke container Jenkins?
- Memberikan akses ke `/var/run/docker.sock` setara dengan memberikan **akses setara `root` terhadap host Docker Engine**.
- Siapa pun yang dapat menjalankan perintah di dalam container Jenkins dapat membuat container baru dengan flag `--privileged` atau melakukan bind-mount direktori root host (`-v /:/host`), membaca/menghapus seluruh container dan volume lain di mesin host, hingga mengambil alih sistem operasi host (*container escape*). Oleh sebab itu, konfigurasi ini hanya digunakan untuk lingkungan lab lokal yang terisolasi.

### 5. Mengapa URL ngrok yang berubah dapat memutus integrasi webhook?
- Pada paket ngrok gratis (*free tier*) tanpa domain statis, setiap kali sesi `ngrok http 8080` dihentikan dan dijalankan kembali, ngrok akan memberikan URL subdomain acak yang baru.
- Sementara itu, **Payload URL** yang tersimpan di pengaturan GitHub Webhook tidak berubah secara otomatis. Akibatnya, GitHub akan tetap mengirim event `push` ke URL ngrok lama yang sudah mati (menghasilkan error `404` / gagal koneksi pada *Recent Deliveries*), sehingga Jenkins tidak menerima notifikasi build sampai Payload URL di GitHub diperbarui.

### 6. Mengapa data pada named volume bertahan setelah container dihapus?
- Penyimpanan internal container (*writable container layer*) bersifat sementara (*ephemeral*) dan terikat pada siklus hidup container tersebut; ketika `docker rm` dijalankan, layer internal container ikut terhapus.
- **Docker Named Volume** (`production-api-data`) dikelola secara terpisah oleh Docker Engine di area penyimpanan host di luar siklus hidup container. Ketika container `03da2f8a4d6e` dihapus (`docker rm`) dan container baru `58a08ecf5c4e` dijalankan dengan `-v production-api-data:/var/lib/backend_data`, volume yang sama dipasang kembali sehingga file `messages.json` tetap utuh.

### 7. Apa perbedaan CI dan CD pada pipeline ini?
- **Continuous Integration (CI)** adalah proses penggabungan kode dan verifikasi otomatis setiap ada perubahan commit:
  - *Stage 1 (Checkout Code)*: Mengambil source code terbaru dari branch `main`.
  - *Stage 2 (Code Syntax Verification)*: Memeriksa sintaks Python (`py_compile`).
  - *Stage 3 (Automated API Tests)*: Menjalankan unit test otomatis untuk `/health` dan validasi `POST /messages`.
  - *Stage 4 (Build Docker Image)*: Membangun artefak image Docker dengan tag nomor build dan commit SHA.
- **Continuous Delivery / Deployment (CD)** adalah proses penerapan artefak image terbaru ke lingkungan runtime secara otomatis beserta verifikasi layanan:
  - *Stage 5 (Automated Deployment)*: Menghentikan container lama dan menjalankan container baru dengan volume persistensi `production-api-data`.
  - *Stage 6 (Health Check)*: Memastikan layanan di container baru merespons `HTTP 200` pada endpoint `/health`.

### 8. Apa yang harus dilakukan jika tahap deploy sukses tetapi health check gagal?
1. **Inspeksi status dan log container** menggunakan `docker ps -a` dan `docker logs production-api-container` untuk mendeteksi penyebab kegagalan runtime (misalnya exception Python saat startup, masalah izin direktori volume, atau port yang gagal di-bind).
2. **Periksa konfigurasi jaringan dan waktu startup (*readiness*)**: pastikan Jenkins dan container aplikasi berada di jaringan Docker yang saling terhubung (`jenkins-net`) dan waktu tunggu sebelum `curl /health` mencukupi.
3. **Lakukan Rollback ke image versi sebelumnya yang sehat**: jalankan ulang container memakai tag nomor build atau tag commit SHA sebelumnya (misalnya `python-crud-api:f9803c8` atau `python-crud-api:1`) agar layanan API kembali pulih sembari memperbaiki commit yang bermasalah.
