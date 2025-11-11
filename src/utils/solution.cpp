/**
 * @file solution.cpp
 * @brief Implementação da classe Solution
 */

#include "solution.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>

Solution::Solution()
    : total_profit(0), total_weight(0), is_feasible(true),
      computation_time(0.0), method_name("Unknown") {}

void Solution::addItem(int item, int profit, int weight)
{
    if (selected_items.find(item) == selected_items.end())
    {
        selected_items.insert(item);
        total_profit += profit;
        total_weight += weight;
    }
}

void Solution::removeItem(int item, int profit, int weight)
{
    if (selected_items.find(item) != selected_items.end())
    {
        selected_items.erase(item);
        total_profit -= profit;
        total_weight -= weight;
    }
}

bool Solution::hasItem(int item) const
{
    return selected_items.find(item) != selected_items.end();
}

int Solution::size() const
{
    return selected_items.size();
}

void Solution::clear()
{
    selected_items.clear();
    total_profit = 0;
    total_weight = 0;
    is_feasible = true;
    computation_time = 0.0;
}

Solution Solution::copy() const
{
    Solution new_sol;
    new_sol.selected_items = this->selected_items;
    new_sol.total_profit = this->total_profit;
    new_sol.total_weight = this->total_weight;
    new_sol.is_feasible = this->is_feasible;
    new_sol.computation_time = this->computation_time;
    new_sol.method_name = this->method_name;
    return new_sol;
}

std::string Solution::toString() const
{
    std::stringstream ss;
    ss << "Solution[Method=" << method_name
       << ", Profit=" << total_profit
       << ", Weight=" << total_weight
       << ", Items=" << selected_items.size()
       << ", Feasible=" << (is_feasible ? "Yes" : "No")
       << ", Time=" << std::fixed << std::setprecision(4) << computation_time << "s]";
    return ss.str();
}

void Solution::print() const
{
    std::cout << "\n=== Solução DCKP ===" << std::endl;
    std::cout << "Método: " << method_name << std::endl;
    std::cout << "Valor total: " << total_profit << std::endl;
    std::cout << "Peso total: " << total_weight << std::endl;
    std::cout << "Número de itens: " << selected_items.size() << std::endl;
    std::cout << "Viável: " << (is_feasible ? "Sim" : "Não") << std::endl;
    std::cout << "Tempo de computação: " << std::fixed << std::setprecision(4)
              << computation_time << " segundos" << std::endl;

    std::cout << "Itens selecionados: [";
    int count = 0;
    for (int item : selected_items)
    {
        if (count > 0)
            std::cout << ", ";
        std::cout << (item + 1); // Converte para base-1 para exibição
        count++;
        if (count >= 20)
        { // Limita a exibição
            std::cout << ", ...";
            break;
        }
    }
    std::cout << "]" << std::endl;
    std::cout << "===================\n"
              << std::endl;
}

bool Solution::saveToFile(const std::string &filename) const
{
    std::ofstream file(filename);
    if (!file.is_open())
    {
        std::cerr << "Erro ao criar arquivo: " << filename << std::endl;
        return false;
    }

    file << "# DCKP Solution File" << std::endl;
    file << "# Method: " << method_name << std::endl;
    file << "# Computation Time: " << computation_time << " seconds" << std::endl;
    file << "# Feasible: " << (is_feasible ? "Yes" : "No") << std::endl;
    file << total_profit << " " << total_weight << " " << selected_items.size() << std::endl;

    for (int item : selected_items)
    {
        file << (item + 1) << " "; // Salva em base-1
    }
    file << std::endl;

    file.close();
    return true;
}

bool Solution::operator>(const Solution &other) const
{
    return this->total_profit > other.total_profit;
}

bool Solution::operator<(const Solution &other) const
{
    return this->total_profit < other.total_profit;
}
