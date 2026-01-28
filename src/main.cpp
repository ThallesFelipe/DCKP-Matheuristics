/**
 * @file main.cpp
 * @brief Programa principal para experimentos com heurísticas construtivas do DCKP
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

void saveResultsCSV(const std::vector<ExperimentResult> &results, const std::string &filename)
{
    std::ofstream file(filename);
    if (!file.is_open())
    {
        std::cerr << "Erro ao criar arquivo: " << filename << std::endl;
        return;
    }

    file << "Instance,Method,Profit,Weight,NumItems,Time,Feasible\n";

    for (const auto &r : results)
    {
        file << r.instance_name << ","
             << r.method << ","
             << r.profit << ","
             << r.weight << ","
             << r.n_items << ","
             << std::fixed << std::setprecision(6) << r.time << ","
             << (r.feasible ? "Yes" : "No") << "\n";
    }

    std::cout << "Resultados salvos: " << filename << std::endl;
}

std::vector<ExperimentResult> processInstance(const std::string &path, const std::string &name)
{
    std::vector<ExperimentResult> results;

    std::cout << "\n----------------------------------------\n";
    std::cout << "Instancia: " << name << "\n";
    std::cout << "----------------------------------------\n";

    DCKPInstance instance;
    if (!instance.readFromFile(path))
    {
        std::cerr << "Falha ao carregar: " << path << std::endl;
        return results;
    }

    instance.print();

    // Greedy
    std::cout << "\n--- Heuristicas Gulosas ---\n";
    GreedyConstructive greedy(instance);
    auto greedy_solutions = greedy.constructAll();

    for (const auto &sol : greedy_solutions)
    {
        results.push_back({name, sol.method_name, sol.total_profit, sol.total_weight,
                           sol.size(), sol.computation_time, sol.is_feasible});
    }

    // GRASP
    std::cout << "\n--- GRASP ---\n";
    GRASPConstructive grasp(instance);
    Solution grasp_sol = grasp.solve(100, 0.3);

    results.push_back({name, grasp_sol.method_name, grasp_sol.total_profit, grasp_sol.total_weight,
                       grasp_sol.size(), grasp_sol.computation_time, grasp_sol.is_feasible});

    // Resumo
    auto best = std::max_element(results.begin(), results.end(),
                                 [](const ExperimentResult &a, const ExperimentResult &b)
                                 { return a.profit < b.profit; });

    std::cout << "\nMelhor: " << best->method << " = " << best->profit << "\n";

    return results;
}

void processDirectory(const std::string &dir_path, const std::string &output_csv)
{
    std::vector<ExperimentResult> all_results;

    std::cout << "\n========================================\n";
    std::cout << "Diretorio: " << dir_path << "\n";
    std::cout << "========================================\n";

    auto start = std::chrono::high_resolution_clock::now();

    for (const auto &entry : fs::recursive_directory_iterator(dir_path))
    {
        if (!entry.is_regular_file())
            continue;

        std::string filepath = entry.path().string();
        std::string filename = entry.path().filename().string();

        if (filename[0] == '.' || filepath.find(".csv") != std::string::npos)
            continue;

        auto instance_results = processInstance(filepath, filename);
        all_results.insert(all_results.end(), instance_results.begin(), instance_results.end());
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;

    std::cout << "\n========================================\n";
    std::cout << "Concluido! Tempo: " << elapsed.count() << "s\n";
    std::cout << "Total de resultados: " << all_results.size() << "\n";
    std::cout << "========================================\n";

    saveResultsCSV(all_results, output_csv);
}

void printUsage(const char *prog)
{
    std::cout << "Uso: " << prog << " <modo> [argumentos]\n\n";
    std::cout << "Modos:\n";
    std::cout << "  single <arquivo> [csv]     Processa uma instancia\n";
    std::cout << "  batch <diretorio> <csv>    Processa todas as instancias\n\n";
    std::cout << "Exemplos:\n";
    std::cout << "  " << prog << " single DCKP-instances/.../1I1\n";
    std::cout << "  " << prog << " batch DCKP-instances/... results/results.csv\n";
}

int main(int argc, char *argv[])
{
    std::cout << "========================================\n";
    std::cout << "DCKP - Heuristicas Construtivas\n";
    std::cout << "========================================\n";

    if (argc < 2)
    {
        printUsage(argv[0]);
        return 1;
    }

    std::string mode = argv[1];

    try
    {
        if (mode == "single" && argc >= 3)
        {
            std::string path = argv[2];
            std::string name = fs::path(path).filename().string();
            auto results = processInstance(path, name);

            if (argc >= 4)
                saveResultsCSV(results, argv[3]);
        }
        else if (mode == "batch" && argc >= 4)
        {
            fs::path csv_path(argv[3]);
            if (csv_path.has_parent_path())
                fs::create_directories(csv_path.parent_path());

            processDirectory(argv[2], argv[3]);
        }
        else
        {
            printUsage(argv[0]);
            return 1;
        }
    }
    catch (const std::exception &e)
    {
        std::cerr << "Erro: " << e.what() << std::endl;
        return 1;
    }

    std::cout << "\nFinalizado.\n";
    return 0;
}
