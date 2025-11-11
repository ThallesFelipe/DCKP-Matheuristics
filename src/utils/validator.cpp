/**
 * @file validator.cpp
 * @brief Implementação da classe Validator
 */

#include "validator.h"
#include <sstream>
#include <iostream>

Validator::Validator(const DCKPInstance &inst) : instance(inst) {}

bool Validator::validate(Solution &solution) const
{
    bool is_valid = true;

    // Verifica capacidade
    if (solution.total_weight > instance.capacity)
    {
        std::cerr << "ERRO: Capacidade excedida! "
                  << solution.total_weight << " > " << instance.capacity << std::endl;
        is_valid = false;
    }

    // Verifica conflitos
    std::vector<int> items(solution.selected_items.begin(), solution.selected_items.end());
    for (size_t i = 0; i < items.size(); i++)
    {
        for (size_t j = i + 1; j < items.size(); j++)
        {
            if (instance.hasConflict(items[i], items[j]))
            {
                std::cerr << "ERRO: Conflito detectado entre itens "
                          << (items[i] + 1) << " e " << (items[j] + 1) << std::endl;
                is_valid = false;
            }
        }
    }

    // Recalcula métricas para garantir consistência
    recalculateMetrics(solution);

    solution.is_feasible = is_valid;
    return is_valid;
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
        {
            return false;
        }
    }
    return true;
}

std::string Validator::validateDetailed(const Solution &solution) const
{
    std::stringstream ss;

    ss << "\n=== Validação Detalhada ===\n";
    ss << "Itens selecionados: " << solution.selected_items.size() << "\n";
    ss << "Valor total: " << solution.total_profit << "\n";
    ss << "Peso total: " << solution.total_weight << "/" << instance.capacity << "\n";

    // Verifica capacidade
    bool capacity_ok = solution.total_weight <= instance.capacity;
    ss << "Capacidade: " << (capacity_ok ? "OK" : "VIOLADA") << "\n";

    if (!capacity_ok)
    {
        ss << "  Excesso: " << (solution.total_weight - instance.capacity) << "\n";
    }

    // Verifica conflitos
    int conflict_count = 0;
    std::vector<int> items(solution.selected_items.begin(), solution.selected_items.end());
    for (size_t i = 0; i < items.size(); i++)
    {
        for (size_t j = i + 1; j < items.size(); j++)
        {
            if (instance.hasConflict(items[i], items[j]))
            {
                if (conflict_count == 0)
                {
                    ss << "Conflitos detectados:\n";
                }
                ss << "  Item " << (items[i] + 1) << " <-> Item " << (items[j] + 1) << "\n";
                conflict_count++;
            }
        }
    }

    if (conflict_count == 0)
    {
        ss << "Conflitos: OK (nenhum conflito)\n";
    }
    else
    {
        ss << "Total de conflitos: " << conflict_count << "\n";
    }

    bool is_valid = capacity_ok && (conflict_count == 0);
    ss << "\nResultado: " << (is_valid ? "SOLUÇÃO VIÁVEL" : "SOLUÇÃO INVIÁVEL") << "\n";
    ss << "==========================\n";

    return ss.str();
}

void Validator::recalculateMetrics(Solution &solution) const
{
    int profit = 0;
    int weight = 0;

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
