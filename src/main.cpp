/**
 * @file main.cpp
 * @brief Programa principal para experimentos com heurísticas e buscas locais do DCKP
 *
 * Este programa implementa um solver para o Disjunctively Constrained Knapsack Problem
 * usando heurísticas construtivas (Greedy, GRASP) e buscas locais (Hill Climbing, VND).
 *
 * @author Thalles e Luiz
 * @version 2.0
 */

#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <ranges>
#include <string>
#include <string_view>
#include <vector>

#include "constructive/grasp.h"
#include "constructive/greedy.h"
#include "local_search/hill_climbing.h"
#include "local_search/vnd.h"
#include "utils/instance_reader.h"
#include "utils/solution.h"
#include "utils/validator.h"

namespace fs = std::filesystem;

// ============================================================================
// Constantes de Configuração
// ============================================================================

namespace config
{
    constexpr int GRASP_ITERATIONS = 100;
    constexpr double GRASP_ALPHA = 0.3;
    constexpr int HILL_CLIMBING_MAX_ITER = 100;
    constexpr int VND_MAX_ITER = 1000;
    constexpr int CSV_TIME_PRECISION = 6;
}

// ============================================================================
// Estruturas de Dados
// ============================================================================

/**
 * @struct ExperimentResult
 * @brief Armazena os resultados de um experimento para exportação CSV
 */
struct ExperimentResult
{
    std::string instance_name;
    std::string method;
    int profit;
    int weight;
    int n_items;
    double time;
    bool feasible;
};

// ============================================================================
// Funções Auxiliares
// ============================================================================

/**
 * @brief Converte uma Solution para ExperimentResult
 */
[[nodiscard]] ExperimentResult solutionToResult(
    const std::string &instance_name,
    const Solution &sol) noexcept
{
    return {
        instance_name,
        sol.method_name,
        sol.total_profit,
        sol.total_weight,
        sol.size(),
        sol.computation_time,
        sol.is_feasible};
}

/**
 * @brief Salva resultados em formato CSV
 */
void saveResultsCSV(const std::vector<ExperimentResult> &results, const std::string &filename)
{
    std::ofstream file(filename);
    if (!file.is_open())
    {
        std::cerr << "Erro ao criar arquivo: " << filename << '\n';
        return;
    }

    file << "Instance,Method,Profit,Weight,NumItems,Time,Feasible\n";

    for (const auto &r : results)
    {
        file << r.instance_name << ','
             << r.method << ','
             << r.profit << ','
             << r.weight << ','
             << r.n_items << ','
             << std::fixed << std::setprecision(config::CSV_TIME_PRECISION) << r.time << ','
             << (r.feasible ? "Yes" : "No") << '\n';
    }

    std::cout << "Resultados salvos: " << filename << '\n';
}

/**
 * @brief Verifica se um arquivo deve ser processado como instância
 */
[[nodiscard]] bool isValidInstanceFile(const fs::directory_entry &entry)
{
    if (!entry.is_regular_file())
    {
        return false;
    }

    const std::string filename = entry.path().filename().string();
    if (filename.empty() || filename[0] == '.')
    {
        return false;
    }

    const std::string filepath = entry.path().string();
    if (filepath.find(".csv") != std::string::npos)
    {
        return false;
    }

    return true;
}

/**
 * @brief Imprime separador visual
 */
void printSeparator(char ch = '-', int width = 40)
{
    std::cout << '\n'
              << std::string(static_cast<std::size_t>(width), ch) << '\n';
}

// ============================================================================
// Processamento de Instâncias
// ============================================================================

/**
 * @brief Processa instância executando todas as heurísticas (Etapa 1 + Etapa 2)
 */
[[nodiscard]] std::vector<ExperimentResult> processInstance(
    const std::string &path,
    const std::string &name)
{
    std::vector<ExperimentResult> results;
    results.reserve(8);

    printSeparator();
    std::cout << "Instancia: " << name << '\n';
    printSeparator();

    DCKPInstance instance;
    if (!instance.readFromFile(path))
    {
        std::cerr << "Falha ao carregar: " << path << '\n';
        return results;
    }

    instance.print();

    // ETAPA 1: Heurísticas Construtivas
    std::cout << "\n--- ETAPA 1: Heuristicas Construtivas ---\n";

    // Greedy
    std::cout << "\n[Guloso]\n";
    GreedyConstructive greedy(instance);
    auto greedy_solutions = greedy.constructAll();

    for (const auto &sol : greedy_solutions)
    {
        results.push_back(solutionToResult(name, sol));
    }

    // GRASP
    std::cout << "\n[GRASP]\n";
    GRASPConstructive grasp(instance);
    Solution grasp_sol = grasp.solve(config::GRASP_ITERATIONS, config::GRASP_ALPHA);
    results.push_back(solutionToResult(name, grasp_sol));

    // ETAPA 2: Buscas Locais
    std::cout << "\n--- ETAPA 2: Buscas Locais ---\n";

    // Hill Climbing
    std::cout << "\n[Hill Climbing]\n";
    HillClimbing hc(instance);
    Solution hc_sol = hc.solve(grasp_sol, config::HILL_CLIMBING_MAX_ITER);
    results.push_back(solutionToResult(name, hc_sol));

    // VND
    std::cout << "\n[VND]\n";
    VND vnd(instance);
    Solution vnd_sol = vnd.solve(grasp_sol, config::VND_MAX_ITER);
    results.push_back(solutionToResult(name, vnd_sol));

    // Resumo
    auto best = std::ranges::max_element(results, {},
                                         [](const ExperimentResult &r)
                                         { return r.profit; });

    std::cout << "\nMelhor: " << best->method << " = " << best->profit << '\n';

    return results;
}

/**
 * @brief Processa instância executando apenas Etapa 1 (Heurísticas Construtivas)
 */
[[nodiscard]] std::vector<ExperimentResult> processInstanceEtapa1(
    const std::string &path,
    const std::string &name)
{
    std::vector<ExperimentResult> results;
    results.reserve(5);

    printSeparator();
    std::cout << "Instancia: " << name << '\n';
    printSeparator();

    DCKPInstance instance;
    if (!instance.readFromFile(path))
    {
        std::cerr << "Falha ao carregar: " << path << '\n';
        return results;
    }

    instance.print();
    std::cout << "\n--- ETAPA 1: Heuristicas Construtivas ---\n";

    // Greedy (todas as estratégias)
    std::cout << "\n[Guloso]\n";
    GreedyConstructive greedy(instance);
    auto greedy_solutions = greedy.constructAll();

    for (const auto &sol : greedy_solutions)
    {
        results.push_back(solutionToResult(name, sol));
    }

    // GRASP
    std::cout << "\n[GRASP]\n";
    GRASPConstructive grasp(instance);
    Solution grasp_sol = grasp.solve(config::GRASP_ITERATIONS, config::GRASP_ALPHA);
    results.push_back(solutionToResult(name, grasp_sol));

    // Resumo
    auto best = std::ranges::max_element(results, {},
                                         [](const ExperimentResult &r)
                                         { return r.profit; });

    std::cout << "\nMelhor (Etapa 1): " << best->method << " = " << best->profit << '\n';

    return results;
}

/**
 * @brief Processa instância executando apenas Etapa 2 (Buscas Locais)
 * @note Utiliza GRASP para gerar solução inicial e aplica HC + VND
 */
[[nodiscard]] std::vector<ExperimentResult> processInstanceEtapa2(
    const std::string &path,
    const std::string &name)
{
    std::vector<ExperimentResult> results;
    results.reserve(3);

    printSeparator();
    std::cout << "Instancia: " << name << '\n';
    printSeparator();

    DCKPInstance instance;
    if (!instance.readFromFile(path))
    {
        std::cerr << "Falha ao carregar: " << path << '\n';
        return results;
    }

    instance.print();
    std::cout << "\n--- ETAPA 2: Buscas Locais ---\n";

    // GRASP para gerar solução inicial
    std::cout << "\n[GRASP - Solucao Inicial]\n";
    GRASPConstructive grasp(instance);
    Solution grasp_sol = grasp.solve(config::GRASP_ITERATIONS, config::GRASP_ALPHA);
    results.push_back({name, "GRASP_Inicial", grasp_sol.total_profit, grasp_sol.total_weight,
                       grasp_sol.size(), grasp_sol.computation_time, grasp_sol.is_feasible});

    // Hill Climbing
    std::cout << "\n[Hill Climbing]\n";
    HillClimbing hc(instance);
    Solution hc_sol = hc.solve(grasp_sol, config::HILL_CLIMBING_MAX_ITER);
    results.push_back(solutionToResult(name, hc_sol));

    // VND
    std::cout << "\n[VND]\n";
    VND vnd(instance);
    Solution vnd_sol = vnd.solve(grasp_sol, config::VND_MAX_ITER);
    results.push_back(solutionToResult(name, vnd_sol));

    // Resumo
    auto best = std::ranges::max_element(results, {},
                                         [](const ExperimentResult &r)
                                         { return r.profit; });

    std::cout << "\nMelhor (Etapa 2): " << best->method << " = " << best->profit << '\n';

    return results;
}

// ============================================================================
// Processamento em Lote
// ============================================================================

/**
 * @brief Template para processamento de diretório
 */
template <typename ProcessFunc>
void processDirectoryGeneric(
    const std::string &dir_path,
    const std::string &output_csv,
    std::string_view stage_name,
    ProcessFunc process_func)
{
    std::vector<ExperimentResult> all_results;

    printSeparator('=', 40);
    if (!stage_name.empty())
    {
        std::cout << stage_name << '\n';
    }
    std::cout << "Diretorio: " << dir_path << '\n';
    printSeparator('=', 40);

    const auto start = std::chrono::high_resolution_clock::now();

    for (const auto &entry : fs::recursive_directory_iterator(dir_path))
    {
        if (!isValidInstanceFile(entry))
        {
            continue;
        }

        std::string filepath = entry.path().string();
        std::string filename = entry.path().filename().string();

        auto instance_results = process_func(filepath, filename);
        all_results.insert(all_results.end(),
                           std::make_move_iterator(instance_results.begin()),
                           std::make_move_iterator(instance_results.end()));
    }

    const auto end = std::chrono::high_resolution_clock::now();
    const std::chrono::duration<double> elapsed = end - start;

    printSeparator('=', 40);
    std::cout << "Concluido! Tempo: " << elapsed.count() << "s\n";
    std::cout << "Total de resultados: " << all_results.size() << '\n';
    printSeparator('=', 40);

    saveResultsCSV(all_results, output_csv);
}

void processDirectory(const std::string &dir_path, const std::string &output_csv)
{
    processDirectoryGeneric(dir_path, output_csv, "", processInstance);
}

void processDirectoryEtapa1(const std::string &dir_path, const std::string &output_csv)
{
    processDirectoryGeneric(dir_path, output_csv, "ETAPA 1 - Heuristicas Construtivas", processInstanceEtapa1);
}

void processDirectoryEtapa2(const std::string &dir_path, const std::string &output_csv)
{
    processDirectoryGeneric(dir_path, output_csv, "ETAPA 2 - Buscas Locais", processInstanceEtapa2);
}

// ============================================================================
// Interface de Linha de Comando
// ============================================================================

void printUsage(std::string_view prog)
{
    std::cout << "Uso: " << prog << " <modo> [argumentos]\n\n"
              << "Modos:\n"
              << "  single <arquivo> [csv]          Processa uma instancia (todas as etapas)\n"
              << "  batch <diretorio> <csv>         Processa todas as instancias (todas as etapas)\n"
              << "  batch-etapa1 <diretorio> <csv>  Processa apenas Etapa 1 (Greedy + GRASP)\n"
              << "  batch-etapa2 <diretorio> <csv>  Processa apenas Etapa 2 (GRASP + HC + VND)\n\n"
              << "Exemplos:\n"
              << "  " << prog << " single DCKP-instances/.../1I1\n"
              << "  " << prog << " batch DCKP-instances/... results/results.csv\n"
              << "  " << prog << " batch-etapa1 DCKP-instances/... results/etapa1/results.csv\n"
              << "  " << prog << " batch-etapa2 DCKP-instances/... results/etapa2/results.csv\n";
}

void printBanner()
{
    std::cout << "========================================\n"
              << "DCKP Solver v2.0\n"
              << "Heuristicas e Buscas Locais\n"
              << "========================================\n";
}

int main(int argc, char *argv[])
{
    printBanner();

    if (argc < 2)
    {
        printUsage(argv[0]);
        return EXIT_FAILURE;
    }

    const std::string_view mode = argv[1];

    try
    {
        if (mode == "single" && argc >= 3)
        {
            const std::string path = argv[2];
            const std::string name = fs::path(path).filename().string();
            auto results = processInstance(path, name);

            if (argc >= 4)
            {
                saveResultsCSV(results, argv[3]);
            }
        }
        else if (mode == "batch" && argc >= 4)
        {
            const fs::path csv_path(argv[3]);
            if (csv_path.has_parent_path())
            {
                fs::create_directories(csv_path.parent_path());
            }
            processDirectory(argv[2], argv[3]);
        }
        else if (mode == "batch-etapa1" && argc >= 4)
        {
            const fs::path csv_path(argv[3]);
            if (csv_path.has_parent_path())
            {
                fs::create_directories(csv_path.parent_path());
            }
            processDirectoryEtapa1(argv[2], argv[3]);
        }
        else if (mode == "batch-etapa2" && argc >= 4)
        {
            const fs::path csv_path(argv[3]);
            if (csv_path.has_parent_path())
            {
                fs::create_directories(csv_path.parent_path());
            }
            processDirectoryEtapa2(argv[2], argv[3]);
        }
        else
        {
            printUsage(argv[0]);
            return EXIT_FAILURE;
        }
    }
    catch (const std::exception &e)
    {
        std::cerr << "Erro: " << e.what() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "\nFinalizado.\n";
    return EXIT_SUCCESS;
}
