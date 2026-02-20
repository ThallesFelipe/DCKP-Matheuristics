# DCKP Matheuristics

Projeto de heurísticas e metaheurísticas para o **Disjunctively Constrained Knapsack Problem (DCKP)**.

## Estrutura do projeto

- `src/` — implementação C++ (construtivas, buscas locais, metaheurísticas e utilitários)
- `scripts/` — automações de build, execução, análise e limpeza
- `DCKP-instances/` — instâncias de benchmark
- `results/` — saídas dos experimentos por etapa
- `results/analysis/` — métricas e tabelas de análise

## Fluxo rápido (Windows)

1. Build:
   - `./scripts/build.ps1`
2. Executar experimentos:
   - `./scripts/run_experiments.ps1 etapa1`
   - `./scripts/run_experiments.ps1 etapa2`
   - `./scripts/run_experiments.ps1 etapa3`
3. Analisar resultados:
   - `python scripts/analyze_results.py`

## Fluxo rápido (Linux/WSL)

1. Build:
   - `./scripts/build.sh`
2. Executar experimentos:
   - `./scripts/run_experiments.sh etapa1`
   - `./scripts/run_experiments.sh etapa2`
   - `./scripts/run_experiments.sh etapa3`
3. Analisar resultados:
   - `./scripts/analyze.sh`
