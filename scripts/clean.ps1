# Script para limpar arquivos de build e resultados
# Suporta limpeza separada de Etapa 1 e Etapa 2

param(
    [switch]$All,
    [switch]$Build,
    [switch]$Results,
    [switch]$Etapa1,
    [switch]$Etapa2
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Limpeza do Projeto DCKP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not $All -and -not $Build -and -not $Results -and -not $Etapa1 -and -not $Etapa2) {
    Write-Host "`nUso:" -ForegroundColor Yellow
    Write-Host "  .\scripts\clean.ps1 -Build      # Limpa build"
    Write-Host "  .\scripts\clean.ps1 -Results    # Limpa todos resultados (etapa1 + etapa2)"
    Write-Host "  .\scripts\clean.ps1 -Etapa1     # Limpa apenas resultados da Etapa 1"
    Write-Host "  .\scripts\clean.ps1 -Etapa2     # Limpa apenas resultados da Etapa 2"
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
    Write-Host "`nLimpando todos os resultados..." -ForegroundColor Yellow
    if (Test-Path "results\etapa1") {
        Remove-Item "results\etapa1\*.csv" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force "results\etapa1\analysis" -ErrorAction SilentlyContinue
        Write-Host "  Resultados Etapa 1 removidos" -ForegroundColor Green
    }
    if (Test-Path "results\etapa2") {
        Remove-Item "results\etapa2\*.csv" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force "results\etapa2\analysis" -ErrorAction SilentlyContinue
        Write-Host "  Resultados Etapa 2 removidos" -ForegroundColor Green
    }
}

if ($Etapa1 -and -not $All -and -not $Results) {
    Write-Host "`nLimpando resultados da Etapa 1..." -ForegroundColor Yellow
    if (Test-Path "results\etapa1") {
        Remove-Item "results\etapa1\*.csv" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force "results\etapa1\analysis" -ErrorAction SilentlyContinue
        Write-Host "  Resultados Etapa 1 removidos" -ForegroundColor Green
    } else {
        Write-Host "  Nenhum diretorio results\etapa1 encontrado" -ForegroundColor Yellow
    }
}

if ($Etapa2 -and -not $All -and -not $Results) {
    Write-Host "`nLimpando resultados da Etapa 2..." -ForegroundColor Yellow
    if (Test-Path "results\etapa2") {
        Remove-Item "results\etapa2\*.csv" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force "results\etapa2\analysis" -ErrorAction SilentlyContinue
        Write-Host "  Resultados Etapa 2 removidos" -ForegroundColor Green
    } else {
        Write-Host "  Nenhum diretorio results\etapa2 encontrado" -ForegroundColor Yellow
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Limpeza concluida!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
