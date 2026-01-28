#!/bin/bash
# Script para executar a análise de resultados no Linux/WSL

set -e

echo "========================================"
echo "DCKP - Analise de Resultados"
echo "========================================"

# Ir para o diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python3 nao encontrado!"
    echo "Instale com: sudo apt install python3 python3-pip"
    exit 1
fi

# Verificar/instalar dependências
echo ""
echo "Verificando dependencias Python..."
# Forçar upgrade para versões mais recentes
pip3 install --upgrade --quiet pandas matplotlib seaborn numpy scipy 2>/dev/null || {
    echo "Instalando dependencias..."
    pip3 install --upgrade pandas matplotlib seaborn numpy scipy
}

# Executar análise
echo ""
echo "Executando analise..."
python3 scripts/analyze_results.py "$@"

echo ""
echo "========================================"
echo "Analise concluida!"
echo "========================================"
