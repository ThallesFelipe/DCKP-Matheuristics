/**
 * @file grasp.cpp
 * @brief Implementação da heurística construtiva GRASP para o DCKP
 */

#include "grasp.h"
#include <algorithm>
#include <chrono>
#include <iostream>
#include <sstream>
#include <iomanip>

GRASPConstructive::GRASPConstructive(const DCKPInstance &inst, unsigned int seed)
    : instance(inst), validator(inst), rng(seed) {}

double GRASPConstructive::calculateScore(int item, const Solution &current_solution) const
{
    double base_score = 0.0;

    if (instance.weights[item] > 0)
    {
        base_score = static_cast<double>(instance.profits[item]) / instance.weights[item];
    }
    else
    {
        base_score = static_cast<double>(instance.profits[item]) * 1000.0;
    }

    int conflict_count = 0;
    for (int selected : current_solution.selected_items)
    {
        if (instance.hasConflict(item, selected))
        {
            conflict_count++;
        }
    }
    conflict_count += static_cast<int>(instance.conflict_graph[item].size());

    double penalty = 1.0 / (1.0 + 0.1 * conflict_count);
    return base_score * penalty;
}

std::vector<int> GRASPConstructive::buildRCL(const Solution &current_solution, double alpha) const
{
    std::vector<Candidate> candidates;

    for (int i = 0; i < instance.n_items; i++)
    {
        if (current_solution.hasItem(i))
            continue;

        if (!validator.checkCapacity(current_solution.total_weight, instance.weights[i]))
            continue;

        if (!validator.checkConflicts(i, current_solution.selected_items))
            continue;

        Candidate c;
        c.item_id = i;
        c.score = calculateScore(i, current_solution);
        candidates.push_back(c);
    }

    if (candidates.empty())
        return {};

    std::sort(candidates.begin(), candidates.end(), std::greater<Candidate>());

    double max_score = candidates.front().score;
    double min_score = candidates.back().score;
    double threshold = max_score - alpha * (max_score - min_score);

    std::vector<int> rcl;
    for (const auto &c : candidates)
    {
        if (c.score >= threshold)
            rcl.push_back(c.item_id);
    }

    return rcl;
}

int GRASPConstructive::selectFromRCL(const std::vector<int> &rcl)
{
    if (rcl.empty())
        return -1;

    std::uniform_int_distribution<int> dist(0, static_cast<int>(rcl.size()) - 1);
    return rcl[dist(rng)];
}

Solution GRASPConstructive::constructSolution(double alpha)
{
    Solution solution;

    while (true)
    {
        std::vector<int> rcl = buildRCL(solution, alpha);
        if (rcl.empty())
            break;

        int selected = selectFromRCL(rcl);
        if (selected < 0)
            break;

        solution.addItem(selected, instance.profits[selected], instance.weights[selected]);
    }

    validator.validate(solution);
    return solution;
}

Solution GRASPConstructive::solve(int iterations, double alpha)
{
    auto start = std::chrono::steady_clock::now();

    Solution best;
    best.total_profit = -1;

    int improved_count = 0;
    double profit_sum = 0.0;

    for (int i = 0; i < iterations; i++)
    {
        Solution current = constructSolution(alpha);

        if (current.is_feasible)
        {
            profit_sum += current.total_profit;

            if (current.total_profit > best.total_profit)
            {
                best = current;
                improved_count++;
            }
        }
    }

    auto end = std::chrono::steady_clock::now();
    std::chrono::duration<double> elapsed = end - start;

    best.computation_time = std::max(0.0, elapsed.count());

    std::ostringstream name;
    name << "GRASP_" << iterations << "_" << std::fixed << std::setprecision(1) << alpha;
    best.method_name = name.str();

    double avg = (iterations > 0) ? profit_sum / iterations : 0.0;

    std::cout << "GRASP (iter=" << iterations << ", alpha=" << alpha << "): "
              << "Valor = " << best.total_profit
              << ", Media = " << std::fixed << std::setprecision(1) << avg
              << ", Melhorias = " << improved_count
              << ", Tempo = " << std::setprecision(4) << best.computation_time << "s"
              << std::endl;

    return best;
}

void GRASPConstructive::setSeed(unsigned int seed)
{
    rng.seed(seed);
}
