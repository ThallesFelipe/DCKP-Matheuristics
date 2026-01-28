/**
 * @file instance_reader.cpp
 * @brief Implementacao da classe DCKPInstance
 */

#include "instance_reader.h"
#include <fstream>
#include <iostream>
#include <algorithm>
#include <numeric>

DCKPInstance::DCKPInstance()
    : n_items(0), capacity(0), n_conflicts(0) {}

bool DCKPInstance::readFromFile(const std::string &filename)
{
    std::ifstream file(filename);
    if (!file.is_open())
    {
        std::cerr << "Erro ao abrir: " << filename << std::endl;
        return false;
    }

    file >> n_items >> capacity >> n_conflicts;

    if (n_items <= 0 || capacity <= 0)
    {
        std::cerr << "Dados invalidos: " << filename << std::endl;
        return false;
    }

    profits.resize(n_items);
    weights.resize(n_items);
    conflict_graph.resize(n_items);

    for (int i = 0; i < n_items; i++)
        file >> profits[i];

    for (int i = 0; i < n_items; i++)
        file >> weights[i];

    int item1, item2;
    while (file >> item1 >> item2)
    {
        item1--;
        item2--;
        if (item1 >= 0 && item1 < n_items && item2 >= 0 && item2 < n_items)
            conflicts.emplace_back(item1, item2);
    }

    buildConflictGraph();
    return true;
}

void DCKPInstance::buildConflictGraph()
{
    for (auto &adj : conflict_graph)
        adj.clear();

    for (const auto &c : conflicts)
    {
        conflict_graph[c.first].push_back(c.second);
        conflict_graph[c.second].push_back(c.first);
    }

    for (auto &adj : conflict_graph)
        std::sort(adj.begin(), adj.end());
}

bool DCKPInstance::hasConflict(int item1, int item2) const
{
    if (item1 < 0 || item1 >= n_items || item2 < 0 || item2 >= n_items)
        return false;

    const auto &adj = (conflict_graph[item1].size() <= conflict_graph[item2].size())
                          ? conflict_graph[item1]
                          : conflict_graph[item2];
    int target = (conflict_graph[item1].size() <= conflict_graph[item2].size()) ? item2 : item1;

    return std::binary_search(adj.begin(), adj.end(), target);
}

void DCKPInstance::print() const
{
    double avg_profit = std::accumulate(profits.begin(), profits.end(), 0.0) / n_items;
    double avg_weight = std::accumulate(weights.begin(), weights.end(), 0.0) / n_items;

    std::cout << "Instancia: n=" << n_items
              << ", W=" << capacity
              << ", conflitos=" << conflicts.size()
              << " (" << getConflictDensity() << "%)\n";
    std::cout << "  Lucro: [" << *std::min_element(profits.begin(), profits.end())
              << "-" << *std::max_element(profits.begin(), profits.end())
              << "], media=" << avg_profit << "\n";
    std::cout << "  Peso: [" << *std::min_element(weights.begin(), weights.end())
              << "-" << *std::max_element(weights.begin(), weights.end())
              << "], media=" << avg_weight << "\n";
}

double DCKPInstance::getConflictDensity() const
{
    if (n_items <= 1)
        return 0.0;
    return (200.0 * conflicts.size()) / (static_cast<double>(n_items) * (n_items - 1));
}
