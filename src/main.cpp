/**
 * @file main.cpp
 * @brief Programa principal para execução dos experimentos da Etapa 1
 *
 * Este programa executa as heurísticas construtivas (Greedy e GRASP)
 * em instâncias do DCKP e salva os resultados para análise.
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <filesystem>
#include <chrono>
#include <iomanip>
#include <algorithm>

#include "utils/instance_reader.h"
#include "utils/solution.h"
#include "utils/validator.h"
#include "constructive/greedy.h"
#include "constructive/grasp.h"

namespace fs = std::filesystem;

/**
 * @brief Estrutura para armazenar resultados de experimentos
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

/**
 * @brief Salva resultados em formato CSV
 */
void saveResultsCSV(const std::vector<ExperimentResult> &results,
                    const std::string &filename)
{
    std::ofstream file(filename);
    if (!file.is_open())
    {
        std::cerr << "Erro ao criar arquivo de resultados: " << filename << std::endl;
        return;
    }

    // Cabeçalho CSV
    file << "Instance,Method,Profit,Weight,NumItems,Time,Feasible" << std::endl;

    // Dados
    for (const auto &result : results)
    {
        file << result.instance_name << ","
             << result.method << ","
             << result.profit << ","
             << result.weight << ","
             << result.n_items << ","
             << std::fixed << std::setprecision(6) << result.time << ","
             << (result.feasible ? "Yes" : "No") << std::endl;
    }

    file.close();
    std::cout << "Resultados salvos em: " << filename << std::endl;
}

/**
 * @brief Processa uma única instância com todos os métodos
 */
std::vector<ExperimentResult> processInstance(const std::string &instance_path,
                                              const std::string &instance_name)
{
    std::vector<ExperimentResult> results;

    std::cout << "\n========================================" << std::endl;
    std::cout << "Processando: " << instance_name << std::endl;
    std::cout << "========================================" << std::endl;

    // Carrega a instância
    DCKPInstance instance;
    if (!instance.readFromFile(instance_path))
    {
        std::cerr << "Falha ao carregar instância: " << instance_path << std::endl;
        return results;
    }

    instance.print();

    // Executa Greedy com todas as estratégias
    std::cout << "\n--- Heurísticas Gulosas ---" << std::endl;
    GreedyConstructive greedy(instance);
    std::vector<Solution> greedy_solutions = greedy.constructAll();

    for (const auto &sol : greedy_solutions)
    {
        ExperimentResult result;
        result.instance_name = instance_name;
        result.method = sol.method_name;
        result.profit = sol.total_profit;
        result.weight = sol.total_weight;
        result.n_items = sol.size();
        result.time = sol.computation_time;
        result.feasible = sol.is_feasible;
        results.push_back(result);
    }

    // Executa GRASP
    std::cout << "\n--- GRASP ---" << std::endl;
    GRASPConstructive grasp(instance);

    // GRASP com alpha = 0.3 e 100 iterações
    Solution grasp_solution = grasp.multiStart(100, 0.3);

    ExperimentResult grasp_result;
    grasp_result.instance_name = instance_name;
    grasp_result.method = grasp_solution.method_name;
    grasp_result.profit = grasp_solution.total_profit;
    grasp_result.weight = grasp_solution.total_weight;
    grasp_result.n_items = grasp_solution.size();
    grasp_result.time = grasp_solution.computation_time;
    grasp_result.feasible = grasp_solution.is_feasible;
    results.push_back(grasp_result);

    // Resumo da instância
    std::cout << "\n--- Resumo ---" << std::endl;
    auto best = std::max_element(results.begin(), results.end(),
                                 [](const ExperimentResult &a, const ExperimentResult &b)
                                 {
                                     return a.profit < b.profit;
                                 });

    std::cout << "Melhor método: " << best->method << std::endl;
    std::cout << "Melhor valor: " << best->profit << std::endl;

    return results;
}

/**
 * @brief Processa todas as instâncias de um diretório
 */
void processDirectory(const std::string &directory_path,
                      const std::string &output_csv)
{
    std::vector<ExperimentResult> all_results;

    std::cout << "\n=======================================" << std::endl;
    std::cout << "Processando diretório: " << directory_path << std::endl;
    std::cout << "=======================================\n"
              << std::endl;

    auto start_time = std::chrono::high_resolution_clock::now();

    // Itera sobre os arquivos do diretório
    for (const auto &entry : fs::directory_iterator(directory_path))
    {
        if (entry.is_regular_file())
        {
            std::string filepath = entry.path().string();
            std::string filename = entry.path().filename().string();

            // Pula arquivos .txt que são apenas documentação
            if (filename.find(".txt") != std::string::npos &&
                filename.length() > 10)
            {
                continue;
            }

            std::vector<ExperimentResult> instance_results =
                processInstance(filepath, filename);

            all_results.insert(all_results.end(),
                               instance_results.begin(),
                               instance_results.end());
        }
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;

    std::cout << "\n=======================================" << std::endl;
    std::cout << "Processamento completo!" << std::endl;
    std::cout << "Tempo total: " << elapsed.count() << " segundos" << std::endl;
    std::cout << "Total de resultados: " << all_results.size() << std::endl;
    std::cout << "=======================================\n"
              << std::endl;

    // Salva resultados
    saveResultsCSV(all_results, output_csv);
}

/**
 * @brief Função principal
 */
int main(int argc, char *argv[])
{
    std::cout << "========================================" << std::endl;
    std::cout << "DCKP - Etapa 1: Heurísticas Construtivas" << std::endl;
    std::cout << "========================================\n"
              << std::endl;

    if (argc < 2)
    {
        std::cout << "Uso: " << argv[0] << " <modo> [argumentos]" << std::endl;
        std::cout << "\nModos disponíveis:" << std::endl;
        std::cout << "  single <arquivo>           - Processa uma única instância" << std::endl;
        std::cout << "  batch <diretório> <csv>    - Processa todas as instâncias de um diretório" << std::endl;
        std::cout << "  tune <arquivo>             - Calibra alpha do GRASP em uma instância" << std::endl;
        std::cout << "\nExemplos:" << std::endl;
        std::cout << "  " << argv[0] << " single DCKP-instances/DCKP-instances-set I-100/I1 - I10/1I1" << std::endl;
        std::cout << "  " << argv[0] << " batch DCKP-instances/DCKP-instances-set I-100/I1 - I10 results/etapa1/results.csv" << std::endl;
        return 1;
    }

    std::string mode = argv[1];

    try
    {
        if (mode == "single" && argc >= 3)
        {
            // Modo single: processa uma instância
            std::string instance_path = argv[2];
            std::string instance_name = fs::path(instance_path).filename().string();

            std::vector<ExperimentResult> results =
                processInstance(instance_path, instance_name);

            // Salva resultados
            std::string output_file = "results/etapa1/single_" + instance_name + ".csv";
            saveResultsCSV(results, output_file);
        }
        else if (mode == "batch" && argc >= 4)
        {
            // Modo batch: processa diretório
            std::string directory_path = argv[2];
            std::string output_csv = argv[3];

            processDirectory(directory_path, output_csv);
        }
        else if (mode == "tune" && argc >= 3)
        {
            // Modo tune: calibra parâmetros
            std::string instance_path = argv[2];

            DCKPInstance instance;
            if (!instance.readFromFile(instance_path))
            {
                std::cerr << "Erro ao carregar instância" << std::endl;
                return 1;
            }

            GRASPConstructive grasp(instance);
            std::vector<Solution> results = grasp.tuneAlpha(20);

            // Salva resultados da calibração
            std::vector<ExperimentResult> tune_results;
            for (const auto &sol : results)
            {
                ExperimentResult result;
                result.instance_name = fs::path(instance_path).filename().string();
                result.method = sol.method_name;
                result.profit = sol.total_profit;
                result.weight = sol.total_weight;
                result.n_items = sol.size();
                result.time = sol.computation_time;
                result.feasible = sol.is_feasible;
                tune_results.push_back(result);
            }

            saveResultsCSV(tune_results, "results/etapa1/alpha_tuning.csv");
        }
        else
        {
            std::cerr << "Modo ou argumentos inválidos" << std::endl;
            return 1;
        }
    }
    catch (const std::exception &e)
    {
        std::cerr << "Erro durante execução: " << e.what() << std::endl;
        return 1;
    }

    std::cout << "\nPrograma finalizado com sucesso!" << std::endl;
    return 0;
}
