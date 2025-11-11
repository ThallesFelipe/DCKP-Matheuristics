/**
 * @file instance_reader.cpp
 * @brief Implementação da classe DCKPInstance
 */

#include "instance_reader.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>

DCKPInstance::DCKPInstance()
    : n_items(0), capacity(0), n_conflicts(0) {}

bool DCKPInstance::readFromFile(const std::string &filename)
{
    std::ifstream file(filename);
    if (!file.is_open())
    {
        std::cerr << "Erro ao abrir arquivo: " << filename << std::endl;
        return false;
    }

    // Lê a primeira linha: n_items capacity n_conflicts
    file >> n_items >> capacity >> n_conflicts;

    if (n_items <= 0 || capacity <= 0)
    {
        std::cerr << "Dados inválidos no arquivo: " << filename << std::endl;
        return false;
    }

    // Redimensiona os vetores
    profits.resize(n_items);
    weights.resize(n_items);
    conflict_graph.resize(n_items);

    // Lê os valores (profits)
    for (int i = 0; i < n_items; i++)
    {
        file >> profits[i];
    }

    // Lê os pesos (weights)
    for (int i = 0; i < n_items; i++)
    {
        file >> weights[i];
    }

    // Lê os pares de conflitos
    int item1, item2;
    while (file >> item1 >> item2)
    {
        // Converte de base-1 para base-0
        item1--;
        item2--;

        if (item1 >= 0 && item1 < n_items && item2 >= 0 && item2 < n_items)
        {
            conflicts.push_back({item1, item2});
        }
    }

    file.close();

    // Constrói o grafo de adjacência
    buildConflictGraph();

    std::cout << "Instância lida com sucesso: " << filename << std::endl;
    std::cout << "  Itens: " << n_items << ", Capacidade: " << capacity
              << ", Conflitos: " << conflicts.size() << std::endl;

    return true;
}

void DCKPInstance::buildConflictGraph()
{
    // Limpa o grafo existente
    for (auto &adj : conflict_graph)
    {
        adj.clear();
    }

    // Adiciona as arestas (ambas direções, pois é não-direcionado)
    for (const auto &conflict : conflicts)
    {
        int i = conflict.first;
        int j = conflict.second;

        conflict_graph[i].push_back(j);
        conflict_graph[j].push_back(i);
    }

    // Ordena as listas de adjacência para buscas binárias eficientes
    for (auto &adj : conflict_graph)
    {
        std::sort(adj.begin(), adj.end());
    }
}

bool DCKPInstance::hasConflict(int item1, int item2) const
{
    if (item1 < 0 || item1 >= n_items || item2 < 0 || item2 >= n_items)
    {
        return false;
    }

    // Busca binária na lista de adjacência do item com menos conflitos
    const auto &adj = (conflict_graph[item1].size() <= conflict_graph[item2].size())
                          ? conflict_graph[item1]
                          : conflict_graph[item2];
    int search_item = (conflict_graph[item1].size() <= conflict_graph[item2].size())
                          ? item2
                          : item1;

    return std::binary_search(adj.begin(), adj.end(), search_item);
}

void DCKPInstance::print() const
{
    std::cout << "\n=== Informações da Instância DCKP ===" << std::endl;
    std::cout << "Número de itens: " << n_items << std::endl;
    std::cout << "Capacidade: " << capacity << std::endl;
    std::cout << "Número de conflitos: " << conflicts.size() << std::endl;
    std::cout << "Densidade de conflitos: " << getConflictDensity() << "%" << std::endl;

    // Estatísticas dos valores
    int min_profit = *std::min_element(profits.begin(), profits.end());
    int max_profit = *std::max_element(profits.begin(), profits.end());
    double avg_profit = 0.0;
    for (int p : profits)
        avg_profit += p;
    avg_profit /= n_items;

    std::cout << "Valores - Min: " << min_profit << ", Max: " << max_profit
              << ", Média: " << avg_profit << std::endl;

    // Estatísticas dos pesos
    int min_weight = *std::min_element(weights.begin(), weights.end());
    int max_weight = *std::max_element(weights.begin(), weights.end());
    double avg_weight = 0.0;
    for (int w : weights)
        avg_weight += w;
    avg_weight /= n_items;

    std::cout << "Pesos - Min: " << min_weight << ", Max: " << max_weight
              << ", Média: " << avg_weight << std::endl;
    std::cout << "====================================\n"
              << std::endl;
}

double DCKPInstance::getConflictDensity() const
{
    if (n_items <= 1)
        return 0.0;

    long long max_conflicts = (long long)n_items * (n_items - 1) / 2;
    return (100.0 * conflicts.size()) / max_conflicts;
}
