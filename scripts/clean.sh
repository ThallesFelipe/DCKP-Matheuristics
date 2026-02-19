#!/bin/bash
# Script para limpar arquivos de build e resultados no Linux/WSL
# Suporta limpeza separada de Etapa 1, Etapa 2 e Etapa 3

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
    echo "  ./scripts/clean.sh --results    # Limpa todos resultados (etapa1 + etapa2 + etapa3)"
    echo "  ./scripts/clean.sh --etapa1     # Limpa apenas resultados da Etapa 1"
    echo "  ./scripts/clean.sh --etapa2     # Limpa apenas resultados da Etapa 2"
    echo "  ./scripts/clean.sh --etapa3     # Limpa apenas resultados da Etapa 3"
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

clean_results_etapa1() {
    echo ""
    echo "Limpando resultados da Etapa 1..."
    if [ -d "results/etapa1" ]; then
        rm -f results/etapa1/*.csv 2>/dev/null || true
        rm -rf results/etapa1/analysis 2>/dev/null || true
        echo "  Resultados Etapa 1 removidos"
    else
        echo "  Nenhum diretorio results/etapa1 encontrado"
    fi
}

clean_results_etapa2() {
    echo ""
    echo "Limpando resultados da Etapa 2..."
    if [ -d "results/etapa2" ]; then
        rm -f results/etapa2/*.csv 2>/dev/null || true
        rm -rf results/etapa2/analysis 2>/dev/null || true
        echo "  Resultados Etapa 2 removidos"
    else
        echo "  Nenhum diretorio results/etapa2 encontrado"
    fi
}

clean_results_etapa3() {
    echo ""
    echo "Limpando resultados da Etapa 3..."
    if [ -d "results/etapa3" ]; then
        rm -f results/etapa3/*.csv 2>/dev/null || true
        rm -rf results/etapa3/analysis 2>/dev/null || true
        echo "  Resultados Etapa 3 removidos"
    else
        echo "  Nenhum diretorio results/etapa3 encontrado"
    fi
}

clean_results_all() {
    clean_results_etapa1
    clean_results_etapa2
    clean_results_etapa3
}

echo "========================================"
echo "Limpeza do Projeto DCKP"
echo "========================================"

case "$1" in
    --all|-a)
        clean_build
        clean_results_all
        ;;
    --build|-b)
        clean_build
        ;;
    --results|-r)
        clean_results_all
        ;;
    --etapa1|-1)
        clean_results_etapa1
        ;;
    --etapa2|-2)
        clean_results_etapa2
        ;;
    --etapa3|-3)
        clean_results_etapa3
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
