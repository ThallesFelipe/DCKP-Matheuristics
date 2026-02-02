/**
 * @file validator.cpp
 * @brief Implementação da classe Validator
 */

#include "validator.h"

#include <iostream>
#include <sstream>
#include <vector>

Validator::Validator(const DCKPInstance &inst) noexcept
    : instance_(inst) {}

bool Validator::validate(Solution &solution) const
{
    bool valid = true;

    // Verifica restrição de capacidade
    if (solution.total_weight > instance_.capacity)
    {
        std::cerr << "Capacidade excedida: " << solution.total_weight
                  << " > " << instance_.capacity << '\n';
        valid = false;
    }

    // Verifica restrições de conflitos
    std::vector<int> items(solution.selected_items.begin(), solution.selected_items.end());
    const auto n = items.size();
    for (std::size_t i = 0; i < n; ++i)
    {
        for (std::size_t j = i + 1; j < n; ++j)
        {
            if (instance_.hasConflict(items[i], items[j]))
            {
                std::cerr << "Conflito: " << (items[i] + 1)
                          << " <-> " << (items[j] + 1) << '\n';
                valid = false;
            }
        }
    }

    recalculateMetrics(solution);
    solution.is_feasible = valid;
    return valid;
}

bool Validator::checkCapacity(int current_weight, int item_weight) const noexcept
{
    return (current_weight + item_weight) <= instance_.capacity;
}

bool Validator::checkConflicts(int item, const std::set<int> &selected_items) const noexcept
{
    for (int selected : selected_items)
    {
        if (instance_.hasConflict(item, selected))
        {
            return false;
        }
    }
    return true;
}

std::string Validator::validateDetailed(const Solution &solution) const
{
    std::ostringstream ss;

    ss << "Itens: " << solution.selected_items.size()
       << ", Peso: " << solution.total_weight << '/' << instance_.capacity
       << ", Lucro: " << solution.total_profit;

    const bool capacity_ok = solution.total_weight <= instance_.capacity;
    ss << " | Capacidade: " << (capacity_ok ? "OK" : "VIOLADA");

    int conflict_count = 0;
    std::vector<int> items(solution.selected_items.begin(), solution.selected_items.end());
    const auto n = items.size();
    for (std::size_t i = 0; i < n; ++i)
    {
        for (std::size_t j = i + 1; j < n; ++j)
        {
            if (instance_.hasConflict(items[i], items[j]))
            {
                ++conflict_count;
            }
        }
    }

    ss << " | Conflitos: " << conflict_count;
    ss << " | " << ((capacity_ok && conflict_count == 0) ? "VIAVEL" : "INVIAVEL");

    return ss.str();
}

void Validator::recalculateMetrics(Solution &solution) const noexcept
{
    int profit = 0;
    int weight = 0;

    for (int item : solution.selected_items)
    {
        if (item >= 0 && item < instance_.n_items)
        {
            profit += instance_.profits[item];
            weight += instance_.weights[item];
        }
    }

    solution.total_profit = profit;
    solution.total_weight = weight;
}
