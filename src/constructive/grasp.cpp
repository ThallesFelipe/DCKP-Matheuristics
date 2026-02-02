/**
 * @file grasp.cpp
 * @brief Implementação da heurística construtiva GRASP para o DCKP
 */

#include "grasp.h"

#include <algorithm>
#include <chrono>
#include <functional>
#include <iomanip>
#include <iostream>
#include <ranges>
#include <sstream>

GRASPConstructive::GRASPConstructive(const DCKPInstance &inst, unsigned int seed) noexcept
    : instance_(inst), validator_(inst), rng_(seed) {}

double GRASPConstructive::calculateScore(int item, const Solution &current_solution) const noexcept
{
    // Score base: razão valor/peso
    double base_score = 0.0;
    if (instance_.weights[item] > 0)
    {
        base_score = static_cast<double>(instance_.profits[item]) /
                     static_cast<double>(instance_.weights[item]);
    }
    else
    {
        base_score = static_cast<double>(instance_.profits[item]) * 1000.0;
    }

    // Penalização por conflitos potenciais
    int conflict_count = 0;
    for (int selected : current_solution.selected_items)
    {
        if (instance_.hasConflict(item, selected))
        {
            ++conflict_count;
        }
    }
    conflict_count += instance_.getConflictDegree(item);

    const double penalty = 1.0 / (1.0 + 0.1 * conflict_count);
    return base_score * penalty;
}

std::vector<int> GRASPConstructive::buildRCL(const Solution &current_solution, double alpha) const
{
    std::vector<Candidate> candidates;
    candidates.reserve(static_cast<std::size_t>(instance_.n_items));

    // Filtra candidatos viáveis
    for (int i = 0; i < instance_.n_items; ++i)
    {
        if (current_solution.hasItem(i))
        {
            continue;
        }

        if (!validator_.checkCapacity(current_solution.total_weight, instance_.weights[i]))
        {
            continue;
        }

        if (!validator_.checkConflicts(i, current_solution.selected_items))
        {
            continue;
        }

        candidates.push_back({i, calculateScore(i, current_solution)});
    }

    if (candidates.empty())
    {
        return {};
    }

    // Ordena por score decrescente
    std::ranges::sort(candidates, std::greater<>{});

    // Calcula threshold da RCL
    const double max_score = candidates.front().score;
    const double min_score = candidates.back().score;
    const double threshold = max_score - alpha * (max_score - min_score);

    // Constrói RCL com candidatos acima do threshold
    std::vector<int> rcl;
    rcl.reserve(candidates.size());
    for (const auto &c : candidates)
    {
        if (c.score >= threshold)
        {
            rcl.push_back(c.item_id);
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

    std::uniform_int_distribution<int> dist(0, static_cast<int>(rcl.size()) - 1);
    return rcl[dist(rng_)];
}

Solution GRASPConstructive::constructSolution(double alpha)
{
    Solution solution;

    while (true)
    {
        std::vector<int> rcl = buildRCL(solution, alpha);
        if (rcl.empty())
        {
            break;
        }

        const int selected = selectFromRCL(rcl);
        if (selected < 0)
        {
            break;
        }

        solution.addItem(selected, instance_.profits[selected], instance_.weights[selected]);
    }

    validator_.validate(solution);
    return solution;
}

Solution GRASPConstructive::solve(int iterations, double alpha)
{
    const auto start = std::chrono::steady_clock::now();

    Solution best;
    best.total_profit = -1;

    int improved_count = 0;
    double profit_sum = 0.0;

    for (int i = 0; i < iterations; ++i)
    {
        Solution current = constructSolution(alpha);

        if (current.is_feasible)
        {
            profit_sum += current.total_profit;

            if (current.total_profit > best.total_profit)
            {
                best = std::move(current);
                ++improved_count;
            }
        }
    }

    const auto end = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = end - start;

    best.computation_time = elapsed.count();

    std::ostringstream name;
    name << "GRASP_" << iterations << '_' << std::fixed << std::setprecision(1) << alpha;
    best.method_name = name.str();

    const double avg = (iterations > 0) ? profit_sum / iterations : 0.0;

    std::cout << "GRASP (iter=" << iterations << ", alpha=" << alpha << "): "
              << "Valor = " << best.total_profit
              << ", Media = " << std::fixed << std::setprecision(1) << avg
              << ", Melhorias = " << improved_count
              << ", Tempo = " << std::setprecision(4) << best.computation_time << "s\n";

    return best;
}

void GRASPConstructive::setSeed(unsigned int seed) noexcept
{
    rng_.seed(seed);
}
