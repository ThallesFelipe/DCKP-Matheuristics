/**
 * @file ils.cpp
 * @brief Implementação do Iterated Local Search para o DCKP
 */

#include "ils.h"
#include "../local_search/vnd.h"

#include <algorithm>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <vector>

ILS::ILS(const DCKPInstance &inst, unsigned int seed) noexcept
    : instance_(inst), validator_(inst), rng_(seed) {}

Solution ILS::perturb(const Solution &solution, int strength)
{
    Solution perturbed = solution;

    // Coleta itens na solução para remoção aleatória
    std::vector<int> items_in(perturbed.selected_items.begin(),
                              perturbed.selected_items.end());

    // Limita strength ao número de itens disponíveis
    const int removals = std::min(strength, static_cast<int>(items_in.size()));

    // Remove itens aleatórios
    for (int i = 0; i < removals && !items_in.empty(); ++i)
    {
        std::uniform_int_distribution<int> dist(0, static_cast<int>(items_in.size()) - 1);
        const int idx = dist(rng_);
        const int item = items_in[idx];

        perturbed.removeItem(item, instance_.profits[item], instance_.weights[item]);

        // Remove do vetor local (swap-and-pop)
        items_in[idx] = items_in.back();
        items_in.pop_back();
    }

    // Tenta inserir itens viáveis de forma gulosa-aleatória
    greedyRandomInsert(perturbed);

    return perturbed;
}

void ILS::greedyRandomInsert(Solution &solution)
{
    // Coleta candidatos viáveis
    std::vector<int> candidates;
    candidates.reserve(static_cast<std::size_t>(instance_.n_items));

    for (int i = 0; i < instance_.n_items; ++i)
    {
        if (solution.hasItem(i))
        {
            continue;
        }

        if (solution.total_weight + instance_.weights[i] > instance_.capacity)
        {
            continue;
        }

        bool has_conflict = false;
        for (int selected : solution.selected_items)
        {
            if (instance_.hasConflict(i, selected))
            {
                has_conflict = true;
                break;
            }
        }

        if (!has_conflict)
        {
            candidates.push_back(i);
        }
    }

    // Ordena por razão valor/peso decrescente
    std::ranges::sort(candidates, [this](int a, int b)
                      {
        const double ratio_a = (instance_.weights[a] > 0)
            ? static_cast<double>(instance_.profits[a]) / instance_.weights[a]
            : static_cast<double>(instance_.profits[a]) * 1000.0;
        const double ratio_b = (instance_.weights[b] > 0)
            ? static_cast<double>(instance_.profits[b]) / instance_.weights[b]
            : static_cast<double>(instance_.profits[b]) * 1000.0;
        return ratio_a > ratio_b; });

    // Insere com aleatoriedade controlada (escolhe entre os top candidatos)
    while (!candidates.empty())
    {
        // Seleciona entre os top 3 candidatos (ou menos se houver poucos)
        const int rcl_size = std::min(3, static_cast<int>(candidates.size()));
        std::uniform_int_distribution<int> dist(0, rcl_size - 1);
        const int idx = dist(rng_);
        const int item = candidates[idx];

        // Verifica viabilidade novamente (pode ter mudado)
        if (solution.total_weight + instance_.weights[item] <= instance_.capacity &&
            validator_.checkConflicts(item, solution.selected_items))
        {
            solution.addItem(item, instance_.profits[item], instance_.weights[item]);
        }

        // Remove candidato (swap-and-pop não preserva ordem, mas reordenação seria cara)
        candidates.erase(candidates.begin() + idx);

        // Refiltra candidatos que excederiam capacidade
        std::erase_if(candidates, [this, &solution](int c)
                      { return solution.total_weight + instance_.weights[c] > instance_.capacity ||
                               !validator_.checkConflicts(c, solution.selected_items); });
    }
}

Solution ILS::solve(
    const Solution &initial_solution,
    int max_iterations,
    int perturbation_strength,
    int vnd_max_iter)
{
    const auto start = std::chrono::steady_clock::now();

    // Aplica VND na solução inicial para obter ótimo local
    VND vnd(instance_);
    Solution current = vnd.solve(initial_solution, vnd_max_iter);
    Solution best = current;

    int improvements = 0;

    for (int iter = 0; iter < max_iterations; ++iter)
    {
        // Perturba solução corrente
        Solution perturbed = perturb(current, perturbation_strength);
        validator_.validate(perturbed);

        // Aplica VND na solução perturbada
        Solution local_opt = vnd.solve(perturbed, vnd_max_iter);

        // Critério de aceitação: aceita se melhorar ou empatar (diversificação)
        if (local_opt.total_profit >= current.total_profit)
        {
            current = std::move(local_opt);

            // Atualiza melhor global
            if (current.total_profit > best.total_profit)
            {
                best = current;
                ++improvements;
            }
        }
    }

    const auto end = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = end - start;

    best.computation_time = elapsed.count();
    best.method_name = "ILS";

    validator_.validate(best);

    std::cout << "ILS: "
              << "Valor = " << best.total_profit
              << ", Iteracoes = " << max_iterations
              << ", Melhorias = " << improvements
              << ", Perturbacao = " << perturbation_strength
              << ", Tempo = " << std::fixed << std::setprecision(4)
              << best.computation_time << "s\n";

    return best;
}

void ILS::setSeed(unsigned int seed) noexcept
{
    rng_.seed(seed);
}
