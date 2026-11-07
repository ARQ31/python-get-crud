# PRD Praktikum CI CD Jenkins

**CLOUD COMPUTING / TEKNIK TELEKOMUNIKASI / VERSI 1.0**

Proyek ini membangun pipeline yang menerapkan perubahan API pesan dari GitHub ke Docker secara otomatis. Praktikan menguji dan mendokumentasikan setiap tahap sebelum beralih ke tahap berikutnya. Dosen dapat menelusuri hasilnya dari commit hingga respons API.

## Ruang lingkup dan kriteria penerimaan

| **Tugas** | **Kebutuhan** | **Kriteria lulus** |
| --- | --- | --- |
| A · Wajib | API Python dan pipeline Jenkins | Jenkins mengambil kode dari `main`, memeriksa sintaks, membangun image, melakukan deploy, dan menerima HTTP 200 dari `/health`. |
| B · Wajib | Webhook GitHub melalui ngrok | Push baru ke `main` mendapat respons 2xx pada Recent Deliveries dan memicu build Jenkins tanpa Build Now. Commit di log sesuai dengan commit yang di-push. |
| C · Wajib | Persistensi pesan di Docker | Minimal dua pesan yang dibuat sebelum redeploy masih tersedia melalui GET `/messages` setelah ID container berubah. |
| D · Pilihan | Tes otomatis dan tag commit SHA | Tes `/health` dan validasi POST berjalan di Jenkins sebelum build. Image yang dibangun memiliki tag nomor build dan tag berdasarkan SHA commit. |

## Arsitektur lab

GitHub mengirim event push melalui HTTPS ngrok ke `/github-webhook/` pada Jenkins. Jenkins mengambil kode dari repo, menjalankan pemeriksaan, lalu meminta Docker Engine membangun image dan mengganti container API.

Port host awal untuk Jenkins adalah 8080 dan untuk API adalah 5000. Docker memasang volume `production-api-data` ke `/var/lib/backend_data` agar `messages.json` tetap tersedia saat container diganti.

## Prasyarat dan akses

Tahap pertama menetapkan OS, shell, dan cara Jenkins mengakses Docker Engine. Repo privat menjadi pilihan awal. Jenkins memakai fine-grained PAT dengan Contents read-only yang disimpan di Jenkins Credentials. Nilai token, password, dan secret disimpan di konfigurasi layanan terkait dan disamarkan pada bukti.

## Urutan pengerjaan

Setiap tahap selesai setelah hasil pada kolom verifikasi terlihat. Jika satu tahap gagal, catat gejala dan perbaikannya sebelum melanjutkan ke tahap yang bergantung padanya.

| **Tahap** | **Pekerjaan** | **Verifikasi sebelum lanjut** |
| --- | --- | --- |
| 1 | Periksa OS dan shell, lalu cek Git, curl, Docker Engine, Docker Compose, serta port 8080 dan 5000. | Docker Engine merespons. Port tersedia atau port pengganti sudah dicatat. |
| 2 | Buat `app.py`, `Dockerfile`, `.dockerignore`, dan `README.md`. Bangun image dan jalankan API secara manual. | Uji HTTP dasar pada bagian [Pengujian dan bukti pengumpulan](#pengujian-dan-bukti-pengumpulan) lulus. Lepas container manual sebelum Jenkins memakai nama dan port yang sama. Pertahankan volume. |
| 3 | Buat `Jenkinsfile` dan push proyek ke GitHub. Siapkan Jenkins, plugin Pipeline, Git dan GitHub, serta credential `github-pat-readonly`. | Docker dapat diakses dari Jenkins. Job memakai Pipeline script from SCM dengan branch `*/main` dan `Jenkinsfile` di root repo. |
| 4 | Jalankan Build Now satu kali untuk validasi awal tugas A. Periksa checkout, sintaks, build, deploy, dan health check. | Build sukses dan `/health` mengembalikan HTTP 200. Simpan tampilan job dan Console Output. |
| 5 | Tambahkan tes otomatis health dan validasi POST serta tag image berbasis SHA. Jalankan tes sebelum build. | Log memperlihatkan tes lulus. Tag SHA dapat dicocokkan dengan commit checkout dan mengarah ke image yang sama dengan tag nomor build. |
| 6 | Aktifkan trigger GitHub pada job. Jalankan ngrok ke Jenkins, atur webhook push, dan uji dengan commit baru. | Delivery 2xx di GitHub dan build otomatis sukses di Jenkins untuk commit yang sama. |
| 7 | Buat dua pesan uji, catat respons dan ID container, lalu picu redeploy. Susun bukti dan jawaban analisis. | ID container berubah, kedua pesan masih ada, dan bukti A sampai D siap diperiksa. |

### Keputusan saat menyiapkan Jenkins

Periksa ketersediaan Docker CLI, akses Docker Engine, dan Python untuk syntax check. Jika Jenkins berjalan dalam container, uji `/health` melalui alamat API yang dapat dijangkau dari jaringan Jenkins. Salah satu rancangan awal adalah menghubungkan Jenkins dan API ke jaringan Docker yang sama dan memakai nama container API sebagai host.

## Pengujian dan bukti pengumpulan

Jalankan skenario HTTP pada API lokal dan simpan status serta respons. Mulai uji daftar kosong dengan data uji yang bersih. Pada uji persistensi, pertahankan volume yang dipakai sebelum redeploy.

| **Skenario** | **Aksi** | **Hasil yang diharapkan** |
| --- | --- | --- |
| Health | GET `/health` | HTTP 200 dengan status active. |
| Daftar kosong | GET `/messages` sebelum membuat pesan | HTTP 200 dengan messages kosong dan total 0. |
| Buat pesan | POST `/messages` dengan pesan valid | HTTP 201 dan respons memuat `created_at`. |
| Validasi input | POST `/messages` dengan pesan kosong | HTTP 400. |
| Hapus pesan | DELETE `/messages?index=0` setelah ada data | HTTP 200. GET berikutnya menunjukkan pesan telah terhapus. |
| Indeks di luar daftar | DELETE `/messages?index=999` | HTTP 404 pada data uji yang memiliki kurang dari 1.000 pesan. |
| Persistensi | GET `/messages` sebelum dan sesudah redeploy | Kedua pesan uji tetap ada setelah ID container berubah. |

### Paket bukti

**GitHub dan Jenkins.** URL repo, screenshot job sukses, serta Console Output berisi checkout, syntax check, tes, build image, deploy, dan health check.

**Webhook dan API.** Screenshot Recent Deliveries yang sukses, nomor build otomatis dan SHA commit, output curl health dan operasi pesan, serta ID container dan daftar pesan sebelum dan sesudah redeploy.

**Analisis.** Dokumentasikan satu kegagalan yang benar-benar terjadi, diagnosis, perbaikan, dan hasil uji ulang. Jawab delapan pertanyaan panduan mengenai alur push sampai deploy, PAT dan izin akses, webhook secret, ngrok authtoken dan URL tunnel, risiko Docker socket, persistensi volume, CI dan CD, serta respons saat health check gagal.

### Sumber persyaratan

`CICD_Jenkins.pdf`, bagian 9 sampai 13 untuk konfigurasi job, pengujian, bukti, tugas, dan checklist pengumpulan.
