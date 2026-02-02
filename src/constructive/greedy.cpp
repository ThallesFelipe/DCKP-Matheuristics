/**
 * @file greedy.cpp
 * @brief Implementação das heurísticas construtivas gulosas
 */

#include "greedy.h"

#include <algorithm>
#include <chrono>
#include <functional>
#include <iostream>
#include <ranges>

GreedyConstructive::GreedyConstructive(const DCKPInstance &inst) noexcept
    : instance_(inst), validator_(inst) {}

double GreedyConstructive::calculateScore(int item, GreedyStrategy strategy) const noexcept
{
    switch (strategy)
    {
    case GreedyStrategy::MAX_PROFIT:
        return static_cast<double>(instance_.profits[item]);

    case GreedyStrategy::MIN_WEIGHT:
        return -static_cast<double>(instance_.weights[item]);

    case GreedyStrategy::MAX_PROFIT_WEIGHT:
        if (instance_.weights[item] == 0)
        {
            return static_cast<double>(instance_.profits[item]) * 1000.0;
        }
        return static_cast<double>(instance_.profits[item]) /
               static_cast<double>(instance_.weights[item]);

    case GreedyStrategy::MIN_CONFLICTS:
        return -static_cast<double>(instance_.getConflictDegree(item));
    }
    return 0.0;
}

std::vector<int> GreedyConstructive::sortItemsByStrategy(GreedyStrategy strategy) const
{
    std::vector<ItemScore> scores;
    scores.reserve(static_cast<std::size_t>(instance_.n_items));

    for (int i = 0; i < instance_.n_items; ++i)
    {
        scores.push_back({i, calculateScore(i, strategy)});
    }

    std::ranges::sort(scores, std::greater<>{});

    std::vector<int> result;
    result.reserve(scores.size());
    for (const auto &s : scores)
    {
        result.push_back(s.item_id);
    }

    return result;
}

Solution GreedyConstructive::construct(GreedyStrategy strategy)
{
    const auto start = std::chrono::steady_clock::now();

    Solution solution;
    solution.method_name = std::string("Greedy_") + std::string(strategyToString(strategy));

    for (int item : sortItemsByStrategy(strategy))
    {
        if (!validator_.checkCapacity(solution.total_weight, instance_.weights[item]))
        {
            continue;
        }

        if (!validator_.checkConflicts(item, solution.selected_items))
        {
            continue;
        }

        solution.addItem(item, instance_.profits[item], instance_.weights[item]);
    }

    validator_.validate(solution);

    const auto end = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = end - start;
    solution.computation_time = elapsed.count();

    std::cout << "Greedy (" << strategyToString(strategy) << "): "
              << "Valor = " << solution.total_profit
              << ", Itens = " << solution.size()
              << ", Tempo = " << solution.computation_time << "s\n";

    return solution;
}

std::vector<Solution> GreedyConstructive::constructAll()
{
    std::cout << "\n--- Estrategias Greedy ---\n";

    std::vector<Solution> solutions;
    solutions.reserve(4);

    solutions.push_back(construct(GreedyStrategy::MAX_PROFIT));
    solutions.push_back(construct(GreedyStrategy::MIN_WEIGHT));
    solutions.push_back(construct(GreedyStrategy::MAX_PROFIT_WEIGHT));
    solutions.push_back(construct(GreedyStrategy::MIN_CONFLICTS));

    const auto best = std::ranges::max_element(solutions, {},
                                               [](const Solution &s)
                                               { return s.total_profit; });
    std::cout << "Melhor Greedy: " << best->method_name << " = " << best->total_profit << "\n";

    return solutions;
}

std::string_view GreedyConstructive::strategyToString(GreedyStrategy strategy) noexcept
{
    switch (strategy)
    {
    case GreedyStrategy::MAX_PROFIT:
        return "MaxProfit";
    case GreedyStrategy::MIN_WEIGHT:
        return "MinWeight";
    case GreedyStrategy::MAX_PROFIT_WEIGHT:
        return "MaxProfitWeight";
    case GreedyStrategy::MIN_CONFLICTS:
        return "MinConflicts";
    }
    return "Unknown";
}
