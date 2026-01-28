# Script para compilar o projeto DCKP

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Compilando DCKP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (!(Test-Path "build")) {
    New-Item -ItemType Directory -Path "build" | Out-Null
}

Set-Location build

Write-Host "`nConfigurando CMake..." -ForegroundColor Yellow
cmake .. -G "MinGW Makefiles"

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nErro no CMake!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "`nCompilando..." -ForegroundColor Yellow
cmake --build . --config Release

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nErro na compilacao!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Compilacao concluida!" -ForegroundColor Green
Write-Host "Executavel: build\bin\dckp_solver.exe" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
