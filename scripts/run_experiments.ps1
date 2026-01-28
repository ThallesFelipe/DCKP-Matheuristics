# Script para executar experimentos com instancias do DCKP

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DCKP - Experimentos" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$executable = "build\bin\dckp_solver.exe"
if (!(Test-Path $executable)) {
    Write-Host "`nExecutavel nao encontrado: $executable" -ForegroundColor Red
    Write-Host "Execute primeiro: .\scripts\build.ps1" -ForegroundColor Yellow
    exit 1
}

if (!(Test-Path "results\etapa1")) {
    New-Item -ItemType Directory -Path "results\etapa1" -Force | Out-Null
}

Write-Host "`n--- Teste com instancia 1I1 ---" -ForegroundColor Yellow
& $executable single "DCKP-instances\DCKP-instances-set I-100\I1 - I10\1I1"

Write-Host "`n`nExecutar experimentos completos? (S/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq "S" -or $response -eq "s") {
    Write-Host "`n--- Processando I1-I10 ---" -ForegroundColor Yellow
    & $executable batch "DCKP-instances\DCKP-instances-set I-100\I1 - I10" "results\etapa1\results_I1_I10.csv"
    
    Write-Host "`n--- Processando I11-I20 ---" -ForegroundColor Yellow
    & $executable batch "DCKP-instances\DCKP-instances-set I-100\I11 - I20" "results\etapa1\results_I11_I20.csv"
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "Concluido!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "`nExperimentos cancelados." -ForegroundColor Yellow
}
