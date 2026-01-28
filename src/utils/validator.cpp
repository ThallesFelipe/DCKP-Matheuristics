/**
 * @file validator.cpp
 * @brief Implementacao da classe Validator
 */

#include "validator.h"
#include <sstream>
#include <iostream>

Validator::Validator(const DCKPInstance &inst) : instance(inst) {}

bool Validator::validate(Solution &solution) const
{
    bool valid = true;

    if (solution.total_weight > instance.capacity)
    {
        std::cerr << "Capacidade excedida: " << solution.total_weight
                  << " > " << instance.capacity << std::endl;
        valid = false;
    }

    std::vector<int> items(solution.selected_items.begin(), solution.selected_items.end());
    for (size_t i = 0; i < items.size(); i++)
    {
        for (size_t j = i + 1; j < items.size(); j++)
        {
            if (instance.hasConflict(items[i], items[j]))
            {
                std::cerr << "Conflito: " << (items[i] + 1)
                          << " <-> " << (items[j] + 1) << std::endl;
                valid = false;
            }
        }
    }

    recalculateMetrics(solution);
    solution.is_feasible = valid;
    return valid;
}

bool Validator::checkCapacity(int current_weight, int item_weight) const
{
    return (current_weight + item_weight) <= instance.capacity;
}

bool Validator::checkConflicts(int item, const std::set<int> &selected_items) const
{
    for (int selected : selected_items)
    {
        if (instance.hasConflict(item, selected))
            return false;
    }
    return true;
}

std::string Validator::validateDetailed(const Solution &solution) const
{
    std::ostringstream ss;

    ss << "Itens: " << solution.selected_items.size()
       << ", Peso: " << solution.total_weight << "/" << instance.capacity
       << ", Lucro: " << solution.total_profit;

    bool capacity_ok = solution.total_weight <= instance.capacity;
    ss << " | Capacidade: " << (capacity_ok ? "OK" : "VIOLADA");

    int conflict_count = 0;
    std::vector<int> items(solution.selected_items.begin(), solution.selected_items.end());
    for (size_t i = 0; i < items.size(); i++)
    {
        for (size_t j = i + 1; j < items.size(); j++)
        {
            if (instance.hasConflict(items[i], items[j]))
                conflict_count++;
        }
    }

    ss << " | Conflitos: " << conflict_count;
    ss << " | " << ((capacity_ok && conflict_count == 0) ? "VIAVEL" : "INVIAVEL");

    return ss.str();
}

void Validator::recalculateMetrics(Solution &solution) const
{
    int profit = 0, weight = 0;

    for (int item : solution.selected_items)
    {
        if (item >= 0 && item < instance.n_items)
        {
            profit += instance.profits[item];
            weight += instance.weights[item];
        }
    }

    solution.total_profit = profit;
    solution.total_weight = weight;
}
