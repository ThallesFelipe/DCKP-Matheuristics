/**
 * @file grasp.cpp
 * @brief Implementação da heurística construtiva GRASP
 */

#include "grasp.h"
#include <algorithm>
#include <chrono>
#include <iostream>
#include <cmath>

GRASPConstructive::GRASPConstructive(const DCKPInstance &inst, unsigned int seed)
    : instance(inst), validator(inst), rng(seed) {}

double GRASPConstructive::calculateScore(int item, const Solution &current_solution) const
{
    // Score baseado em valor/peso, penalizando conflitos
    double base_score = 0.0;

    if (instance.weights[item] > 0)
    {
        base_score = static_cast<double>(instance.profits[item]) / instance.weights[item];
    }
    else
    {
        base_score = 1e9; // Peso zero = score muito alto
    }

    // Penaliza itens com muitos conflitos
    int conflict_penalty = 0;
    for (int selected : current_solution.selected_items)
    {
        if (instance.hasConflict(item, selected))
        {
            conflict_penalty++;
        }
    }

    // Penaliza também itens com muitos conflitos no grafo
    conflict_penalty += instance.conflict_graph[item].size();

    // Aplica penalização
    double penalty_factor = 1.0 / (1.0 + 0.1 * conflict_penalty);

    return base_score * penalty_factor;
}

std::vector<int> GRASPConstructive::buildRCL(const Solution &current_solution, double alpha) const
{
    std::vector<Candidate> candidates;

    // Avalia todos os itens não selecionados e viáveis
    for (int i = 0; i < instance.n_items; i++)
    {
        // Pula itens já selecionados
        if (current_solution.hasItem(i))
        {
            continue;
        }

        // Verifica capacidade
        if (!validator.checkCapacity(current_solution.total_weight, instance.weights[i]))
        {
            continue;
        }

        // Verifica conflitos
        if (!validator.checkConflicts(i, current_solution.selected_items))
        {
            continue;
        }

        // Calcula score e adiciona aos candidatos
        Candidate c;
        c.item_id = i;
        c.score = calculateScore(i, current_solution);
        candidates.push_back(c);
    }

    // Se não há candidatos viáveis, retorna lista vazia
    if (candidates.empty())
    {
        return std::vector<int>();
    }

    // Ordena candidatos por score (decrescente)
    std::sort(candidates.begin(), candidates.end(), std::greater<Candidate>());

    // Determina limites da RCL
    double max_score = candidates.front().score;
    double min_score = candidates.back().score;
    double threshold = max_score - alpha * (max_score - min_score);

    // Constrói RCL com candidatos acima do threshold
    std::vector<int> rcl;
    for (const auto &candidate : candidates)
    {
        if (candidate.score >= threshold)
        {
            rcl.push_back(candidate.item_id);
        }
    }

    return rcl;
}

int GRASPConstructive::selectFromRCL(const std::vector<int> &rcl)
{
    if (rcl.empty())
    {
        return -1;
    }

    std::uniform_int_distribution<int> dist(0, rcl.size() - 1);
    int index = dist(rng);
    return rcl[index];
}

Solution GRASPConstructive::construct(double alpha)
{
    auto start_time = std::chrono::high_resolution_clock::now();

    Solution solution;
    solution.method_name = "GRASP_alpha" + std::to_string(alpha);

    // Constrói solução iterativamente
    while (true)
    {
        // Constrói a RCL
        std::vector<int> rcl = buildRCL(solution, alpha);

        // Se RCL vazia, não há mais candidatos viáveis
        if (rcl.empty())
        {
            break;
        }

        // Seleciona aleatoriamente da RCL
        int selected_item = selectFromRCL(rcl);

        if (selected_item == -1)
        {
            break;
        }

        // Adiciona o item à solução
        solution.addItem(selected_item,
                         instance.profits[selected_item],
                         instance.weights[selected_item]);
    }

    // Valida a solução final
    validator.validate(solution);

    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;
    solution.computation_time = elapsed.count();

    return solution;
}

Solution GRASPConstructive::multiStart(int iterations, double alpha)
{
    std::cout << "\n=== GRASP Multi-Start (alpha=" << alpha
              << ", iterations=" << iterations << ") ===" << std::endl;

    auto overall_start = std::chrono::high_resolution_clock::now();

    Solution best_solution;
    best_solution.total_profit = -1;

    double total_profit_sum = 0.0;
    int valid_solutions = 0;

    for (int iter = 0; iter < iterations; iter++)
    {
        Solution current = construct(alpha);

        if (current.is_feasible)
        {
            valid_solutions++;
            total_profit_sum += current.total_profit;

            if (current.total_profit > best_solution.total_profit)
            {
                best_solution = current;
                std::cout << "  Iteração " << (iter + 1) << ": Nova melhor = "
                          << current.total_profit << std::endl;
            }
        }
    }

    auto overall_end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> total_elapsed = overall_end - overall_start;

    best_solution.computation_time = total_elapsed.count();
    best_solution.method_name = "GRASP_MultiStart_" + std::to_string(iterations) + "_alpha" + std::to_string(alpha);

    double avg_profit = (valid_solutions > 0) ? (total_profit_sum / valid_solutions) : 0.0;

    std::cout << "\nResultados GRASP Multi-Start:" << std::endl;
    std::cout << "  Melhor valor: " << best_solution.total_profit << std::endl;
    std::cout << "  Valor médio: " << avg_profit << std::endl;
    std::cout << "  Soluções válidas: " << valid_solutions << "/" << iterations << std::endl;
    std::cout << "  Tempo total: " << total_elapsed.count() << "s" << std::endl;
    std::cout << "===============================================\n"
              << std::endl;

    return best_solution;
}

std::vector<Solution> GRASPConstructive::tuneAlpha(int iterations)
{
    std::cout << "\n=== Calibrando parâmetro alpha do GRASP ===" << std::endl;

    std::vector<double> alpha_values = {0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0};
    std::vector<Solution> results;

    for (double alpha : alpha_values)
    {
        std::cout << "\nTestando alpha = " << alpha << std::endl;
        Solution best = multiStart(iterations, alpha);
        results.push_back(best);
    }

    // Encontra o melhor alpha
    auto best_result = std::max_element(results.begin(), results.end(),
                                        [](const Solution &a, const Solution &b)
                                        {
                                            return a.total_profit < b.total_profit;
                                        });

    std::cout << "\n=== Resumo da Calibração ===" << std::endl;
    for (size_t i = 0; i < alpha_values.size(); i++)
    {
        std::cout << "  Alpha " << alpha_values[i] << ": "
                  << results[i].total_profit;
        if (&results[i] == &(*best_result))
        {
            std::cout << " <- MELHOR";
        }
        std::cout << std::endl;
    }
    std::cout << "============================\n"
              << std::endl;

    return results;
}

void GRASPConstructive::setSeed(unsigned int seed)
{
    rng.seed(seed);
}
