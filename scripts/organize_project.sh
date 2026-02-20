#!/bin/bash
# Script de organização e limpeza segura do projeto DCKP (Linux/WSL)

set -e

CLEAN_BUILD=false
CLEAN_ANALYSIS=false
CLEAN_RESULTS=false
DRY_RUN=false

for arg in "$@"; do
    case "$arg" in
        --clean-build) CLEAN_BUILD=true ;;
        --clean-analysis) CLEAN_ANALYSIS=true ;;
        --clean-results) CLEAN_RESULTS=true ;;
        --dry-run) DRY_RUN=true ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

step() {
    echo ""
    echo ">> $1"
}

remove_if_exists() {
    target="$1"
    if [ -e "$target" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "[dry-run] remover: $target"
        else
            rm -rf "$target"
            echo "removido: $target"
        fi
    fi
}

echo "========================================"
echo "DCKP - Organizacao do Projeto"
echo "========================================"

step "Limpando temporarios e caches"
find . \
    \( -path "./.git" -o -path "./.venv" -o -path "./.venv_wsl" -o -path "./venv" -o -path "./build" \) -prune -o \
    -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" \) -print0 | \
while IFS= read -r -d '' path; do
    remove_if_exists "$path"
done

find . \
    \( -path "./.git" -o -path "./.venv" -o -path "./.venv_wsl" -o -path "./venv" -o -path "./build" \) -prune -o \
    -type f \( -name "*.tmp" -o -name "*.log" -o -name ".DS_Store" -o -name "Thumbs.db" \) -print0 | \
while IFS= read -r -d '' path; do
    if [ "$DRY_RUN" = true ]; then
        echo "[dry-run] remover: $path"
    else
        rm -f "$path"
        echo "removido: $path"
    fi
done

if [ "$CLEAN_BUILD" = true ]; then
    step "Limpando diretorio de build"
    remove_if_exists "build"
fi

if [ "$CLEAN_ANALYSIS" = true ]; then
    step "Limpando apenas resultados de analise"
    remove_if_exists "results/analysis"
fi

if [ "$CLEAN_RESULTS" = true ]; then
    step "Limpando resultados experimentais"
    remove_if_exists "results/etapa1"
    remove_if_exists "results/etapa2"
    remove_if_exists "results/etapa3"
fi

step "Garantindo estrutura minima de diretorios"
for dir in \
    "results/etapa1" \
    "results/etapa2" \
    "results/etapa3" \
    "results/analysis/etapa1" \
    "results/analysis/etapa2" \
    "results/analysis/etapa3"; do
    if [ ! -d "$dir" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "[dry-run] criar: $dir"
        else
            mkdir -p "$dir"
            echo "criado: $dir"
        fi
    fi
done

echo ""
echo "========================================"
echo "Organizacao concluida"
echo "========================================"
