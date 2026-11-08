import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_callout(doc, text, title=""):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F0F4F8")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="1F497D"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    if title:
        run_title = p.add_run(f"{title}\n")
        run_title.bold = True
        run_title.font.name = "Calibri"
        run_title.font.size = Pt(10.5)
        run_title.font.color.rgb = RGBColor(31, 73, 125)
    
    run_text = p.add_run(text)
    run_text.font.name = "Calibri"
    run_text.font.size = Pt(10)
    run_text.font.color.rgb = RGBColor(40, 40, 40)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_code_block(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F5F5F5")
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="12" w:space="0" w:color="CCCCCC"/>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="E0E0E0"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="E0E0E0"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="E0E0E0"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(30, 30, 30)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def format_table(table, col_widths, headers, data):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        hdr_cells[i].width = col_widths[i]
        set_cell_background(hdr_cells[i], "1F497D")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.bold = True
            r.font.name = "Calibri"
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(255, 255, 255)
            
    for row_idx, row_data in enumerate(data):
        row = table.add_row()
        fill_hex = "F9FBFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.text = str(val)
            cell.width = col_widths[col_idx]
            set_cell_background(cell, fill_hex)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(40, 40, 40)
            tcPr = cell._tc.get_or_add_tcPr()
            borders = parse_xml(
                f'<w:tcBorders {nsdecls("w")}>'
                f'<w:left w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>'
                f'<w:top w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>'
                f'<w:right w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>'
                f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>'
                f'</w:tcBorders>'
            )
            tcPr.append(borders)

def build_document():
    doc = Document()
    
    # Page setup - 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # User requested strictly:
    # "diawal filenya tulis Nama: Ahmad Faisal Hafidz, lalu dibaris barunya NIM: 101012300379"
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(2)
    run_nama = p_meta.add_run("Nama: Ahmad Faisal Hafidz\n")
    run_nama.bold = True
    run_nama.font.name = "Calibri"
    run_nama.font.size = Pt(13)
    run_nama.font.color.rgb = RGBColor(20, 20, 20)
    
    run_nim = p_meta.add_run("NIM: 101012300379")
    run_nim.bold = True
    run_nim.font.name = "Calibri"
    run_nim.font.size = Pt(13)
    run_nim.font.color.rgb = RGBColor(20, 20, 20)
    
    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(14)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("LAPORAN PRAKTIKUM CI/CD PIPELINE JENKINS")
    run_title.bold = True
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(18)
    run_title.font.color.rgb = RGBColor(31, 73, 125)
    
    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(16)
    run_sub = p_sub.add_run("Mata Kuliah: Cloud Computing | Program Studi S1 Teknik Telekomunikasi\nOtomasi CI/CD dengan GitHub Webhook, ngrok, Docker Engine, dan Named Volume")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(10.5)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(100, 100, 100)
    
    # Identity Table
    doc.add_heading("Informasi Lingkungan Praktikum", level=2)
    info_table = doc.add_table(rows=1, cols=2)
    format_table(
        info_table,
        [Inches(2.2), Inches(4.3)],
        ["Parameter", "Keterangan / Nilai"],
        [
            ["Nama Mahasiswa", "Ahmad Faisal Hafidz"],
            ["NIM", "101012300379"],
            ["GitHub Repository", "https://github.com/ARQ31/python-get-crud"],
            ["Branch Target", "main"],
            ["Jenkins Job Name", "python-crud-api-pipeline"],
            ["Jenkins Credential ID", "github-pat-readonly (Fine-grained PAT: Contents Read-only)"],
            ["ngrok Public Tunnel", "https://retired-cover-giddiness.ngrok-free.dev"],
            ["GitHub Webhook URL", "https://retired-cover-giddiness.ngrok-free.dev/github-webhook/"],
            ["Docker Network", "jenkins-net"],
            ["Docker Named Volume", "production-api-data (Mount: /var/lib/backend_data)"],
            ["Production Container", "production-api-container (Port Host 5000:5000)"]
        ]
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    
    # Section 1: Ringkasan Tugas PRD
    doc.add_heading("1. Ringkasan Ruang Lingkup dan Kriteria Penerimaan PRD", level=1)
    p_prd = doc.add_paragraph(
        "Berdasarkan dokumen PRD Praktikum CI/CD Jenkins, praktikum ini membangun sistem otomatisasi "
        "yang mencakup verifikasi kode, pengetesan unit otomatis, pembuatan Docker image ber-tag commit SHA, "
        "deployment ke container Docker, trigger webhook via ngrok, dan pengujian persistensi data."
    )
    p_prd.paragraph_format.space_after = Pt(6)
    
    tugas_table = doc.add_table(rows=1, cols=4)
    format_table(
        tugas_table,
        [Inches(1.1), Inches(1.8), Inches(2.4), Inches(1.2)],
        ["Tugas", "Kebutuhan", "Kriteria Lulus PRD", "Status"],
        [
            ["A · Wajib", "API Python & Pipeline Jenkins", "Jenkins checkout main, syntax check, build image, deploy container, dan GET /health menghasilkan HTTP 200.", "LULUS (100%)"],
            ["B · Wajib", "Webhook GitHub via ngrok", "Push baru ke main menerima respons 200 OK pada Recent Deliveries dan memicu build Jenkins otomatis tanpa Build Now.", "LULUS (100%)"],
            ["C · Wajib", "Persistensi Pesan di Docker", "Minimal 2 pesan sebelum redeploy tetap tersedia pada GET /messages setelah ID container berubah.", "LULUS (100%)"],
            ["D · Pilihan", "Otomasi Tes & Tag Commit SHA", "Unit test otomatis /health dan validasi POST berjalan sebelum build; image memiliki tag nomor build dan commit SHA.", "LULUS (100%)"]
        ]
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    
    # Section 2: Bukti Pengujian & Hasil Screenshot
    doc.add_heading("2. Bukti Pengujian & Dokumentasi Visual", level=1)
    
    doc.add_heading("2.1 Screenshot Pipeline Job Jenkins (Build #1 & Build #2)", level=2)
    p_sc1 = doc.add_paragraph(
        "Gambar di bawah ini merupakan tangkapan layar antarmuka Jenkins Job 'python-crud-api-pipeline' "
        "yang menunjukkan riwayat eksekusi Build #1 (manual Build Now) dan Build #2 (otomatis terpicu via GitHub Webhook), "
        "keduanya berstatus sukses (hijau)."
    )
    p_sc1.paragraph_format.space_after = Pt(4)
    
    img_pipeline_path = r"C:\Users\ariqm\Downloads\TUGAS CC\Documentation\pipeline_screenshot.png"
    if os.path.exists(img_pipeline_path):
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.paragraph_format.space_after = Pt(2)
        doc.add_picture(img_pipeline_path, width=Inches(6.2))
        p_cap1 = doc.add_paragraph("Gambar 1: Tampilan Status Jenkins Job python-crud-api-pipeline (Build #1 & Build #2 Sukses)")
        p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap1.paragraph_format.space_after = Pt(10)
        p_cap1.runs[0].font.size = Pt(9)
        p_cap1.runs[0].font.italic = True
        
    doc.add_heading("2.2 Screenshot GitHub Webhook Recent Deliveries (Status 200 OK)", level=2)
    p_sc2 = doc.add_paragraph(
        "Gambar di bawah ini memperlihatkan bukti keberhasilan delivery Webhook dari GitHub ke URL publik ngrok "
        "(https://retired-cover-giddiness.ngrok-free.dev/github-webhook/) dengan status respons HTTP 200 OK "
        "untuk event push commit bc65727be0e6d2acd55c2677bbf77da22b0acada."
    )
    p_sc2.paragraph_format.space_after = Pt(4)
    
    img_webhook_path = r"C:\Users\ariqm\Downloads\TUGAS CC\Documentation\github_webhook_screenshot.png"
    if os.path.exists(img_webhook_path):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_after = Pt(2)
        doc.add_picture(img_webhook_path, width=Inches(6.2))
        p_cap2 = doc.add_paragraph("Gambar 2: Screenshot GitHub Webhook Recent Deliveries dengan HTTP Response 200 OK")
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap2.paragraph_format.space_after = Pt(10)
        p_cap2.runs[0].font.size = Pt(9)
        p_cap2.runs[0].font.italic = True
        
    doc.add_heading("2.3 Bukti Console Output Build #2 (Otomatis via Webhook)", level=2)
    p_log_intro = doc.add_paragraph(
        "Hasil Console Output Build #2 diambil dari file dokumentasi 'Documentation/#2.txt' "
        "(dan arsip lengkap 'Documentation/Console - #2 - Jenkins.pdf'). Log ini membuktikan seluruh tahapan pipeline "
        "mulai dari trigger webhook GitHub, syntax check, automated unittest, build Docker dengan commit SHA, "
        "deploy container baru, dan validasi health check berhasil secara otomatis."
    )
    p_log_intro.paragraph_format.space_after = Pt(4)
    
    txt_log_path = r"C:\Users\ariqm\Downloads\TUGAS CC\Documentation\#2.txt"
    if os.path.exists(txt_log_path):
        with open(txt_log_path, "r", encoding="utf-8") as f:
            raw_log = f.read()
        add_code_block(doc, raw_log)
    else:
        add_callout(doc, "File Documentation/#2.txt tidak ditemukan di workspace.", "Peringatan Log")
        
    # Section 3: Pengujian HTTP CRUD API
    doc.add_heading("3. Hasil Pengujian Endpoint REST API (6 Skenario HTTP)", level=1)
    p_crud_desc = doc.add_paragraph(
        "Pengujian HTTP REST API dilakukan sesuai skenario pada PRD untuk memvalidasi fungsi aplikasi, "
        "kepatuhan status kode HTTP, format JSON, dan validasi input:"
    )
    p_crud_desc.paragraph_format.space_after = Pt(4)
    
    crud_table = doc.add_table(rows=1, cols=4)
    format_table(
        crud_table,
        [Inches(1.1), Inches(1.9), Inches(1.9), Inches(1.6)],
        ["Skenario", "Aksi / Perintah HTTP", "Hasil yang Diharapkan", "Hasil Aktual"],
        [
            ["Health Check", "GET /health", "HTTP 200, status active, service Backend API", "HTTP 200 OK\n{\"status\": \"active\", \"service\": \"Backend API\"}"],
            ["Daftar Kosong", "GET /messages (awal)", "HTTP 200, messages: [], total: 0", "HTTP 200 OK\n{\"messages\": [], \"total\": 0}"],
            ["Buat Pesan", "POST /messages\nBody: {\"message\": \"Pesan pertama dari praktikum\"}", "HTTP 201, memuat created_at UTC", "HTTP 201 Created\n{\"status\": \"created\", \"message\": {...}}"],
            ["Validasi Input", "POST /messages\nBody: {\"message\": \"   \"}", "HTTP 400 Bad Request", "HTTP 400 Bad Request\n{\"error\": \"message must not be empty\"}"],
            ["Hapus Pesan", "DELETE /messages?index=0", "HTTP 200, item terhapus, GET berikutnya kosong", "HTTP 200 OK, removed item returned.\nGET berikutnya: total: 0"],
            ["Indeks di Luar Jangkauan", "DELETE /messages?index=999", "HTTP 404 Not Found", "HTTP 404 Not Found\n{\"error\": \"Message not found\"}"]
        ]
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    
    # Section 4: Bukti Persistensi Data Docker
    doc.add_heading("4. Bukti Persistensi Data pada Docker Named Volume (Tugas C)", level=1)
    p_pers_desc = doc.add_paragraph(
        "Kriteria Tugas C mewajibkan pembuatan minimal dua pesan sebelum redeploy, kemudian membuktikan bahwa "
        "pesan-pesan tersebut tetap utuh setelah container dihentikan, dihapus, dan dibuat ulang oleh pipeline Jenkins."
    )
    p_pers_desc.paragraph_format.space_after = Pt(4)
    
    add_callout(
        doc,
        "1. KONDISI SEBELUM REDEPLOY (Build #1):\n"
        "   - Container ID Aktif: 03da2f8a4d6e\n"
        "   - Pesan 1: 'Pesan Uji Persistensi 1 - Sebelum Redeploy (Container 03da2f8a4d6e)'\n"
        "   - Pesan 2: 'Pesan Uji Persistensi 2 - Sebelum Redeploy (Container 03da2f8a4d6e)'\n"
        "   - GET /messages: Total 2 pesan.\n\n"
        "2. PROSES REDEPLOY OLEH PIPELINE JENKINS (Build #2):\n"
        "   - docker stop production-api-container\n"
        "   - docker rm production-api-container\n"
        "   - docker volume create production-api-data\n"
        "   - docker run -d --name production-api-container -v production-api-data:/var/lib/backend_data ...\n\n"
        "3. KONDISI SESUDAH REDEPLOY (Build #2):\n"
        "   - Container ID Baru: 58a08ecf5c4e (Berubah terbukti diganti container baru)\n"
        "   - Respons GET /messages:\n"
        "     HTTP/1.0 200 OK\n"
        "     {\"messages\": [\n"
        "       {\"message\": \"Pesan Uji Persistensi 1 - Sebelum Redeploy (Container 03da2f8a4d6e)\", \"created_at\": \"2026-11-07T23:50:17.367824+00:00\"},\n"
        "       {\"message\": \"Pesan Uji Persistensi 2 - Sebelum Redeploy (Container 03da2f8a4d6e)\", \"created_at\": \"2026-11-07T23:50:17.389760+00:00\"}\n"
        "     ], \"total\": 2}\n\n"
        "KESIMPULAN: Data pesan tersimpan di named volume 'production-api-data' (/var/lib/backend_data/messages.json) "
        "sehingga tetap bertahan melintasi siklus hidup container baru.",
        "Ringkasan Bukti Persistensi Data"
    )
    
    # Section 5: Troubleshooting
    doc.add_heading("5. Dokumentasi Troubleshooting, Diagnosis, dan Perbaikan", level=1)
    doc.add_heading("Kasus: Inkompatibilitas Mount Docker CLI Host Windows & Plugin Belum Aktif", level=2)
    
    add_callout(
        doc,
        "A. GEJALA:\n"
        "1. Saat memeriksa 'docker exec jenkins-server docker --version' pada image default jenkins/jenkins:lts-jdk17, "
        "   muncul error: 'OCI runtime exec failed: exec failed: unable to start container process: exec: \"docker\": executable file not found in $PATH'.\n"
        "2. Di antarmuka konfigurasi job Jenkins, opsi 'GitHub hook trigger for GITScm polling' dan 'Pipeline script from SCM' "
        "   belum muncul di browser.\n\n"
        "B. DIAGNOSIS:\n"
        "1. Pada Docker Desktop Windows, binary Docker di host adalah executable Windows (docker.exe), sehingga perintah panduan "
        "   Linux '-v \"$(which docker)\":/usr/bin/docker' tidak dapat dijalankan di dalam container Linux Jenkins. "
        "   Selain itu, instalasi apt-get docker.io pada Debian Trixie tidak menyertakan binary docker-cli mandiri.\n"
        "2. Plugin git, github, dan workflow-cps baru saja selesai mengunduh pembaruan dependensi (jackson2-api) dan membutuhkan "
        "   restart layanan Jenkins agar extension terdaftar sepenuhnya ke memori sistem.\n\n"
        "C. PERBAIKAN:\n"
        "1. Membuat 'Dockerfile.jenkins' dengan multi-stage copy: 'COPY --from=docker:cli /usr/local/bin/docker /usr/bin/docker' "
        "   serta menginstal python3 dan curl di dalam container Jenkins.\n"
        "2. Menjalankan 'jenkins-plugin-cli --plugins workflow-aggregator git github' dan melakukan 'docker restart jenkins-server'.\n\n"
        "D. HASIL UJI ULANG:\n"
        "1. Perintah 'docker exec jenkins-server docker version' berhasil merespons Client 29.9.3 dan terhubung ke Docker Engine 29.8.2.\n"
        "2. Opsi webhook trigger dan Pipeline SCM muncul sempurna, serta Build #1 dan Build #2 berhasil 100% (Finished: SUCCESS).",
        "Laporan Kasus Troubleshooting Nyata"
    )
    
    # Section 6: Jawaban 8 Pertanyaan Analisis
    doc.add_heading("6. Jawaban 8 Pertanyaan Analisis PRD", level=1)
    
    questions = [
        (
            "1. Jelaskan urutan peristiwa dari git push hingga container baru berjalan!",
            "Urutan peristiwa dari awal hingga akhir adalah sebagai berikut:\n"
            "a. Developer melakukan 'git push origin main' ke repository GitHub (https://github.com/ARQ31/python-get-crud.git).\n"
            "b. GitHub mendeteksi event push dan mengirimkan HTTP POST webhook berisi metadata commit ke URL ngrok (https://retired-cover-giddiness.ngrok-free.dev/github-webhook/).\n"
            "c. Agen ngrok lokal meneruskan (forward) request HTTP tersebut ke port Jenkins lokal (http://localhost:8080/github-webhook/).\n"
            "d. Jenkins GitHub Plugin memproses payload webhook, mencocokkan URL repository dan branch target (*/main), lalu memicu job 'python-crud-api-pipeline'.\n"
            "e. Stage 1 (Checkout Code): Jenkins mengunduh kode terbaru dan Jenkinsfile dari GitHub menggunakan credential 'github-pat-readonly'.\n"
            "f. Stage 2 & 3 (Syntax Check & Automated Tests): Jenkins memverifikasi sintaks Python dengan py_compile dan menjalankan unittest otomatis (test_app.py).\n"
            "g. Stage 4 (Build Docker Image): Jenkins memerintahkan Docker host melalui /var/run/docker.sock untuk membangun image baru dengan tag nomor build (${BUILD_NUMBER}) dan commit SHA (${COMMIT_SHA}).\n"
            "h. Stage 5 (Automated Deployment): Jenkins menghentikan container lama (docker stop), menghapusnya (docker rm), memastikan named volume 'production-api-data' ada, dan menjalankan container baru dengan volume tersebut.\n"
            "i. Stage 6 (Health Check): Jenkins melakukan request curl ke endpoint /health pada container baru dan memverifikasi respons HTTP 200 OK."
        ),
        (
            "2. Apa perbedaan PAT, webhook secret, dan ngrok authtoken?",
            "Perbedaan ketiga kredensial tersebut mencakup fungsi, otorisasi, dan arah alirannya:\n"
            "• GitHub Fine-grained PAT: Kredensial yang digunakan oleh Jenkins untuk mengautentikasi dan mengunduh source code dari repository privat GitHub melalui HTTPS. Aliran: Outbound dari Jenkins ke GitHub.\n"
            "• Webhook Secret: String rahasia yang disepakati antara GitHub dan Jenkins untuk memvalidasi integritas dan keaslian payload webhook menggunakan signature HMAC-SHA256 (header X-Hub-Signature-256). Aliran: Inbound dari GitHub ke Jenkins.\n"
            "• ngrok Authtoken: Kredensial akun untuk mengotentikasi agen ngrok di komputer lokal ke platform cloud ngrok agar diizinkan membuka tunnel publik HTTPS. Aliran: Outbound dari mesin lokal ke cloud ngrok."
        ),
        (
            "3. Mengapa PAT read-only cukup untuk checkout source code, tetapi tidak cukup untuk push kembali ke repository?",
            "Karena proses 'git checkout / fetch / clone' hanya melakukan operasi pembacaan data (read-only) terhadap objek Git di server GitHub. Sesuai prinsip keamanan Least Privilege (hak akses minimum), izin 'Repository Contents: Read-only' sudah cukup untuk mengambil kode.\n"
            "Sebaliknya, operasi 'git push' memodifikasi state repository (menulis commit dan memperbarui referensi branch) sehingga membutuhkan izin 'Contents: Read and write'. Membatasi PAT pada level Read-only memastikan bahwa jika token Jenkins bocor, penyerang tidak dapat menyuntikkan kode berbahaya ke repository GitHub."
        ),
        (
            "4. Apa risiko memasang Docker socket host (/var/run/docker.sock) ke container Jenkins?",
            "Memasang /var/run/docker.sock memberikan hak akses penuh setara 'root' pada host Docker daemon. Proses di dalam container Jenkins dapat mengeksekusi perintah Docker apa pun terhadap host, termasuk membuat container privileged, melakukan bind-mount ke root filesystem host (-v /:/host), mematikan/menghapus container lain, atau mengakses data rahasia pada volume lain (container breakout/escape). Oleh karena itu, arsitektur ini hanya aman digunakan pada mesin lab pengembang terisolasi, bukan pada lingkungan produksi multi-tenant."
        ),
        (
            "5. Mengapa URL ngrok yang berubah dapat memutus integrasi webhook?",
            "Pada akun ngrok gratis (free tier) tanpa domain statis terdaftar, setiap kali sesi ngrok dimulai ulang (restart), ngrok akan menghasilkan subdomain acak baru. Sementara itu, Payload URL pada pengaturan Webhook GitHub bersifat statis. Jika URL ngrok berubah namun konfigurasi di GitHub belum diperbarui, GitHub akan tetap mengirim request ke URL lama yang sudah tidak aktif (menghasilkan kegagalan koneksi 404/Connection Refused), sehingga Jenkins tidak pernah menerima event push."
        ),
        (
            "6. Mengapa data pada named volume bertahan setelah container dihapus?",
            "Filesystem internal sebuah container (writable layer) bersifat ephemeral dan siklus hidupnya terikat langsung dengan container tersebut; saat container di-remove (docker rm), writable layer-nya ikut musnah. Sebaliknya, Docker Named Volume dikelola secara independen oleh Docker Engine di direktori host di luar container lifecycle. Ketika container dihapus dan container baru dijalankan dengan memasang volume yang sama (-v production-api-data:/var/lib/backend_data), Docker memasang kembali storage yang sama sehingga file messages.json beserta isinya tetap utuh."
        ),
        (
            "7. Apa perbedaan CI dan CD pada pipeline ini?",
            "• Continuous Integration (CI): Tahap integrasi kode dan penjaminan kualitas secara otomatis setiap kali ada commit baru. Pada pipeline ini, CI mencakup Stage 1 (Checkout Code), Stage 2 (Syntax Check py_compile), Stage 3 (Automated Unit Tests), dan Stage 4 (Build Docker Image & Tagging).\n"
            "• Continuous Delivery / Deployment (CD): Tahap penerapan artefak hasil build ke lingkungan runtime secara otomatis. Pada pipeline ini, CD mencakup Stage 5 (Automated Deployment dengan docker stop, rm, dan run baru dengan persistensi volume) serta Stage 6 (Health Check verifikasi endpoint /health HTTP 200)."
        ),
        (
            "8. Apa yang harus dilakukan jika tahap deploy sukses tetapi health check gagal?",
            "Langkah-langkah terstruktur yang harus dilakukan adalah:\n"
            "a. Periksa status dan log container menggunakan 'docker ps -a' dan 'docker logs production-api-container' untuk mengidentifikasi penyebab crash atau error (misal SyntaxError, runtime exception, atau port collision).\n"
            "b. Periksa konfigurasi port binding dan jaringan (apakah container berada pada network yang sama dengan Jenkins dan port 5000 tidak terblokir firewall).\n"
            "c. Periksa kesiapan startup (readiness) dan naikkan jeda sleep sebelum health check jika aplikasi membutuhkan waktu inisialisasi lebih lama.\n"
            "d. Lakukan rollback otomatis atau manual ke image versi build sebelumnya yang stabil (menggunakan tag build number atau commit SHA sebelumnya, misal python-crud-api:f9803c8) untuk meminimalkan downtime layanan."
        )
    ]
    
    for q_title, q_ans in questions:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        r_q = p_q.add_run(q_title)
        r_q.bold = True
        r_q.font.name = "Calibri"
        r_q.font.size = Pt(11)
        r_q.font.color.rgb = RGBColor(31, 73, 125)
        
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(0)
        p_a.paragraph_format.space_after = Pt(6)
        p_a.paragraph_format.line_spacing = 1.15
        r_a = p_a.add_run(q_ans)
        r_a.font.name = "Calibri"
        r_a.font.size = Pt(10)
        r_a.font.color.rgb = RGBColor(40, 40, 40)
        
    output_filename = "Laporan_Praktikum_CICD_Jenkins_Ahmad_Faisal_Hafidz.docx"
    doc.save(output_filename)
    print(f"Document successfully created: {output_filename}")

if __name__ == "__main__":
    build_document()
