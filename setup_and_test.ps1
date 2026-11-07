<#
.SYNOPSIS
    Automated execution & verification script for PRD Praktikum CI/CD Jenkins
    Supports:
      - Stage 1: Prerequisite & Port Check
      - Stage 2: Manual Docker Build & CRUD Verification
      - Stage 3: Start Jenkins in Docker (with Docker CLI + Python 3 installed)
      - Stage 7: Persistence Verification (Create 2 messages -> Redeploy -> Verify)
#>

param(
    [ValidateSet("all", "check", "manual-test", "start-jenkins", "persistence-test")]
    [string]$Step = "all"
)

$ErrorActionPreference = "Continue"

function Invoke-Stage1Check {
    Write-Host "`n=========================================" -ForegroundColor Cyan
    Write-Host "  TAHAP 1: Pemeriksaan Lingkungan & Port" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    git --version
    curl.exe --version | Select-Object -First 1
    docker --version
    docker compose version
    docker info --format "Docker Engine Server Version: {{.ServerVersion}}"
}

function Invoke-Stage2ManualTest {
    Write-Host "`n=========================================" -ForegroundColor Cyan
    Write-Host "  TAHAP 2: Build Manual & Uji HTTP CRUD" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan

    docker rm -f production-api-container 2>$null | Out-Null
    docker volume rm production-api-data 2>$null | Out-Null

    docker build -t python-crud-api:manual .
    docker volume create production-api-data | Out-Null
    docker run -d --name production-api-container `
        -p 5000:5000 `
        -v production-api-data:/var/lib/backend_data `
        python-crud-api:manual

    Start-Sleep -Seconds 2

    Write-Host "`n[1] Health (GET /health):" -ForegroundColor Yellow
    curl.exe -i -s http://localhost:5000/health

    Write-Host "`n`n[2] Daftar kosong (GET /messages):" -ForegroundColor Yellow
    curl.exe -i -s http://localhost:5000/messages

    Write-Host "`n`n[3] Buat pesan valid (POST /messages):" -ForegroundColor Yellow
    '{"message":"Pesan pertama dari praktikum"}' | curl.exe -i -s -X POST http://localhost:5000/messages -H "Content-Type: application/json" --data-binary "@-"

    Write-Host "`n`n[4] Validasi input kosong (POST /messages):" -ForegroundColor Yellow
    '{"message":"   "}' | curl.exe -i -s -X POST http://localhost:5000/messages -H "Content-Type: application/json" --data-binary "@-"

    Write-Host "`n`n[5] Hapus pesan (DELETE /messages?index=0) & verifikasi GET:" -ForegroundColor Yellow
    curl.exe -i -s -X DELETE "http://localhost:5000/messages?index=0"
    Write-Host "`n--- Setelah DELETE ---"
    curl.exe -i -s http://localhost:5000/messages

    Write-Host "`n`n[6] Indeks di luar daftar (DELETE /messages?index=999):" -ForegroundColor Yellow
    curl.exe -i -s -X DELETE "http://localhost:5000/messages?index=999"

    Write-Host "`n`n[Cleanup] Menghentikan container manual & mempertahankan volume production-api-data..." -ForegroundColor Green
    docker stop production-api-container | Out-Null
    docker rm production-api-container | Out-Null
}

function Invoke-Stage3JenkinsSetup {
    Write-Host "`n=========================================" -ForegroundColor Cyan
    Write-Host "  TAHAP 3: Menyiapkan Jenkins di Docker" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan

    docker network inspect jenkins-net 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        docker network create jenkins-net | Out-Null
    }
    docker volume create jenkins-data | Out-Null

    Write-Host "Building Jenkins image with Docker CLI & Python 3 (Dockerfile.jenkins)..." -ForegroundColor Yellow
    docker build -t jenkins-cicd-lab:lts-jdk17 -f Dockerfile.jenkins .

    docker rm -f jenkins-server 2>$null | Out-Null
    docker run -d `
        --name jenkins-server `
        --network jenkins-net `
        -p 8080:8080 -p 50000:50000 `
        -v jenkins-data:/var/jenkins_home `
        -v /var/run/docker.sock:/var/run/docker.sock `
        --restart unless-stopped `
        jenkins-cicd-lab:lts-jdk17

    Write-Host "Verifikasi Docker CLI dan Python3 di dalam container Jenkins:" -ForegroundColor Yellow
    docker exec jenkins-server docker --version
    docker exec jenkins-server python3 --version
    Write-Host "`nJenkins sedang berjalan di http://localhost:8080" -ForegroundColor Green
    Write-Host "Untuk melihat Initial Admin Password (tunggu ~20 detik jika baru pertama kali):" -ForegroundColor Yellow
    Write-Host "  docker exec jenkins-server cat /var/jenkins_home/secrets/initialAdminPassword"
}

function Invoke-Stage7PersistenceTest {
    Write-Host "`n=========================================" -ForegroundColor Cyan
    Write-Host "  TAHAP 7: Uji Persistensi Volume Docker" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan

    Write-Host "[Sebelum Redeploy] Container ID aktif:" -ForegroundColor Yellow
    docker ps --filter "name=production-api-container" --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}"

    Write-Host "`nMembuat 2 pesan uji sebelum redeploy..." -ForegroundColor Yellow
    '{"message":"Pesan Uji Persistensi 1 (Sebelum Redeploy)"}' | curl.exe -i -s -X POST http://localhost:5000/messages -H "Content-Type: application/json" --data-binary "@-"
    Write-Host ""
    '{"message":"Pesan Uji Persistensi 2 (Sebelum Redeploy)"}' | curl.exe -i -s -X POST http://localhost:5000/messages -H "Content-Type: application/json" --data-binary "@-"

    Write-Host "`n`nDaftar pesan sebelum redeploy:" -ForegroundColor Yellow
    curl.exe -s http://localhost:5000/messages
    Write-Host ""
}

switch ($Step) {
    "check"            { Invoke-Stage1Check }
    "manual-test"      { Invoke-Stage2ManualTest }
    "start-jenkins"    { Invoke-Stage3JenkinsSetup }
    "persistence-test" { Invoke-Stage7PersistenceTest }
    "all" {
        Invoke-Stage1Check
        Invoke-Stage2ManualTest
        Invoke-Stage3JenkinsSetup
    }
}

