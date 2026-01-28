# Makefile para o projeto DCKP
# Para uso no Linux/WSL

.PHONY: all build run test analyze clean help menu \
        run-set1 run-set2 run-all \
        run-I1-I10 run-I11-I20 \
        run-C1 run-C3 run-C10 run-C15 \
        run-R1 run-R3 run-R10 run-R15 \
        run-all-C run-all-R \
        single compare

# Configurações
BUILD_DIR = build
BIN_DIR = $(BUILD_DIR)/bin
EXECUTABLE = $(BIN_DIR)/dckp_solver
RESULTS_DIR = results/etapa1

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
	@echo "$(BOLD)$(YELLOW)│  SET I - Instâncias Pequenas (100 instâncias)                   │$(NC)"
	@echo "$(BOLD)$(YELLOW)└─────────────────────────────────────────────────────────────────┘$(NC)"
	@echo "  $(GREEN)make run-I1-I10$(NC)     → Executar instâncias I1 a I10 (50 instâncias)"
	@echo "  $(GREEN)make run-I11-I20$(NC)    → Executar instâncias I11 a I20 (50 instâncias)"
	@echo "  $(GREEN)make run-set1$(NC)       → Executar TODO o Set I (100 instâncias)"
	@echo ""
	@echo "$(BOLD)$(YELLOW)┌─────────────────────────────────────────────────────────────────┐$(NC)"
	@echo "$(BOLD)$(YELLOW)│  SET II - Instâncias Grandes (6240 instâncias)                  │$(NC)"
	@echo "$(BOLD)$(YELLOW)└─────────────────────────────────────────────────────────────────┘$(NC)"
	@echo "  $(CYAN)[Correlacionadas - C]$(NC)"
	@echo "  $(GREEN)make run-C1$(NC)         → Densidade de conflito 1%"
	@echo "  $(GREEN)make run-C3$(NC)         → Densidade de conflito 3%"
	@echo "  $(GREEN)make run-C10$(NC)        → Densidade de conflito 10%"
	@echo "  $(GREEN)make run-C15$(NC)        → Densidade de conflito 15%"
	@echo "  $(GREEN)make run-all-C$(NC)      → Todas as instâncias C (C1+C3+C10+C15)"
	@echo ""
	@echo "  $(CYAN)[Randômicas - R]$(NC)"
	@echo "  $(GREEN)make run-R1$(NC)         → Densidade de conflito 1%"
	@echo "  $(GREEN)make run-R3$(NC)         → Densidade de conflito 3%"
	@echo "  $(GREEN)make run-R10$(NC)        → Densidade de conflito 10%"
	@echo "  $(GREEN)make run-R15$(NC)        → Densidade de conflito 15%"
	@echo "  $(GREEN)make run-all-R$(NC)      → Todas as instâncias R (R1+R3+R10+R15)"
	@echo ""
	@echo "  $(GREEN)make run-set2$(NC)       → Executar TODO o Set II (6240 instâncias)"
	@echo ""
	@echo "$(BOLD)$(YELLOW)┌─────────────────────────────────────────────────────────────────┐$(NC)"
	@echo "$(BOLD)$(YELLOW)│  EXECUÇÃO COMPLETA                                              │$(NC)"
	@echo "$(BOLD)$(YELLOW)└─────────────────────────────────────────────────────────────────┘$(NC)"
	@echo "  $(GREEN)make run-all$(NC)        → Executar TODOS os sets (Set I + Set II)"
	@echo ""
	@echo "$(BOLD)$(YELLOW)┌─────────────────────────────────────────────────────────────────┐$(NC)"
	@echo "$(BOLD)$(YELLOW)│  TESTES INDIVIDUAIS E COMPARAÇÕES                               │$(NC)"
	@echo "$(BOLD)$(YELLOW)└─────────────────────────────────────────────────────────────────┘$(NC)"
	@echo "  $(GREEN)make single FILE=<caminho>$(NC)"
	@echo "      Exemplo: make single FILE=\"DCKP-instances/DCKP-instances-set I-100/I1 - I10/1I1\""
	@echo ""
	@echo "  $(GREEN)make compare FILES=\"<arquivo1> <arquivo2> ...\"$(NC)"
	@echo "      Compara resultados de múltiplos arquivos CSV"
	@echo ""
	@echo "$(BOLD)$(YELLOW)┌─────────────────────────────────────────────────────────────────┐$(NC)"
	@echo "$(BOLD)$(YELLOW)│  UTILITÁRIOS                                                    │$(NC)"
	@echo "$(BOLD)$(YELLOW)└─────────────────────────────────────────────────────────────────┘$(NC)"
	@echo "  $(GREEN)make build$(NC)          → Compilar o projeto"
	@echo "  $(GREEN)make test$(NC)           → Teste rápido (1 instância)"
	@echo "  $(GREEN)make analyze$(NC)        → Analisar resultados"
	@echo "  $(GREEN)make clean$(NC)          → Limpar build e resultados"
	@echo "  $(GREEN)make help$(NC)           → Este menu"
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
# SET I - INSTÂNCIAS PEQUENAS
# ============================================================
run-I1-I10: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando I1-I10 ===$(NC)"
	@mkdir -p $(RESULTS_DIR)
	@./$(EXECUTABLE) batch "$(INSTANCES_I1_I10)" "$(RESULTS_DIR)/results_I1_I10.csv"
	@echo "$(GREEN)=== Concluído: I1-I10 ===$(NC)"

run-I11-I20: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando I11-I20 ===$(NC)"
	@mkdir -p $(RESULTS_DIR)
	@./$(EXECUTABLE) batch "$(INSTANCES_I11_I20)" "$(RESULTS_DIR)/results_I11_I20.csv"
	@echo "$(GREEN)=== Concluído: I11-I20 ===$(NC)"

run-set1: run-I1-I10 run-I11-I20
	@echo "$(GREEN)=== Set I completo! ===$(NC)"

# ============================================================
# SET II - INSTÂNCIAS CORRELACIONADAS (C)
# ============================================================
run-C1: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando C1 (correlacionadas, 1% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR)
	@./$(EXECUTABLE) batch "$(INSTANCES_C1)" "$(RESULTS_DIR)/results_C1.csv"
	@echo "$(GREEN)=== Concluído: C1 ===$(NC)"

run-C3: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando C3 (correlacionadas, 3% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR)
	@./$(EXECUTABLE) batch "$(INSTANCES_C3)" "$(RESULTS_DIR)/results_C3.csv"
	@echo "$(GREEN)=== Concluído: C3 ===$(NC)"

run-C10: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando C10 (correlacionadas, 10% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR)
	@./$(EXECUTABLE) batch "$(INSTANCES_C10)" "$(RESULTS_DIR)/results_C10.csv"
	@echo "$(GREEN)=== Concluído: C10 ===$(NC)"

run-C15: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando C15 (correlacionadas, 15% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR)
	@./$(EXECUTABLE) batch "$(INSTANCES_C15)" "$(RESULTS_DIR)/results_C15.csv"
	@echo "$(GREEN)=== Concluído: C15 ===$(NC)"

run-all-C: run-C1 run-C3 run-C10 run-C15
	@echo "$(GREEN)=== Todas as instâncias C concluídas! ===$(NC)"

# ============================================================
# SET II - INSTÂNCIAS RANDÔMICAS (R)
# ============================================================
run-R1: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando R1 (randômicas, 1% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR)
	@./$(EXECUTABLE) batch "$(INSTANCES_R1)" "$(RESULTS_DIR)/results_R1.csv"
	@echo "$(GREEN)=== Concluído: R1 ===$(NC)"

run-R3: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando R3 (randômicas, 3% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR)
	@./$(EXECUTABLE) batch "$(INSTANCES_R3)" "$(RESULTS_DIR)/results_R3.csv"
	@echo "$(GREEN)=== Concluído: R3 ===$(NC)"

run-R10: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando R10 (randômicas, 10% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR)
	@./$(EXECUTABLE) batch "$(INSTANCES_R10)" "$(RESULTS_DIR)/results_R10.csv"
	@echo "$(GREEN)=== Concluído: R10 ===$(NC)"

run-R15: $(EXECUTABLE)
	@echo "$(CYAN)=== Executando R15 (randômicas, 15% conflitos) ===$(NC)"
	@mkdir -p $(RESULTS_DIR)
	@./$(EXECUTABLE) batch "$(INSTANCES_R15)" "$(RESULTS_DIR)/results_R15.csv"
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
	@echo "$(CYAN)=== Teste Rápido ===$(NC)"
	@./$(EXECUTABLE) single "$(INSTANCES_I1_I10)/1I1"

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
	@rm -f $(RESULTS_DIR)/*.csv 2>/dev/null || true
	@rm -rf $(RESULTS_DIR)/analysis 2>/dev/null || true
	@echo "$(GREEN)=== Limpeza concluída ===$(NC)"

# Rebuild completo
rebuild: clean build

# Build + Run + Analyze
full: build run analyze
