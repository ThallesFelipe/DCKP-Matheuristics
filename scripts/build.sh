#!/bin/bash
# Script para compilar o projeto DCKP no Linux/WSL

set -e

echo "========================================"
echo "Compilando DCKP"
echo "========================================"

# Ir para o diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Criar diretório de build se não existir
if [ ! -d "build" ]; then
    mkdir build
fi

cd build

echo ""
echo "Configurando CMake..."
cmake .. -DCMAKE_BUILD_TYPE=Release

if [ $? -ne 0 ]; then
    echo ""
    echo "Erro no CMake!"
    exit 1
fi

echo ""
echo "Compilando..."
make -j$(nproc)

if [ $? -ne 0 ]; then
    echo ""
    echo "Erro na compilacao!"
    exit 1
fi

cd ..

echo ""
echo "========================================"
echo "Compilacao concluida!"
echo "Executavel: build/bin/dckp_solver"
echo "========================================"
