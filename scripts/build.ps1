# Script para compilar o projeto DCKP-Matheuristics no Windows
# Uso: .\build.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Compilando DCKP-Matheuristics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Cria diretório de build se não existir
if (!(Test-Path -Path "build")) {
    Write-Host "`nCriando diretório build..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "build" | Out-Null
}

# Entra no diretório de build
Set-Location build

# Executa CMake
Write-Host "`nConfigurando projeto com CMake..." -ForegroundColor Yellow
cmake .. -G "MinGW Makefiles"

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nErro na configuração do CMake!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

# Compila o projeto
Write-Host "`nCompilando..." -ForegroundColor Yellow
cmake --build . --config Release

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nErro na compilação!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

# Volta ao diretório raiz
Set-Location ..

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Compilação concluída com sucesso!" -ForegroundColor Green
Write-Host "Executável: build\bin\dckp_solver.exe" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
