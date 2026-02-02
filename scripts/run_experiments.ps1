# Script para executar experimentos com instancias do DCKP
# Suporta execução separada de Etapa 1 (Construtivas) e Etapa 2 (Buscas Locais)

param(
    [Parameter(Position=0)]
    [ValidateSet("etapa1", "etapa2", "ambas", "")]
    [string]$Etapa = "",
    [switch]$Set1Only,
    [switch]$Set2Only
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DCKP - Experimentos" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$executable = "build\bin\dckp_solver.exe"
if (!(Test-Path $executable)) {
    Write-Host "`nExecutavel nao encontrado: $executable" -ForegroundColor Red
    Write-Host "Execute primeiro: .\scripts\build.ps1" -ForegroundColor Yellow
    exit 1
}

# Criar diretorios de resultados
if (!(Test-Path "results\etapa1")) {
    New-Item -ItemType Directory -Path "results\etapa1" -Force | Out-Null
}
if (!(Test-Path "results\etapa2")) {
    New-Item -ItemType Directory -Path "results\etapa2" -Force | Out-Null
}

function Show-Menu {
    Write-Host "`nEscolha o modo de execucao:" -ForegroundColor Yellow
    Write-Host "  1) Etapa 1 - Heuristicas Construtivas (Greedy + GRASP)"
    Write-Host "  2) Etapa 2 - Buscas Locais (GRASP + HC + VND)"
    Write-Host "  3) Ambas Etapas"
    Write-Host "  4) Teste rapido (1 instancia)"
    Write-Host "  0) Sair"
    Write-Host ""
    $choice = Read-Host "Opcao"
    return $choice
}

function Run-Etapa1 {
    param([bool]$OnlySet1, [bool]$OnlySet2)
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "ETAPA 1 - Heuristicas Construtivas" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    if (!$OnlySet2) {
        Write-Host "`n--- Processando I1-I10 (Etapa 1) ---" -ForegroundColor Yellow
        & $executable batch-etapa1 "DCKP-instances\DCKP-instances-set I-100\I1 - I10" "results\etapa1\results_I1_I10.csv"
        
        Write-Host "`n--- Processando I11-I20 (Etapa 1) ---" -ForegroundColor Yellow
        & $executable batch-etapa1 "DCKP-instances\DCKP-instances-set I-100\I11 - I20" "results\etapa1\results_I11_I20.csv"
    }
    
    if (!$OnlySet1) {
        Write-Host "`n--- Set II (Etapa 1) requer execucao via Makefile ---" -ForegroundColor Yellow
        Write-Host "Use: make run-etapa1-set2" -ForegroundColor Yellow
    }
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "ETAPA 1 Concluida!" -ForegroundColor Green
    Write-Host "Resultados em: results\etapa1\" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}

function Run-Etapa2 {
    param([bool]$OnlySet1, [bool]$OnlySet2)
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "ETAPA 2 - Buscas Locais" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    if (!$OnlySet2) {
        Write-Host "`n--- Processando I1-I10 (Etapa 2) ---" -ForegroundColor Yellow
        & $executable batch-etapa2 "DCKP-instances\DCKP-instances-set I-100\I1 - I10" "results\etapa2\results_I1_I10.csv"
        
        Write-Host "`n--- Processando I11-I20 (Etapa 2) ---" -ForegroundColor Yellow
        & $executable batch-etapa2 "DCKP-instances\DCKP-instances-set I-100\I11 - I20" "results\etapa2\results_I11_I20.csv"
    }
    
    if (!$OnlySet1) {
        Write-Host "`n--- Set II (Etapa 2) requer execucao via Makefile ---" -ForegroundColor Yellow
        Write-Host "Use: make run-etapa2-set2" -ForegroundColor Yellow
    }
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "ETAPA 2 Concluida!" -ForegroundColor Green
    Write-Host "Resultados em: results\etapa2\" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}

# Se parametro foi passado, executar diretamente
if ($Etapa -ne "") {
    switch ($Etapa) {
        "etapa1" { Run-Etapa1 -OnlySet1:$Set1Only -OnlySet2:$Set2Only }
        "etapa2" { Run-Etapa2 -OnlySet1:$Set1Only -OnlySet2:$Set2Only }
        "ambas" {
            Run-Etapa1 -OnlySet1:$Set1Only -OnlySet2:$Set2Only
            Run-Etapa2 -OnlySet1:$Set1Only -OnlySet2:$Set2Only
        }
    }
    exit 0
}

# Modo interativo
Write-Host "`n--- Teste com instancia 1I1 ---" -ForegroundColor Yellow
& $executable single "DCKP-instances\DCKP-instances-set I-100\I1 - I10\1I1"

$choice = Show-Menu

switch ($choice) {
    "1" { Run-Etapa1 -OnlySet1:$false -OnlySet2:$false }
    "2" { Run-Etapa2 -OnlySet1:$false -OnlySet2:$false }
    "3" {
        Run-Etapa1 -OnlySet1:$false -OnlySet2:$false
        Run-Etapa2 -OnlySet1:$false -OnlySet2:$false
    }
    "4" {
        Write-Host "`n--- Teste rapido concluido ---" -ForegroundColor Green
    }
    default {
        Write-Host "`nSaindo..." -ForegroundColor Yellow
    }
}
