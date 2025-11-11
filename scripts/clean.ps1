# Script para limpar arquivos de build e resultados temporários
# Uso: .\clean.ps1

param(
    [switch]$All,
    [switch]$Build,
    [switch]$Results
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Limpeza do Projeto DCKP-Matheuristics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not $All -and -not $Build -and -not $Results) {
    Write-Host "`nUso:" -ForegroundColor Yellow
    Write-Host "  .\scripts\clean.ps1 -Build      # Limpa apenas build" -ForegroundColor White
    Write-Host "  .\scripts\clean.ps1 -Results    # Limpa apenas resultados" -ForegroundColor White
    Write-Host "  .\scripts\clean.ps1 -All        # Limpa tudo" -ForegroundColor White
    Write-Host ""
    exit 0
}

if ($All -or $Build) {
    Write-Host "`nLimpando diretório de build..." -ForegroundColor Yellow
    if (Test-Path "build") {
        Remove-Item -Recurse -Force build
        Write-Host "  ✓ Diretório build removido" -ForegroundColor Green
    } else {
        Write-Host "  - Diretório build não existe" -ForegroundColor Gray
    }
}

if ($All -or $Results) {
    Write-Host "`nLimpando resultados temporários..." -ForegroundColor Yellow
    if (Test-Path "results\etapa1") {
        # Remove apenas arquivos temporários, mantém estrutura
        Remove-Item "results\etapa1\*.csv" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force "results\etapa1\analysis" -ErrorAction SilentlyContinue
        Write-Host "  ✓ Resultados temporários removidos" -ForegroundColor Green
    } else {
        Write-Host "  - Diretório de resultados não existe" -ForegroundColor Gray
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Limpeza concluída!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
