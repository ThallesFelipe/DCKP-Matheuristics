#!/bin/bash
# Script para executar experimentos com instancias do DCKP no Linux/WSL
# Suporta execução separada de Etapa 1 (Construtivas), Etapa 2 (Buscas Locais) e Etapa 3 (Metaheurísticas)
#
# Uso:
#   ./scripts/run_experiments.sh              # Menu interativo
#   ./scripts/run_experiments.sh etapa1       # Executar apenas Etapa 1
#   ./scripts/run_experiments.sh etapa2       # Executar apenas Etapa 2
#   ./scripts/run_experiments.sh etapa3       # Executar apenas Etapa 3
#   ./scripts/run_experiments.sh todas        # Executar todas as etapas
#   ./scripts/run_experiments.sh --set1       # Apenas Set I
#   ./scripts/run_experiments.sh --set2       # Apenas Set II
#   ./scripts/run_experiments.sh etapa3 --set1  # Etapa 3 apenas Set I

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}DCKP - Experimentos${NC}"
echo -e "${CYAN}========================================${NC}"

# Ir para o diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

EXECUTABLE="build/bin/dckp_solver"

if [ ! -f "$EXECUTABLE" ]; then
    echo ""
    echo -e "${RED}Executavel nao encontrado: $EXECUTABLE${NC}"
    echo -e "${YELLOW}Execute primeiro: ./scripts/build.sh${NC}"
    exit 1
fi

# Criar diretórios de resultados
mkdir -p results/etapa1
mkdir -p results/etapa2
mkdir -p results/etapa3

# Parsear argumentos
ETAPA=""
SET1_ONLY=false
SET2_ONLY=false

for arg in "$@"; do
    case $arg in
        etapa1|etapa2|etapa3|todas|ambas)
            ETAPA="$arg"
            ;;
        --set1)
            SET1_ONLY=true
            ;;
        --set2)
            SET2_ONLY=true
            ;;
    esac
done

# Função para executar Etapa 1
run_etapa1() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}ETAPA 1 - Heuristicas Construtivas${NC}"
    echo -e "${CYAN}========================================${NC}"
    
    if [ "$SET2_ONLY" = false ]; then
        echo ""
        echo -e "${YELLOW}--- Processando I1-I10 (Etapa 1) ---${NC}"
        $EXECUTABLE batch-etapa1 "DCKP-instances/DCKP-instances-set I-100/I1 - I10" "results/etapa1/results_I1_I10.csv"
        
        echo ""
        echo -e "${YELLOW}--- Processando I11-I20 (Etapa 1) ---${NC}"
        $EXECUTABLE batch-etapa1 "DCKP-instances/DCKP-instances-set I-100/I11 - I20" "results/etapa1/results_I11_I20.csv"
    fi
    
    if [ "$SET1_ONLY" = false ]; then
        echo ""
        echo -e "${YELLOW}--- Set II (Etapa 1) requer execucao via Makefile ---${NC}"
        echo -e "${YELLOW}Use: make run-etapa1-set2${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}ETAPA 1 Concluida!${NC}"
    echo -e "${GREEN}Resultados em: results/etapa1/${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# Função para executar Etapa 2
run_etapa2() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}ETAPA 2 - Buscas Locais${NC}"
    echo -e "${CYAN}========================================${NC}"
    
    if [ "$SET2_ONLY" = false ]; then
        echo ""
        echo -e "${YELLOW}--- Processando I1-I10 (Etapa 2) ---${NC}"
        $EXECUTABLE batch-etapa2 "DCKP-instances/DCKP-instances-set I-100/I1 - I10" "results/etapa2/results_I1_I10.csv"
        
        echo ""
        echo -e "${YELLOW}--- Processando I11-I20 (Etapa 2) ---${NC}"
        $EXECUTABLE batch-etapa2 "DCKP-instances/DCKP-instances-set I-100/I11 - I20" "results/etapa2/results_I11_I20.csv"
    fi
    
    if [ "$SET1_ONLY" = false ]; then
        echo ""
        echo -e "${YELLOW}--- Set II (Etapa 2) requer execucao via Makefile ---${NC}"
        echo -e "${YELLOW}Use: make run-etapa2-set2${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}ETAPA 2 Concluida!${NC}"
    echo -e "${GREEN}Resultados em: results/etapa2/${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# Função para executar Etapa 3 (apenas Set I)
run_etapa3() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}ETAPA 3 - Metaheuristicas (Set I apenas)${NC}"
    echo -e "${CYAN}========================================${NC}"
    
    echo ""
    echo -e "${YELLOW}--- Processando I1-I10 (Etapa 3) ---${NC}"
    $EXECUTABLE batch-etapa3 "DCKP-instances/DCKP-instances-set I-100/I1 - I10" "results/etapa3/results_I1_I10.csv"
    
    echo ""
    echo -e "${YELLOW}--- Processando I11-I20 (Etapa 3) ---${NC}"
    $EXECUTABLE batch-etapa3 "DCKP-instances/DCKP-instances-set I-100/I11 - I20" "results/etapa3/results_I11_I20.csv"
    
    echo ""
    echo -e "${YELLOW}Nota: Set II nao executado na Etapa 3 (tempo proibitivo).${NC}"
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}ETAPA 3 Concluida! (Set I - 100 instancias)${NC}"
    echo -e "${GREEN}Resultados em: results/etapa3/${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# Função para mostrar menu
show_menu() {
    echo ""
    echo -e "${YELLOW}Escolha o modo de execucao:${NC}"
    echo "  1) Etapa 1 - Heuristicas Construtivas (Greedy + GRASP)"
    echo "  2) Etapa 2 - Buscas Locais (GRASP + HC + VND)"
    echo "  3) Etapa 3 - Metaheuristicas (GRASP + ILS + VNS)"
    echo "  4) Todas as Etapas"
    echo "  5) Teste rapido (1 instancia)"
    echo "  0) Sair"
    echo ""
    read -rp "Opcao: " choice
    echo "$choice"
}

# Se argumento foi passado, executar diretamente
if [ -n "$ETAPA" ]; then
    case $ETAPA in
        etapa1)
            run_etapa1
            ;;
        etapa2)
            run_etapa2
            ;;
        etapa3)
            run_etapa3
            ;;
        todas|ambas)
            run_etapa1
            run_etapa2
            run_etapa3
            ;;
    esac
    exit 0
fi

# Modo interativo
echo ""
echo -e "${YELLOW}--- Teste com instancia 1I1 ---${NC}"
$EXECUTABLE single "DCKP-instances/DCKP-instances-set I-100/I1 - I10/1I1"

choice=$(show_menu)

case $choice in
    1)
        run_etapa1
        ;;
    2)
        run_etapa2
        ;;
    3)
        run_etapa3
        ;;
    4)
        run_etapa1
        run_etapa2
        run_etapa3
        ;;
    5)
        echo ""
        echo -e "${GREEN}--- Teste rapido concluido ---${NC}"
        ;;
    *)
        echo ""
        echo -e "${YELLOW}Saindo...${NC}"
        ;;
esac
