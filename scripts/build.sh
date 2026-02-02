#!/bin/bash
# ==============================================================================
# DCKP Solver - Build Script (Linux/WSL)
# ==============================================================================
# Uso: ./scripts/build.sh [--clean] [--verbose]
# ==============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Diretórios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_DIR/build"

# Parse argumentos
CLEAN=false
VERBOSE=false

for arg in "$@"; do
    case $arg in
        --clean)
            CLEAN=true
            ;;
        --verbose)
            VERBOSE=true
            ;;
    esac
done

print_banner() {
    echo ""
    echo -e "${1}==================================================${NC}"
    echo -e "${1}$2${NC}"
    echo -e "${1}==================================================${NC}"
}

print_step() {
    echo -e "\n${YELLOW}>> $1${NC}"
}

# Banner inicial
print_banner "$CYAN" "DCKP Solver v2.0 - Build"

cd "$PROJECT_DIR"

# Limpar se solicitado
if [ "$CLEAN" = true ] && [ -d "$BUILD_DIR" ]; then
    print_step "Limpando diretorio de build..."
    rm -rf "$BUILD_DIR"
fi

# Criar diretório de build
if [ ! -d "$BUILD_DIR" ]; then
    mkdir -p "$BUILD_DIR"
fi

cd "$BUILD_DIR"

# Configurar CMake
print_step "Configurando CMake..."
CMAKE_ARGS="-DCMAKE_BUILD_TYPE=Release"
if [ "$VERBOSE" = true ]; then
    CMAKE_ARGS="$CMAKE_ARGS -DCMAKE_VERBOSE_MAKEFILE=ON"
fi
cmake .. $CMAKE_ARGS

# Compilar
print_step "Compilando..."
JOBS=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
make -j"$JOBS"

# Sucesso
print_banner "$GREEN" "Build concluido com sucesso!"
echo -e "${GREEN}Executavel: build/bin/dckp_solver${NC}"
echo ""
