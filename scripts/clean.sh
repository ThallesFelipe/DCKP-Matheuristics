#!/bin/bash
# Script para limpar arquivos de build e resultados no Linux/WSL

# Ir para o diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

show_usage() {
    echo "========================================"
    echo "Limpeza do Projeto DCKP"
    echo "========================================"
    echo ""
    echo "Uso:"
    echo "  ./scripts/clean.sh --build      # Limpa build"
    echo "  ./scripts/clean.sh --results    # Limpa resultados"
    echo "  ./scripts/clean.sh --all        # Limpa tudo"
}

clean_build() {
    echo ""
    echo "Limpando build..."
    if [ -d "build" ]; then
        rm -rf build
        echo "  Build removido"
    else
        echo "  Nenhum diretorio build encontrado"
    fi
}

clean_results() {
    echo ""
    echo "Limpando resultados..."
    if [ -d "results/etapa1" ]; then
        rm -f results/etapa1/*.csv 2>/dev/null || true
        rm -rf results/etapa1/analysis 2>/dev/null || true
        echo "  Resultados removidos"
    else
        echo "  Nenhum diretorio de resultados encontrado"
    fi
}

echo "========================================"
echo "Limpeza do Projeto DCKP"
echo "========================================"

case "$1" in
    --all|-a)
        clean_build
        clean_results
        ;;
    --build|-b)
        clean_build
        ;;
    --results|-r)
        clean_results
        ;;
    *)
        show_usage
        exit 0
        ;;
esac

echo ""
echo "========================================"
echo "Limpeza concluida!"
echo "========================================"
