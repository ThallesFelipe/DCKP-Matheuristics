/**
 * @file vnd.cpp
 * @brief Implementação do Variable Neighborhood Descent para o DCKP
 */

#include "vnd.h"

#include <algorithm>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <vector>

VND::VND(const DCKPInstance &inst) noexcept
    : instance_(inst), validator_(inst) {}

std::vector<Solution> VND::generateAddDropNeighborhood(const Solution &current_sol) const
{
    std::vector<Solution> neighborhood;
    neighborhood.reserve(static_cast<std::size_t>(instance_.n_items));

    // Movimentos ADD: tenta adicionar cada item não presente na solução
    for (int i = 0; i < instance_.n_items; ++i)
    {
        if (current_sol.hasItem(i))
        {
            continue;
        }

        // Verifica capacidade
        if (current_sol.total_weight + instance_.weights[i] > instance_.capacity)
        {
            continue;
        }

        // Verifica conflitos
        bool has_conflict = false;
        for (int selected : current_sol.selected_items)
        {
            if (instance_.hasConflict(i, selected))
            {
                has_conflict = true;
                break;
            }
        }

        if (has_conflict)
        {
            continue;
        }

        Solution neighbor = current_sol;
        neighbor.addItem(i, instance_.profits[i], instance_.weights[i]);
        neighbor.is_feasible = true;
        neighborhood.push_back(std::move(neighbor));
    }

    // Movimentos DROP: tenta remover cada item da solução
    for (int item : current_sol.selected_items)
    {
        Solution neighbor = current_sol;
        neighbor.removeItem(item, instance_.profits[item], instance_.weights[item]);
        neighbor.is_feasible = true;
        neighborhood.push_back(std::move(neighbor));
    }

    return neighborhood;
}

std::vector<Solution> VND::generateSwap11Neighborhood(const Solution &current_sol) const
{
    std::vector<Solution> neighborhood;

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

    neighborhood.reserve(in_solution.size() * out_solution.size() / 4);

    for (int item_out : in_solution)
    {
        const int weight_freed = instance_.weights[item_out];
        const int profit_lost = instance_.profits[item_out];

        for (int item_in : out_solution)
        {
            const int new_weight = current_sol.total_weight - weight_freed + instance_.weights[item_in];

            if (new_weight > instance_.capacity)
            {
                continue;
            }

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

            Solution neighbor = current_sol;
            neighbor.removeItem(item_out, profit_lost, weight_freed);
            neighbor.addItem(item_in, instance_.profits[item_in], instance_.weights[item_in]);
            neighbor.is_feasible = true;
            neighborhood.push_back(std::move(neighbor));
        }
    }

    return neighborhood;
}

std::vector<Solution> VND::generateSwap21Neighborhood(const Solution &current_sol) const
{
    std::vector<Solution> neighborhood;

    std::vector<int> in_solution(current_sol.selected_items.begin(),
                                 current_sol.selected_items.end());

    if (in_solution.size() < 2)
    {
        return neighborhood;
    }

    std::vector<int> out_solution;
    out_solution.reserve(static_cast<std::size_t>(instance_.n_items) - in_solution.size());
    for (int i = 0; i < instance_.n_items; ++i)
    {
        if (!current_sol.hasItem(i))
        {
            out_solution.push_back(i);
        }
    }

    // Gera todos os movimentos Swap(2-1): remove 2 itens, adiciona 1
    const auto n_in = in_solution.size();
    for (std::size_t i = 0; i < n_in; ++i)
    {
        for (std::size_t j = i + 1; j < n_in; ++j)
        {
            const int item_out1 = in_solution[i];
            const int item_out2 = in_solution[j];

            const int freed_weight = instance_.weights[item_out1] + instance_.weights[item_out2];
            const int freed_profit = instance_.profits[item_out1] + instance_.profits[item_out2];

            for (int item_in : out_solution)
            {
                // Só vale a pena se o item entrante tiver lucro maior
                if (instance_.profits[item_in] <= freed_profit)
                {
                    continue;
                }

                const int new_weight = current_sol.total_weight - freed_weight + instance_.weights[item_in];

                if (new_weight > instance_.capacity)
                {
                    continue;
                }

                // Verifica conflitos com itens restantes (excluindo os dois removidos)
                bool has_conflict = false;
                for (int remaining : current_sol.selected_items)
                {
                    if (remaining == item_out1 || remaining == item_out2)
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

                Solution neighbor = current_sol;
                neighbor.removeItem(item_out1,
                                    instance_.profits[item_out1],
                                    instance_.weights[item_out1]);
                neighbor.removeItem(item_out2,
                                    instance_.profits[item_out2],
                                    instance_.weights[item_out2]);
                neighbor.addItem(item_in,
                                 instance_.profits[item_in],
                                 instance_.weights[item_in]);
                neighbor.is_feasible = true;
                neighborhood.push_back(std::move(neighbor));
            }
        }
    }

    return neighborhood;
}

std::pair<Solution, bool> VND::exploreNeighborhood(
    const Solution &current_sol,
    NeighborhoodType type) const
{
    std::vector<Solution> neighborhood;

    switch (type)
    {
    case NeighborhoodType::ADD_DROP:
        neighborhood = generateAddDropNeighborhood(current_sol);
        break;
    case NeighborhoodType::SWAP_1_1:
        neighborhood = generateSwap11Neighborhood(current_sol);
        break;
    case NeighborhoodType::SWAP_2_1:
        neighborhood = generateSwap21Neighborhood(current_sol);
        break;
    }

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
        return {*best, true};
    }
    return {current_sol, false};
}

Solution VND::solve(const Solution &initial_solution, int max_iterations)
{
    const auto start = std::chrono::steady_clock::now();

    Solution current_sol = initial_solution;
    current_sol.method_name = "VND";

    int iteration = 0;
    int k = 1; // Start with first neighborhood
    int improvements = 0;

    while (k <= 3 && iteration < max_iterations)
    {
        auto type = static_cast<NeighborhoodType>(k);
        auto [best_neighbor, found_improvement] = exploreNeighborhood(current_sol, type);

        if (found_improvement)
        {
            current_sol = std::move(best_neighbor);
            k = 1; // Reset to first neighborhood
            ++improvements;
        }
        else
        {
            ++k; // Move to next neighborhood
        }
        ++iteration;
    }

    const auto end = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = end - start;
    current_sol.computation_time = elapsed.count();

    std::cout << "VND: "
              << "Valor = " << current_sol.total_profit
              << ", Iteracoes = " << iteration
              << ", Melhorias = " << improvements
              << ", Tempo = " << std::fixed << std::setprecision(4)
              << current_sol.computation_time << "s\n";

    return current_sol;
}
