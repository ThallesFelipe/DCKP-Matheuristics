# Script para limpar arquivos de build e resultados

param(
    [switch]$All,
    [switch]$Build,
    [switch]$Results
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Limpeza do Projeto DCKP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not $All -and -not $Build -and -not $Results) {
    Write-Host "`nUso:" -ForegroundColor Yellow
    Write-Host "  .\scripts\clean.ps1 -Build      # Limpa build"
    Write-Host "  .\scripts\clean.ps1 -Results    # Limpa resultados"
    Write-Host "  .\scripts\clean.ps1 -All        # Limpa tudo"
    exit 0
}

if ($All -or $Build) {
    Write-Host "`nLimpando build..." -ForegroundColor Yellow
    if (Test-Path "build") {
        Remove-Item -Recurse -Force build
        Write-Host "  Build removido" -ForegroundColor Green
    }
}

if ($All -or $Results) {
    Write-Host "`nLimpando resultados..." -ForegroundColor Yellow
    if (Test-Path "results\etapa1") {
        Remove-Item "results\etapa1\*.csv" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force "results\etapa1\analysis" -ErrorAction SilentlyContinue
        Write-Host "  Resultados removidos" -ForegroundColor Green
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Limpeza concluida!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
