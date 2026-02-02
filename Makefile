# Makefile para o projeto DCKP
# Para uso no Linux/WSL

.PHONY: all build run test test-etapa2 analyze clean help menu \
        run-set1 run-set2 run-all \
        run-I1-I10 run-I11-I20 \
        run-C1 run-C3 run-C10 run-C15 \
        run-R1 run-R3 run-R10 run-R15 \
        run-all-C run-all-R \
        run-etapa1 run-etapa1-set1 run-etapa1-set2 \
        run-etapa2 run-etapa2-set1 run-etapa2-set2 \
        run-all-etapas run-all-etapas-set1 run-all-etapas-set2 \
        run-I1-I10-etapa1 run-I11-I20-etapa1 \
        run-I1-I10-etapa2 run-I11-I20-etapa2 \
        run-C1-etapa1 run-C1-etapa2 run-R1-etapa1 run-R1-etapa2 \
        single compare

# Configurações
BUILD_DIR = build
BIN_DIR = $(BUILD_DIR)/bin
EXECUTABLE = $(BIN_DIR)/dckp_solver
RESULTS_DIR_ETAPA1 = results/etapa1
RESULTS_DIR_ETAPA2 = results/etapa2

# Diretórios de instâncias - Set I (100 instâncias)
SET1_DIR = DCKP-instances/DCKP-instances-set I-100
INSTANCES_I1_I10 = $(SET1_DIR)/I1 - I10
INSTANCES_I11_I20 = $(SET1_DIR)/I11 - I20

# Diretórios de instâncias - Set II (6240 instâncias)
SET2_DIR = DCKP-instances/DCKP-instances-set II-6240
INSTANCES_C1 = $(SET2_DIR)/C1
INSTANCES_C3 = $(SET2_DIR)/C3
INSTANCES_C10 = $(SET2_DIR)/C10
INSTANCES_C15 = $(SET2_DIR)/C15
INSTANCES_R1 = $(SET2_DIR)/R1
INSTANCES_R3 = $(SET2_DIR)/R3
INSTANCES_R10 = $(SET2_DIR)/R10
INSTANCES_R15 = $(SET2_DIR)/R15

# Cores para output
GREEN = \033[0;32m
YELLOW = \033[0;33m
CYAN = \033[0;36m
RED = \033[0;31m
BOLD = \033[1m
NC = \033[0m # No Color

# Comandos
all: build

# ============================================================
# MENU INTERATIVO
# ============================================================
menu:
	@echo ""
	@echo "$(BOLD)$(CYAN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BOLD)$(CYAN)║           DCKP SOLVER - MENU DE EXPERIMENTOS                   ║$(NC)"
	@echo "$(BOLD)$(CYAN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BOLD)$(YELLOW)┌─────────────────────────────────────────────────────────────────┐$(NC)"
	@echo "$(BOLD)$(YELLOW)│  EXECUÇÃO POR ETAPAS                                            │$(NC)"
	@echo "$(BOLD)$(YELLOW)└─────────────────────────────────────────────────────────────────┘$(NC)"
	@echo "  $(CYAN)[Etapa 1 - Heurísticas Construtivas (Greedy + GRASP)]$(NC)"
	@echo "  $(GREEN)make run-etapa1$(NC)          → Executar Etapa 1 em TODOS os sets"
	@echo "  $(GREEN)make run-etapa1-set1$(NC)     → Executar Etapa 1 no Set I (100 inst.)"
	@echo "  $(GREEN)make run-etapa1-set2$(NC)     → Executar Etapa 1 no Set II (6240 inst.)"
	@echo ""
	@echo "  $(CYAN)[Etapa 2 - Buscas Locais (GRASP + Hill Climbing + VND)]$(NC)"
	@echo "  $(GREEN)make run-etapa2$(NC)          → Executar Etapa 2 em TODOS os sets"
	@echo "  $(GREEN)make run-etapa2-set1$(NC)     → Executar Etapa 2 no Set I"
	@echo "  $(GREEN)make run-etapa2-set2$(NC)     → Executar Etapa 2 no Set II"
	@echo ""
	@echo "  $(CYAN)[Ambas Etapas]$(NC)"
	@echo "  $(GREEN)make run-all-etapas$(NC)      → Executar Etapa 1 + Etapa 2 (todos os sets)"
	@echo "  $(GREEN)make run-all-etapas-set1$(NC) → Executar ambas etapas no Set I"
	@echo "  $(GREEN)make run-all-etapas-set2$(NC) → Executar ambas etapas no Set II"
	@echo ""
	@echo "$(BOLD)$(YELLOW)┌─────────────────────────────────────────────────────────────────┐$(NC)"
	@echo "$(BOLD)$(YELLOW)│  SET I - Instâncias Pequenas (100 instâncias)                   │$(NC)"
	@echo "$(BOLD)$(YELLOW)└─────────────────────────────────────────────────────────────────┘$(NC)"
	@echo "  $(GREEN)make run-I1-I10$(NC)          → I1-I10 (ambas etapas, compat.)"
	@echo "  $(GREEN)make run-I1-I10-etapa1$(NC)   → I1-I10 apenas Etapa 1"
	@echo "  $(GREEN)make run-I1-I10-etapa2$(NC)   → I1-I10 apenas Etapa 2"
	@echo "  $(GREEN)make run-I11-I20$(NC)         → I11-I20 (ambas etapas)"
	@echo "  $(GREEN)make run-I11-I20-etapa1$(NC)  → I11-I20 apenas Etapa 1"
	@echo "  $(GREEN)make run-I11-I20-etapa2$(NC)  → I11-I20 apenas Etapa 2"
	@echo "  $(GREEN)make run-set1$(NC)            → TODO o Set I (ambas etapas)"
	@echo ""
	@echo "$(BOLD)$(YELLOW)┌─────────────────────────────────────────────────────────────────┐$(NC)"
	@echo "$(BOLD)$(YELLOW)│  SET II - Instâncias Grandes (6240 instâncias)                  │$(NC)"
	@echo "$(BOLD)$(YELLOW)└─────────────────────────────────────────────────────────────────┘$(NC)"
	@echo "  $(CYAN)[Correlacionadas - C]$(NC)"
	@echo "  $(GREEN)make run-C1$(NC)              → C1 (ambas etapas)"
	@echo "  $(GREEN)make run-C1-etapa1$(NC)       → C1 apenas Etapa 1"
	@echo "  $(GREEN)make run-C1-etapa2$(NC)       → C1 apenas Etapa 2"
	@echo "  $(GREEN)make run-C3$(NC)              → Densidade de conflito 3%"
	@echo "  $(GREEN)make run-C10$(NC)             → Densidade de conflito 10%"
	@echo "  $(GREEN)make run-C15$(NC)             → Densidade de conflito 15%"
	@echo "  $(GREEN)make run-all-C$(NC)           → Todas as instâncias C"
	@echo ""
	@echo "  $(CYAN)[Randômicas - R]$(NC)"
	@echo "  $(GREEN)make run-R1$(NC)              → R1 (ambas etapas)"
	@echo "  $(GREEN)make run-R1-etapa1$(NC)       → R1 apenas Etapa 1"
	@echo "  $(GREEN)make run-R1-etapa2$(NC)       → R1 apenas Etapa 2"
	@echo "  $(GREEN)make run-R3$(NC)  $(GREEN)make run-R10$(NC)  $(GREEN)make run-R15$(NC)"
	@echo "  $(GREEN)make run-all-R$(NC)           → Todas as instâncias R"
	@echo ""
	@echo "  $(GREEN)make run-set2$(NC)            → TODO o Set II (ambas etapas)"
	@echo ""
	@echo "$(BOLD)$(YELLOW)┌─────────────────────────────────────────────────────────────────┐$(NC)"
	@echo "$(BOLD)$(YELLOW)│  EXECUÇÃO COMPLETA                                              │$(NC)"
	@echo "$(BOLD)$(YELLOW)└─────────────────────────────────────────────────────────────────┘$(NC)"
	@echo "  $(GREEN)make run-all$(NC)             → Executar TODOS os sets (ambas etapas)"
	@echo ""
	@echo "$(BOLD)$(YELLOW)┌─────────────────────────────────────────────────────────────────┐$(NC)"
	@echo "$(BOLD)$(YELLOW)│  TESTES INDIVIDUAIS E UTILITÁRIOS                               │$(NC)"
	@echo "$(BOLD)$(YELLOW)└─────────────────────────────────────────────────────────────────┘$(NC)"
	@echo "  $(GREEN)make single FILE=<caminho>$(NC)"
	@echo "      Exemplo: make single FILE=\"DCKP-instances/DCKP-instances-set I-100/I1 - I10/1I1\""
	@echo ""
	@echo "  $(GREEN)make build$(NC)               → Compilar o projeto"
	@echo "  $(GREEN)make test$(NC)                → Teste rápido Etapa 1+2 (1 instância)"
	@echo "  $(GREEN)make test-etapa2$(NC)         → Teste rápido apenas Etapa 2"
	@echo "  $(GREEN)make analyze$(NC)             → Analisar resultados"
	@echo "  $(GREEN)make clean$(NC)               → Limpar build e resultados"
	@echo "  $(GREEN)make help$(NC)                → Este menu"
	@echo ""
	@echo "$(BOLD)$(YELLOW)┌─────────────────────────────────────────────────────────────────┐$(NC)"
	@echo "$(BOLD)$(YELLOW)│  DIRETÓRIOS DE RESULTADOS                                       │$(NC)"
	@echo "$(BOLD)$(YELLOW)└─────────────────────────────────────────────────────────────────┘$(NC)"
	@echo "  Etapa 1: $(CYAN)results/etapa1/$(NC)"
	@echo "  Etapa 2: $(CYAN)results/etapa2/$(NC)"
	@echo ""

help: menu

# ============================================================
# COMPILAÇÃO
# ============================================================
build:
	@echo "$(CYAN)=== Compilando DCKP ===$(NC)"
	@mkdir -p $(BUILD_DIR)
	@cd $(BUILD_DIR) && cmake .. -DCMAKE_BUILD_TYPE=Release && make -j$$(nproc)
	@echo "$(GREEN)=== Compilação concluída ===$(NC)"
	@echo "Executável: $(EXECUTABLE)"

$(EXECUTABLE): build

# ============================================================
# ETAPA 1 - HEURÍSTICAS CONSTRUTIVAS
# ============================================================
run-I1-I10-etapa1: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 1: I1-I10 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch-etapa1 "$(INSTANCES_I1_I10)" "$(RESULTS_DIR_ETAPA1)/results_I1_I10.csv"
	@echo "$(GREEN)=== Concluído: I1-I10 (Etapa 1) ===$(NC)"

run-I11-I20-etapa1: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 1: I11-I20 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch-etapa1 "$(INSTANCES_I11_I20)" "$(RESULTS_DIR_ETAPA1)/results_I11_I20.csv"
	@echo "$(GREEN)=== Concluído: I11-I20 (Etapa 1) ===$(NC)"

run-etapa1-set1: run-I1-I10-etapa1 run-I11-I20-etapa1
	@echo "$(GREEN)=== Set I (Etapa 1) completo! ===$(NC)"

run-C1-etapa1: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 1: C1 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch-etapa1 "$(INSTANCES_C1)" "$(RESULTS_DIR_ETAPA1)/results_C1.csv"
	@echo "$(GREEN)=== Concluído: C1 (Etapa 1) ===$(NC)"

run-C3-etapa1: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 1: C3 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch-etapa1 "$(INSTANCES_C3)" "$(RESULTS_DIR_ETAPA1)/results_C3.csv"
	@echo "$(GREEN)=== Concluído: C3 (Etapa 1) ===$(NC)"

run-C10-etapa1: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 1: C10 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch-etapa1 "$(INSTANCES_C10)" "$(RESULTS_DIR_ETAPA1)/results_C10.csv"
	@echo "$(GREEN)=== Concluído: C10 (Etapa 1) ===$(NC)"

run-C15-etapa1: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 1: C15 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch-etapa1 "$(INSTANCES_C15)" "$(RESULTS_DIR_ETAPA1)/results_C15.csv"
	@echo "$(GREEN)=== Concluído: C15 (Etapa 1) ===$(NC)"

run-R1-etapa1: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 1: R1 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch-etapa1 "$(INSTANCES_R1)" "$(RESULTS_DIR_ETAPA1)/results_R1.csv"
	@echo "$(GREEN)=== Concluído: R1 (Etapa 1) ===$(NC)"

run-R3-etapa1: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 1: R3 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch-etapa1 "$(INSTANCES_R3)" "$(RESULTS_DIR_ETAPA1)/results_R3.csv"
	@echo "$(GREEN)=== Concluído: R3 (Etapa 1) ===$(NC)"

run-R10-etapa1: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 1: R10 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch-etapa1 "$(INSTANCES_R10)" "$(RESULTS_DIR_ETAPA1)/results_R10.csv"
	@echo "$(GREEN)=== Concluído: R10 (Etapa 1) ===$(NC)"

run-R15-etapa1: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 1: R15 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch-etapa1 "$(INSTANCES_R15)" "$(RESULTS_DIR_ETAPA1)/results_R15.csv"
	@echo "$(GREEN)=== Concluído: R15 (Etapa 1) ===$(NC)"

run-all-C-etapa1: run-C1-etapa1 run-C3-etapa1 run-C10-etapa1 run-C15-etapa1
	@echo "$(GREEN)=== Todas as instâncias C (Etapa 1) concluídas! ===$(NC)"

run-all-R-etapa1: run-R1-etapa1 run-R3-etapa1 run-R10-etapa1 run-R15-etapa1
	@echo "$(GREEN)=== Todas as instâncias R (Etapa 1) concluídas! ===$(NC)"

run-etapa1-set2: run-all-C-etapa1 run-all-R-etapa1
	@echo "$(GREEN)=== Set II (Etapa 1) completo! ===$(NC)"

run-etapa1: run-etapa1-set1 run-etapa1-set2
	@echo "$(GREEN)=== ETAPA 1 completa (todos os sets)! ===$(NC)"

# ============================================================
# ETAPA 2 - BUSCAS LOCAIS
# ============================================================
run-I1-I10-etapa2: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 2: I1-I10 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA2)
	@./$(EXECUTABLE) batch-etapa2 "$(INSTANCES_I1_I10)" "$(RESULTS_DIR_ETAPA2)/results_I1_I10.csv"
	@echo "$(GREEN)=== Concluído: I1-I10 (Etapa 2) ===$(NC)"

run-I11-I20-etapa2: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 2: I11-I20 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA2)
	@./$(EXECUTABLE) batch-etapa2 "$(INSTANCES_I11_I20)" "$(RESULTS_DIR_ETAPA2)/results_I11_I20.csv"
	@echo "$(GREEN)=== Concluído: I11-I20 (Etapa 2) ===$(NC)"

run-etapa2-set1: run-I1-I10-etapa2 run-I11-I20-etapa2
	@echo "$(GREEN)=== Set I (Etapa 2) completo! ===$(NC)"

run-C1-etapa2: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 2: C1 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA2)
	@./$(EXECUTABLE) batch-etapa2 "$(INSTANCES_C1)" "$(RESULTS_DIR_ETAPA2)/results_C1.csv"
	@echo "$(GREEN)=== Concluído: C1 (Etapa 2) ===$(NC)"

run-C3-etapa2: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 2: C3 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA2)
	@./$(EXECUTABLE) batch-etapa2 "$(INSTANCES_C3)" "$(RESULTS_DIR_ETAPA2)/results_C3.csv"
	@echo "$(GREEN)=== Concluído: C3 (Etapa 2) ===$(NC)"

run-C10-etapa2: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 2: C10 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA2)
	@./$(EXECUTABLE) batch-etapa2 "$(INSTANCES_C10)" "$(RESULTS_DIR_ETAPA2)/results_C10.csv"
	@echo "$(GREEN)=== Concluído: C10 (Etapa 2) ===$(NC)"

run-C15-etapa2: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 2: C15 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA2)
	@./$(EXECUTABLE) batch-etapa2 "$(INSTANCES_C15)" "$(RESULTS_DIR_ETAPA2)/results_C15.csv"
	@echo "$(GREEN)=== Concluído: C15 (Etapa 2) ===$(NC)"

run-R1-etapa2: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 2: R1 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA2)
	@./$(EXECUTABLE) batch-etapa2 "$(INSTANCES_R1)" "$(RESULTS_DIR_ETAPA2)/results_R1.csv"
	@echo "$(GREEN)=== Concluído: R1 (Etapa 2) ===$(NC)"

run-R3-etapa2: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 2: R3 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA2)
	@./$(EXECUTABLE) batch-etapa2 "$(INSTANCES_R3)" "$(RESULTS_DIR_ETAPA2)/results_R3.csv"
	@echo "$(GREEN)=== Concluído: R3 (Etapa 2) ===$(NC)"

run-R10-etapa2: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 2: R10 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA2)
	@./$(EXECUTABLE) batch-etapa2 "$(INSTANCES_R10)" "$(RESULTS_DIR_ETAPA2)/results_R10.csv"
	@echo "$(GREEN)=== Concluído: R10 (Etapa 2) ===$(NC)"

run-R15-etapa2: $(EXECUTABLE)
	@echo "$(CYAN)=== ETAPA 2: R15 ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA2)
	@./$(EXECUTABLE) batch-etapa2 "$(INSTANCES_R15)" "$(RESULTS_DIR_ETAPA2)/results_R15.csv"
	@echo "$(GREEN)=== Concluído: R15 (Etapa 2) ===$(NC)"

run-all-C-etapa2: run-C1-etapa2 run-C3-etapa2 run-C10-etapa2 run-C15-etapa2
	@echo "$(GREEN)=== Todas as instâncias C (Etapa 2) concluídas! ===$(NC)"

run-all-R-etapa2: run-R1-etapa2 run-R3-etapa2 run-R10-etapa2 run-R15-etapa2
	@echo "$(GREEN)=== Todas as instâncias R (Etapa 2) concluídas! ===$(NC)"

run-etapa2-set2: run-all-C-etapa2 run-all-R-etapa2
	@echo "$(GREEN)=== Set II (Etapa 2) completo! ===$(NC)"

run-etapa2: run-etapa2-set1 run-etapa2-set2
	@echo "$(GREEN)=== ETAPA 2 completa (todos os sets)! ===$(NC)"

# ============================================================
# AMBAS ETAPAS (SEQUENCIAL)
# ============================================================
run-all-etapas-set1: run-etapa1-set1 run-etapa2-set1
	@echo "$(GREEN)=== Set I (Etapa 1 + Etapa 2) completo! ===$(NC)"

run-all-etapas-set2: run-etapa1-set2 run-etapa2-set2
	@echo "$(GREEN)=== Set II (Etapa 1 + Etapa 2) completo! ===$(NC)"

run-all-etapas: run-etapa1 run-etapa2
	@echo "$(GREEN)=== Todas as etapas concluídas (todos os sets)! ===$(NC)"

# ============================================================
# COMPATIBILIDADE - EXECUÇÃO COMBINADA (MODO LEGADO)
# ============================================================
run-I1-I10: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando I1-I10 (ambas etapas) ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch "$(INSTANCES_I1_I10)" "$(RESULTS_DIR_ETAPA1)/results_I1_I10.csv"
	@echo "$(GREEN)=== Concluído: I1-I10 ===$(NC)"

run-I11-I20: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando I11-I20 (ambas etapas) ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch "$(INSTANCES_I11_I20)" "$(RESULTS_DIR_ETAPA1)/results_I11_I20.csv"
	@echo "$(GREEN)=== Concluído: I11-I20 ===$(NC)"

run-set1: run-I1-I10 run-I11-I20
	@echo "$(GREEN)=== Set I completo! ===$(NC)"

# ============================================================
# SET II - INSTÂNCIAS CORRELACIONADAS (C) - MODO LEGADO
# ============================================================
run-C1: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando C1 (correlacionadas, 1% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch "$(INSTANCES_C1)" "$(RESULTS_DIR_ETAPA1)/results_C1.csv"
	@echo "$(GREEN)=== Concluído: C1 ===$(NC)"

run-C3: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando C3 (correlacionadas, 3% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch "$(INSTANCES_C3)" "$(RESULTS_DIR_ETAPA1)/results_C3.csv"
	@echo "$(GREEN)=== Concluído: C3 ===$(NC)"

run-C10: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando C10 (correlacionadas, 10% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch "$(INSTANCES_C10)" "$(RESULTS_DIR_ETAPA1)/results_C10.csv"
	@echo "$(GREEN)=== Concluído: C10 ===$(NC)"

run-C15: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando C15 (correlacionadas, 15% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch "$(INSTANCES_C15)" "$(RESULTS_DIR_ETAPA1)/results_C15.csv"
	@echo "$(GREEN)=== Concluído: C15 ===$(NC)"

run-all-C: run-C1 run-C3 run-C10 run-C15
	@echo "$(GREEN)=== Todas as instâncias C concluídas! ===$(NC)"

# ============================================================
# SET II - INSTÂNCIAS RANDÔMICAS (R) - MODO LEGADO
# ============================================================
run-R1: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando R1 (randômicas, 1% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch "$(INSTANCES_R1)" "$(RESULTS_DIR_ETAPA1)/results_R1.csv"
	@echo "$(GREEN)=== Concluído: R1 ===$(NC)"

run-R3: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando R3 (randômicas, 3% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch "$(INSTANCES_R3)" "$(RESULTS_DIR_ETAPA1)/results_R3.csv"
	@echo "$(GREEN)=== Concluído: R3 ===$(NC)"

run-R10: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando R10 (randômicas, 10% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch "$(INSTANCES_R10)" "$(RESULTS_DIR_ETAPA1)/results_R10.csv"
	@echo "$(GREEN)=== Concluído: R10 ===$(NC)"

run-R15: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando R15 (randômicas, 15% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA1)
	@./$(EXECUTABLE) batch "$(INSTANCES_R15)" "$(RESULTS_DIR_ETAPA1)/results_R15.csv"
	@echo "$(GREEN)=== Concluído: R15 ===$(NC)"

run-all-R: run-R1 run-R3 run-R10 run-R15
	@echo "$(GREEN)=== Todas as instâncias R concluídas! ===$(NC)"

# ============================================================
# EXECUÇÕES COMBINADAS
# ============================================================
run-set2: run-all-C run-all-R
	@echo "$(GREEN)=== Set II completo! ===$(NC)"

run-all: run-set1 run-set2
	@echo "$(GREEN)=== TODOS os experimentos concluídos! ===$(NC)"

# Alias para compatibilidade
run: run-set1

# ============================================================
# TESTES INDIVIDUAIS E COMPARAÇÕES
# ============================================================
test: $(EXECUTABLE)
	@echo "$(CYAN)=== Teste Rápido (Etapa 1 + Etapa 2) ===$(NC)"
	@./$(EXECUTABLE) single "$(INSTANCES_I1_I10)/1I1"

test-etapa2: $(EXECUTABLE)
	@echo "$(CYAN)=== Teste Rápido (Apenas Etapa 2 - Buscas Locais) ===$(NC)"
	@mkdir -p $(RESULTS_DIR_ETAPA2)
	@./$(EXECUTABLE) batch-etapa2 "$(INSTANCES_I1_I10)/1I1" "$(RESULTS_DIR_ETAPA2)/test_etapa2.csv"
	@echo "$(GREEN)=== Teste Etapa 2 concluído! ===$(NC)"

single: $(EXECUTABLE)
ifndef FILE
	@echo "$(RED)Erro: Especifique o arquivo com FILE=<caminho>$(NC)"
	@echo "Exemplo: make single FILE=\"DCKP-instances/DCKP-instances-set I-100/I1 - I10/1I1\""
else
	@echo "$(CYAN)=== Executando instância individual ===$(NC)"
	@./$(EXECUTABLE) single "$(FILE)"
endif

compare:
ifndef FILES
	@echo "$(RED)Erro: Especifique os arquivos com FILES=\"arq1.csv arq2.csv\"$(NC)"
else
	@echo "$(CYAN)=== Comparando resultados ===$(NC)"
	@.venv_wsl/bin/python scripts/analyze_results.py --compare $(FILES)
endif

# ============================================================
# ANÁLISE E LIMPEZA
# ============================================================
analyze:
	@echo "$(CYAN)=== Analisando Resultados ===$(NC)"
	@venv/bin/python scripts/analyze_results.py
	@echo "$(GREEN)=== Análise concluída ===$(NC)"

clean:
	@echo "$(CYAN)=== Limpando projeto ===$(NC)"
	@rm -rf $(BUILD_DIR)
	@rm -f $(RESULTS_DIR_ETAPA1)/*.csv 2>/dev/null || true
	@rm -rf $(RESULTS_DIR_ETAPA1)/analysis 2>/dev/null || true
	@rm -f $(RESULTS_DIR_ETAPA2)/*.csv 2>/dev/null || true
	@rm -rf $(RESULTS_DIR_ETAPA2)/analysis 2>/dev/null || true
	@echo "$(GREEN)=== Limpeza concluída ===$(NC)"

# Rebuild completo
rebuild: clean build

# Build + Run + Analyze
full: build run analyze
