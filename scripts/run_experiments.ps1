# Script para executar experimentos com as instâncias do DCKP
# Uso: .\run_experiments.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DCKP - Executando Experimentos Etapa 1" -ForegroundColor Cyan
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
    Write-Host "`nCriando diretório de resultados..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "results\etapa1" -Force | Out-Null
}

# Teste com uma única instância primeiro
Write-Host "`n--- Teste com instância única ---" -ForegroundColor Yellow
Write-Host "Executando: 1I1" -ForegroundColor Cyan
& $executable single "DCKP-instances\DCKP-instances-set I-100\I1 - I10\1I1"

Write-Host "`n`nDeseja executar experimentos completos? (S/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq "S" -or $response -eq "s") {
    Write-Host "`n--- Executando experimentos completos ---" -ForegroundColor Yellow
    
    # Processa conjunto I1-I10
    Write-Host "`nProcessando conjunto I1-I10..." -ForegroundColor Cyan
    & $executable batch "DCKP-instances\DCKP-instances-set I-100\I1 - I10" "results\etapa1\results_I1_I10.csv"
    
    # Processa conjunto I11-I20
    Write-Host "`nProcessando conjunto I11-I20..." -ForegroundColor Cyan
    & $executable batch "DCKP-instances\DCKP-instances-set I-100\I11 - I20" "results\etapa1\results_I11_I20.csv"
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "Experimentos concluídos!" -ForegroundColor Green
    Write-Host "Resultados salvos em: results\etapa1\" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "`nExperimentos cancelados pelo usuário." -ForegroundColor Yellow
}
