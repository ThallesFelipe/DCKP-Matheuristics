/**
 * @file hill_climbing.cpp
 * @brief Implementação do Hill Climbing com Best Improvement para o DCKP
 */

#include "hill_climbing.h"

#include <algorithm>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <vector>

HillClimbing::HillClimbing(const DCKPInstance &inst) noexcept
    : instance_(inst), validator_(inst) {}

std::vector<Solution> HillClimbing::generateSwapNeighborhood(const Solution &current_sol) const
{
    std::vector<Solution> neighborhood;

    // Converte para vetores para acesso indexado eficiente
    std::vector<int> in_solution(current_sol.selected_items.begin(),
                                 current_sol.selected_items.end());

    std::vector<int> out_solution;
    out_solution.reserve(static_cast<std::size_t>(instance_.n_items) - in_solution.size());
    for (int i = 0; i < instance_.n_items; ++i)
    {
        if (!current_sol.hasItem(i))
        {
            out_solution.push_back(i);
        }
    }

    // Estima tamanho da vizinhança para pré-alocação
    neighborhood.reserve(in_solution.size() * out_solution.size() / 4);

    // Gera todos os movimentos Swap(1-1) viáveis
    for (int item_out : in_solution)
    {
        const int weight_freed = instance_.weights[item_out];
        const int profit_lost = instance_.profits[item_out];

        for (int item_in : out_solution)
        {
            // Verifica capacidade
            const int new_weight = current_sol.total_weight - weight_freed + instance_.weights[item_in];
            if (new_weight > instance_.capacity)
            {
                continue;
            }

            // Verifica conflitos: item_in não pode conflitar com itens restantes
            bool has_conflict = false;
            for (int remaining : current_sol.selected_items)
            {
                if (remaining == item_out)
                {
                    continue;
                }
                if (instance_.hasConflict(item_in, remaining))
                {
                    has_conflict = true;
                    break;
                }
            }

            if (has_conflict)
            {
                continue;
            }

            // Constrói a solução vizinha
            Solution neighbor = current_sol;
            neighbor.removeItem(item_out, profit_lost, weight_freed);
            neighbor.addItem(item_in, instance_.profits[item_in], instance_.weights[item_in]);
            neighbor.is_feasible = true;

            neighborhood.push_back(std::move(neighbor));
        }
    }

    return neighborhood;
}

std::optional<Solution> HillClimbing::findBestNeighbor(
    const Solution &current_sol,
    const std::vector<Solution> &neighborhood) const
{
    const Solution *best = nullptr;

    for (const auto &neighbor : neighborhood)
    {
        if (neighbor.total_profit > current_sol.total_profit)
        {
            if (!best || neighbor.total_profit > best->total_profit)
            {
                best = &neighbor;
            }
        }
    }

    if (best != nullptr)
    {
        return *best;
    }
    return std::nullopt;
}

Solution HillClimbing::solve(const Solution &initial_solution, int max_iterations)
{
    const auto start = std::chrono::steady_clock::now();

    Solution current_sol = initial_solution;
    current_sol.method_name = "HillClimbing";

    int iteration = 0;
    int improvements = 0;

    while (iteration < max_iterations)
    {
        auto neighborhood = generateSwapNeighborhood(current_sol);
        auto best_neighbor = findBestNeighbor(current_sol, neighborhood);

        if (!best_neighbor.has_value())
        {
            // Ótimo local atingido
            break;
        }

        current_sol = std::move(best_neighbor.value());
        ++improvements;
        ++iteration;
    }

    const auto end = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = end - start;
    current_sol.computation_time = elapsed.count();

    std::cout << "HillClimbing: "
              << "Valor = " << current_sol.total_profit
              << ", Iteracoes = " << iteration
              << ", Melhorias = " << improvements
              << ", Tempo = " << std::fixed << std::setprecision(4)
              << current_sol.computation_time << "s\n";

    return current_sol;
}
