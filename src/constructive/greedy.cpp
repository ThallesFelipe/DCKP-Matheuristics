/**
 * @file greedy.cpp
 * @brief Implementação das heurísticas construtivas gulosas
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
            return 1e9;
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
        ItemScore is;
        is.item_id = i;
        is.score = calculateScore(i, strategy);
        scores.push_back(is);
    }

    // Ordena em ordem decrescente de score
    std::sort(scores.begin(), scores.end(), std::greater<ItemScore>());

    std::vector<int> sorted_items;
    sorted_items.reserve(instance.n_items);
    for (const auto &item_score : scores)
    {
        sorted_items.push_back(item_score.item_id);
    }

    return sorted_items;
}

Solution GreedyConstructive::construct(GreedyStrategy strategy)
{
    auto start_time = std::chrono::high_resolution_clock::now();

    Solution solution;
    solution.method_name = "Greedy_" + strategyToString(strategy);

    // Ordena itens pela estratégia escolhida
    std::vector<int> sorted_items = sortItemsByStrategy(strategy);

    // Tenta adicionar cada item na ordem
    for (int item : sorted_items)
    {
        // Verifica capacidade
        if (!validator.checkCapacity(solution.total_weight, instance.weights[item]))
        {
            continue;
        }

        // Verifica conflitos
        if (!validator.checkConflicts(item, solution.selected_items))
        {
            continue;
        }

        // Adiciona o item
        solution.addItem(item, instance.profits[item], instance.weights[item]);
    }

    // Valida a solução final
    validator.validate(solution);

    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;
    solution.computation_time = elapsed.count();

    std::cout << "Greedy (" << strategyToString(strategy) << "): "
              << "Valor = " << solution.total_profit
              << ", Itens = " << solution.size()
              << ", Tempo = " << solution.computation_time << "s" << std::endl;

    return solution;
}

std::vector<Solution> GreedyConstructive::constructAll()
{
    std::cout << "\n=== Executando todas as estratégias Greedy ===" << std::endl;

    std::vector<Solution> solutions;

    solutions.push_back(construct(GreedyStrategy::MAX_PROFIT));
    solutions.push_back(construct(GreedyStrategy::MIN_WEIGHT));
    solutions.push_back(construct(GreedyStrategy::MAX_PROFIT_WEIGHT));
    solutions.push_back(construct(GreedyStrategy::MIN_CONFLICTS));

    // Encontra a melhor solução
    auto best = std::max_element(solutions.begin(), solutions.end(),
                                 [](const Solution &a, const Solution &b)
                                 {
                                     return a.total_profit < b.total_profit;
                                 });

    std::cout << "\nMelhor estratégia Greedy: " << best->method_name
              << " com valor = " << best->total_profit << std::endl;
    std::cout << "=============================================\n"
              << std::endl;

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
