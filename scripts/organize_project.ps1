# Script de organização e limpeza segura do projeto DCKP (Windows)

param(
    [switch]$CleanBuild,
    [switch]$CleanAnalysis,
    [switch]$CleanResults,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

function Step([string]$Message) {
    Write-Host "`n>> $Message" -ForegroundColor Yellow
}

function Remove-IfExists([string]$Path, [switch]$Recurse = $true) {
    if (Test-Path $Path) {
        if ($DryRun) {
            Write-Host "[dry-run] remover: $Path" -ForegroundColor DarkGray
        } else {
            if ($Recurse) {
                Remove-Item -Force -Recurse $Path
            } else {
                Remove-Item -Force $Path
            }
            Write-Host "removido: $Path" -ForegroundColor Green
        }
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DCKP - Organizacao do Projeto" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Step "Limpando temporarios e caches"

$cacheDirs = @(
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache"
)

foreach ($dirName in $cacheDirs) {
    Get-ChildItem -Path . -Directory -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FullName -notmatch '\\(\.git|\.venv|\.venv_wsl|venv|build)\\'
        } |
        Where-Object { $_.Name -eq $dirName } |
        ForEach-Object { Remove-IfExists $_.FullName }
}

Get-ChildItem -Path . -File -Recurse -Force -Include "*.tmp", "*.log", ".DS_Store", "Thumbs.db" -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch '\\(\.git|\.venv|\.venv_wsl|venv|build)\\'
    } |
    ForEach-Object { Remove-IfExists $_.FullName -Recurse:$false }

if ($CleanBuild) {
    Step "Limpando diretorio de build"
    Remove-IfExists "build"
}

if ($CleanAnalysis) {
    Step "Limpando apenas resultados de analise"
    Remove-IfExists "results/analysis"
}

if ($CleanResults) {
    Step "Limpando resultados experimentais"
    Remove-IfExists "results/etapa1"
    Remove-IfExists "results/etapa2"
    Remove-IfExists "results/etapa3"
}

Step "Garantindo estrutura minima de diretorios"
$dirs = @(
    "results/etapa1",
    "results/etapa2",
    "results/etapa3",
    "results/analysis/etapa1",
    "results/analysis/etapa2",
    "results/analysis/etapa3"
)

foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        if ($DryRun) {
            Write-Host "[dry-run] criar: $dir" -ForegroundColor DarkGray
        } else {
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
            Write-Host "criado: $dir" -ForegroundColor Green
        }
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Organizacao concluida" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
