/**
 * @file instance_reader.cpp
 * @brief Implementação da classe DCKPInstance
 */

#include "instance_reader.h"

#include <algorithm>
#include <fstream>
#include <iostream>
#include <numeric>
#include <ranges>

DCKPInstance::DCKPInstance() noexcept
    : n_items(0), capacity(0), n_conflicts(0) {}

bool DCKPInstance::readFromFile(const std::string &filename)
{
    std::ifstream file(filename);
    if (!file.is_open())
    {
        std::cerr << "Erro ao abrir: " << filename << '\n';
        return false;
    }

    file >> n_items >> capacity >> n_conflicts;

    if (n_items <= 0 || capacity <= 0)
    {
        std::cerr << "Dados invalidos: " << filename << '\n';
        return false;
    }

    // Pré-alocação para evitar realocações
    profits.resize(n_items);
    weights.resize(n_items);
    conflict_graph.resize(n_items);
    conflicts.reserve(static_cast<std::size_t>(n_conflicts));

    for (int i = 0; i < n_items; ++i)
    {
        file >> profits[i];
    }

    for (int i = 0; i < n_items; ++i)
    {
        file >> weights[i];
    }

    int item1 = 0;
    int item2 = 0;
    while (file >> item1 >> item2)
    {
        // Converte de base 1 para base 0
        --item1;
        --item2;
        if (item1 >= 0 && item1 < n_items && item2 >= 0 && item2 < n_items)
        {
            conflicts.emplace_back(item1, item2);
        }
    }

    buildConflictGraph();
    return true;
}

void DCKPInstance::buildConflictGraph()
{
    // Limpa e reconstrói o grafo
    for (auto &adj : conflict_graph)
    {
        adj.clear();
    }

    // Adiciona arestas bidirecionais
    for (const auto &[u, v] : conflicts)
    {
        conflict_graph[u].push_back(v);
        conflict_graph[v].push_back(u);
    }

    // Ordena para busca binária eficiente
    for (auto &adj : conflict_graph)
    {
        std::ranges::sort(adj);
        // Remove duplicatas se houver
        auto [first, last] = std::ranges::unique(adj);
        adj.erase(first, last);
    }
}

bool DCKPInstance::hasConflict(int item1, int item2) const noexcept
{
    if (item1 < 0 || item1 >= n_items || item2 < 0 || item2 >= n_items)
    {
        return false;
    }

    // Busca na lista de adjacência menor para eficiência
    const auto &smaller = (conflict_graph[item1].size() <= conflict_graph[item2].size())
                              ? conflict_graph[item1]
                              : conflict_graph[item2];
    const int target = (conflict_graph[item1].size() <= conflict_graph[item2].size())
                           ? item2
                           : item1;

    return std::ranges::binary_search(smaller, target);
}

void DCKPInstance::print() const
{
    const double avg_profit = std::accumulate(profits.begin(), profits.end(), 0.0) /
                              static_cast<double>(n_items);
    const double avg_weight = std::accumulate(weights.begin(), weights.end(), 0.0) /
                              static_cast<double>(n_items);

    const auto [min_profit, max_profit] = std::ranges::minmax(profits);
    const auto [min_weight, max_weight] = std::ranges::minmax(weights);

    std::cout << "Instancia: n=" << n_items
              << ", W=" << capacity
              << ", conflitos=" << conflicts.size()
              << " (" << getConflictDensity() << "%)\n";
    std::cout << "  Lucro: [" << min_profit << "-" << max_profit
              << "], media=" << avg_profit << "\n";
    std::cout << "  Peso: [" << min_weight << "-" << max_weight
              << "], media=" << avg_weight << "\n";
}

double DCKPInstance::getConflictDensity() const noexcept
{
    if (n_items <= 1)
    {
        return 0.0;
    }
    const double max_edges = static_cast<double>(n_items) * (n_items - 1) / 2.0;
    return (100.0 * static_cast<double>(conflicts.size())) / max_edges;
}

int DCKPInstance::getConflictDegree(int item) const noexcept
{
    if (item < 0 || item >= n_items)
    {
        return 0;
    }
    return static_cast<int>(conflict_graph[item].size());
}
