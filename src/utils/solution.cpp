/**
 * @file solution.cpp
 * @brief Implementacao da classe Solution
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
    if (selected_items.insert(item).second)
    {
        total_profit += profit;
        total_weight += weight;
    }
}

void Solution::removeItem(int item, int profit, int weight)
{
    if (selected_items.erase(item) > 0)
    {
        total_profit -= profit;
        total_weight -= weight;
    }
}

bool Solution::hasItem(int item) const
{
    return selected_items.count(item) > 0;
}

int Solution::size() const
{
    return static_cast<int>(selected_items.size());
}

void Solution::clear()
{
    selected_items.clear();
    total_profit = 0;
    total_weight = 0;
    is_feasible = true;
    computation_time = 0.0;
}

std::string Solution::toString() const
{
    std::ostringstream ss;
    ss << "[" << method_name << "] "
       << "Lucro=" << total_profit
       << ", Peso=" << total_weight
       << ", Itens=" << selected_items.size()
       << ", " << (is_feasible ? "Viavel" : "Inviavel")
       << ", " << std::fixed << std::setprecision(4) << computation_time << "s";
    return ss.str();
}

void Solution::print() const
{
    std::cout << toString() << std::endl;
}

bool Solution::saveToFile(const std::string &filename) const
{
    std::ofstream file(filename);
    if (!file.is_open())
        return false;

    file << total_profit << " " << total_weight << " " << selected_items.size() << "\n";
    for (int item : selected_items)
        file << (item + 1) << " ";
    file << "\n";

    return true;
}

bool Solution::operator>(const Solution &other) const
{
    return total_profit > other.total_profit;
}

bool Solution::operator<(const Solution &other) const
{
    return total_profit < other.total_profit;
}
