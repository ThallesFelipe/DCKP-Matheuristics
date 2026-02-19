/**
 * @file vns.cpp
 * @brief Implementação do Variable Neighborhood Search para o DCKP
 */

#include "vns.h"
#include "../local_search/vnd.h"

#include <algorithm>
#include <chrono>
#include <iomanip>
#include <iostream>
#include <vector>

VNS::VNS(const DCKPInstance &inst, unsigned int seed) noexcept
    : instance_(inst), validator_(inst), rng_(seed) {}

Solution VNS::shakeAddDrop(const Solution &solution, int strength)
{
    Solution shaken = solution;

    for (int s = 0; s < strength; ++s)
    {
        // Decide aleatoriamente entre Add ou Drop
        std::uniform_int_distribution<int> coin(0, 1);

        if (coin(rng_) == 0 && !shaken.selected_items.empty())
        {
            // DROP: remove um item aleatório
            std::vector<int> items_in(shaken.selected_items.begin(),
                                      shaken.selected_items.end());
            std::uniform_int_distribution<int> dist(0, static_cast<int>(items_in.size()) - 1);
            const int item = items_in[dist(rng_)];
            shaken.removeItem(item, instance_.profits[item], instance_.weights[item]);
        }
        else
        {
            // ADD: tenta adicionar um item aleatório viável
            std::vector<int> candidates;
            for (int i = 0; i < instance_.n_items; ++i)
            {
                if (shaken.hasItem(i))
                {
                    continue;
                }
                if (shaken.total_weight + instance_.weights[i] > instance_.capacity)
                {
                    continue;
                }
                bool has_conflict = false;
                for (int sel : shaken.selected_items)
                {
                    if (instance_.hasConflict(i, sel))
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

            if (!candidates.empty())
            {
                std::uniform_int_distribution<int> dist(0, static_cast<int>(candidates.size()) - 1);
                const int item = candidates[dist(rng_)];
                shaken.addItem(item, instance_.profits[item], instance_.weights[item]);
            }
        }
    }

    return shaken;
}

Solution VNS::shakeSwap11(const Solution &solution, int strength)
{
    Solution shaken = solution;

    for (int s = 0; s < strength; ++s)
    {
        std::vector<int> items_in(shaken.selected_items.begin(),
                                  shaken.selected_items.end());

        if (items_in.empty())
        {
            break;
        }

        // Seleciona item a remover aleatoriamente
        std::uniform_int_distribution<int> dist_in(0, static_cast<int>(items_in.size()) - 1);
        const int item_out = items_in[dist_in(rng_)];

        // Coleta candidatos para inserção após remoção
        std::vector<int> candidates;
        for (int i = 0; i < instance_.n_items; ++i)
        {
            if (shaken.hasItem(i) || i == item_out)
            {
                continue;
            }

            const int new_weight = shaken.total_weight - instance_.weights[item_out] + instance_.weights[i];
            if (new_weight > instance_.capacity)
            {
                continue;
            }

            bool has_conflict = false;
            for (int sel : shaken.selected_items)
            {
                if (sel == item_out)
                {
                    continue;
                }
                if (instance_.hasConflict(i, sel))
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

        if (!candidates.empty())
        {
            std::uniform_int_distribution<int> dist_out(0, static_cast<int>(candidates.size()) - 1);
            const int item_in = candidates[dist_out(rng_)];

            shaken.removeItem(item_out, instance_.profits[item_out], instance_.weights[item_out]);
            shaken.addItem(item_in, instance_.profits[item_in], instance_.weights[item_in]);
        }
    }

    return shaken;
}

Solution VNS::shakeSwap21(const Solution &solution, int strength)
{
    Solution shaken = solution;

    for (int s = 0; s < strength; ++s)
    {
        std::vector<int> items_in(shaken.selected_items.begin(),
                                  shaken.selected_items.end());

        if (items_in.size() < 2)
        {
            break;
        }

        // Seleciona dois itens aleatórios para remover
        std::uniform_int_distribution<int> dist(0, static_cast<int>(items_in.size()) - 1);
        const int idx1 = dist(rng_);
        int idx2 = dist(rng_);
        while (idx2 == idx1)
        {
            idx2 = dist(rng_);
        }

        const int item_out1 = items_in[idx1];
        const int item_out2 = items_in[idx2];

        const int freed_weight = instance_.weights[item_out1] + instance_.weights[item_out2];

        // Coleta candidatos para inserção
        std::vector<int> candidates;
        for (int i = 0; i < instance_.n_items; ++i)
        {
            if (shaken.hasItem(i))
            {
                continue;
            }

            const int new_weight = shaken.total_weight - freed_weight + instance_.weights[i];
            if (new_weight > instance_.capacity)
            {
                continue;
            }

            bool has_conflict = false;
            for (int sel : shaken.selected_items)
            {
                if (sel == item_out1 || sel == item_out2)
                {
                    continue;
                }
                if (instance_.hasConflict(i, sel))
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

        if (!candidates.empty())
        {
            std::uniform_int_distribution<int> cand_dist(0, static_cast<int>(candidates.size()) - 1);
            const int item_in = candidates[cand_dist(rng_)];

            shaken.removeItem(item_out1, instance_.profits[item_out1], instance_.weights[item_out1]);
            shaken.removeItem(item_out2, instance_.profits[item_out2], instance_.weights[item_out2]);
            shaken.addItem(item_in, instance_.profits[item_in], instance_.weights[item_in]);
        }
    }

    // Tenta preencher espaço restante
    greedyRandomInsert(shaken);

    return shaken;
}

Solution VNS::shake(const Solution &solution, int k, int strength)
{
    switch (k)
    {
    case 1:
        return shakeAddDrop(solution, strength);
    case 2:
        return shakeSwap11(solution, strength);
    case 3:
        return shakeSwap21(solution, strength);
    default:
        return solution;
    }
}

void VNS::greedyRandomInsert(Solution &solution)
{
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

    while (!candidates.empty())
    {
        const int rcl_size = std::min(3, static_cast<int>(candidates.size()));
        std::uniform_int_distribution<int> dist(0, rcl_size - 1);
        const int idx = dist(rng_);
        const int item = candidates[idx];

        if (solution.total_weight + instance_.weights[item] <= instance_.capacity &&
            validator_.checkConflicts(item, solution.selected_items))
        {
            solution.addItem(item, instance_.profits[item], instance_.weights[item]);
        }

        candidates.erase(candidates.begin() + idx);

        std::erase_if(candidates, [this, &solution](int c)
                      { return solution.total_weight + instance_.weights[c] > instance_.capacity ||
                               !validator_.checkConflicts(c, solution.selected_items); });
    }
}

Solution VNS::solve(
    const Solution &initial_solution,
    int max_iterations,
    int k_max,
    int shake_strength,
    int vnd_max_iter)
{
    const auto start = std::chrono::steady_clock::now();

    // Aplica VND na solução inicial para obter ótimo local
    VND vnd(instance_);
    Solution current = vnd.solve(initial_solution, vnd_max_iter);
    Solution best = current;

    int improvements = 0;
    int total_shakes = 0;

    for (int iter = 0; iter < max_iterations; ++iter)
    {
        int k = 1;

        while (k <= k_max)
        {
            // Shaking na k-ésima vizinhança
            Solution shaken = shake(current, k, shake_strength);
            validator_.validate(shaken);
            ++total_shakes;

            // Busca local com VND
            Solution local_opt = vnd.solve(shaken, vnd_max_iter);

            if (local_opt.total_profit > current.total_profit)
            {
                // Melhoria encontrada: aceita e reseta k
                current = std::move(local_opt);
                k = 1;

                // Atualiza melhor global
                if (current.total_profit > best.total_profit)
                {
                    best = current;
                    ++improvements;
                }
            }
            else
            {
                // Sem melhoria: avança para próxima vizinhança
                ++k;
            }
        }
    }

    const auto end = std::chrono::steady_clock::now();
    const std::chrono::duration<double> elapsed = end - start;

    best.computation_time = elapsed.count();
    best.method_name = "VNS";

    validator_.validate(best);

    std::cout << "VNS: "
              << "Valor = " << best.total_profit
              << ", Iteracoes = " << max_iterations
              << ", Shakes = " << total_shakes
              << ", Melhorias = " << improvements
              << ", k_max = " << k_max
              << ", Tempo = " << std::fixed << std::setprecision(4)
              << best.computation_time << "s\n";

    return best;
}

void VNS::setSeed(unsigned int seed) noexcept
{
    rng_.seed(seed);
}
