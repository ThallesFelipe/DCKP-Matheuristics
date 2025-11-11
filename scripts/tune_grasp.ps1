# Script para calibrar o parâmetro alpha do GRASP
# Uso: .\tune_grasp.ps1

param(
    [string]$instance = "DCKP-instances\DCKP-instances-set I-100\I1 - I10\1I1"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GRASP - Calibração do parâmetro alpha" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Verifica se o executável existe
$executable = "build\bin\dckp_solver.exe"
if (!(Test-Path $executable)) {
    Write-Host "`nExecutável não encontrado: $executable" -ForegroundColor Red
    Write-Host "Execute primeiro: .\scripts\build.ps1" -ForegroundColor Yellow
    exit 1
}

# Cria diretório de resultados se não existir
if (!(Test-Path -Path "results\etapa1")) {
    New-Item -ItemType Directory -Path "results\etapa1" -Force | Out-Null
}

Write-Host "`nInstância: $instance" -ForegroundColor Yellow
Write-Host "Executando calibração..." -ForegroundColor Yellow
Write-Host "(Isso pode levar alguns minutos)`n" -ForegroundColor Yellow

& $executable tune $instance

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Calibração concluída!" -ForegroundColor Green
Write-Host "Resultados: results\etapa1\alpha_tuning.csv" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
