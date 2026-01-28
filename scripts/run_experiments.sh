#!/bin/bash
# Script para executar experimentos com instancias do DCKP no Linux/WSL

set -e

echo "========================================"
echo "DCKP - Experimentos"
echo "========================================"

# Ir para o diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

EXECUTABLE="build/bin/dckp_solver"

if [ ! -f "$EXECUTABLE" ]; then
    echo ""
    echo "Executavel nao encontrado: $EXECUTABLE"
    echo "Execute primeiro: ./scripts/build.sh"
    exit 1
fi

# Criar diretório de resultados
mkdir -p results/etapa1

echo ""
echo "--- Teste com instancia 1I1 ---"
$EXECUTABLE single "DCKP-instances/DCKP-instances-set I-100/I1 - I10/1I1"

echo ""
echo "Executar experimentos completos? (S/N)"
read -r response

if [ "$response" = "S" ] || [ "$response" = "s" ]; then
    echo ""
    echo "--- Processando I1-I10 ---"
    $EXECUTABLE batch "DCKP-instances/DCKP-instances-set I-100/I1 - I10" "results/etapa1/results_I1_I10.csv"
    
    echo ""
    echo "--- Processando I11-I20 ---"
    $EXECUTABLE batch "DCKP-instances/DCKP-instances-set I-100/I11 - I20" "results/etapa1/results_I11_I20.csv"
    
    echo ""
    echo "========================================"
    echo "Concluido!"
    echo "========================================"
else
    echo ""
    echo "Experimentos cancelados."
fi
