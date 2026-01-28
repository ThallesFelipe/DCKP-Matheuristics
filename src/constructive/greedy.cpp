/**
 * @file greedy.cpp
 * @brief Implementacao das heuristicas construtivas gulosas
 */

#include "greedy.h"
#include <algorithm>
#include <chrono>
#include <iostream>

GreedyConstructive::GreedyConstructive(const DCKPInstance &inst)
    : instance(inst), validator(inst) {}

double GreedyConstructive::calculateScore(int item, GreedyStrategy strategy) const
{
    switch (strategy)
    {
    case GreedyStrategy::MAX_PROFIT:
        return static_cast<double>(instance.profits[item]);

    case GreedyStrategy::MIN_WEIGHT:
        return -static_cast<double>(instance.weights[item]);

    case GreedyStrategy::MAX_PROFIT_WEIGHT:
        if (instance.weights[item] == 0)
            return static_cast<double>(instance.profits[item]) * 1000.0;
        return static_cast<double>(instance.profits[item]) / instance.weights[item];

    case GreedyStrategy::MIN_CONFLICTS:
        return -static_cast<double>(instance.conflict_graph[item].size());

    default:
        return 0.0;
    }
}

std::vector<int> GreedyConstructive::sortItemsByStrategy(GreedyStrategy strategy) const
{
    std::vector<ItemScore> scores;
    scores.reserve(instance.n_items);

    for (int i = 0; i < instance.n_items; i++)
    {
        scores.push_back({i, calculateScore(i, strategy)});
    }

    std::sort(scores.begin(), scores.end(), std::greater<ItemScore>());

    std::vector<int> result;
    result.reserve(instance.n_items);
    for (const auto &s : scores)
        result.push_back(s.item_id);

    return result;
}

Solution GreedyConstructive::construct(GreedyStrategy strategy)
{
    auto start = std::chrono::steady_clock::now();

    Solution solution;
    solution.method_name = "Greedy_" + strategyToString(strategy);

    for (int item : sortItemsByStrategy(strategy))
    {
        if (!validator.checkCapacity(solution.total_weight, instance.weights[item]))
            continue;

        if (!validator.checkConflicts(item, solution.selected_items))
            continue;

        solution.addItem(item, instance.profits[item], instance.weights[item]);
    }

    validator.validate(solution);

    auto end = std::chrono::steady_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    solution.computation_time = std::max(0.0, elapsed.count());

    std::cout << "Greedy (" << strategyToString(strategy) << "): "
              << "Valor = " << solution.total_profit
              << ", Itens = " << solution.size()
              << ", Tempo = " << solution.computation_time << "s" << std::endl;

    return solution;
}

std::vector<Solution> GreedyConstructive::constructAll()
{
    std::cout << "\n--- Estrategias Greedy ---\n";

    std::vector<Solution> solutions;
    solutions.push_back(construct(GreedyStrategy::MAX_PROFIT));
    solutions.push_back(construct(GreedyStrategy::MIN_WEIGHT));
    solutions.push_back(construct(GreedyStrategy::MAX_PROFIT_WEIGHT));
    solutions.push_back(construct(GreedyStrategy::MIN_CONFLICTS));

    auto best = std::max_element(solutions.begin(), solutions.end());
    std::cout << "Melhor Greedy: " << best->method_name << " = " << best->total_profit << "\n";

    return solutions;
}

std::string GreedyConstructive::strategyToString(GreedyStrategy strategy)
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
    default:
        return "Unknown";
    }
}
