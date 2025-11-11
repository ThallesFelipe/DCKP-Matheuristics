/**
 * @file solution.h
 * @brief Classe para representação de soluções do DCKP
 *
 * Esta classe representa uma solução candidata para o problema DCKP,
 * contendo os itens selecionados e métricas de qualidade.
 */

#ifndef SOLUTION_H
#define SOLUTION_H

#include <vector>
#include <set>
#include <string>

/**
 * @class Solution
 * @brief Representa uma solução para o DCKP
 *
 * Armazena os itens selecionados, valor total, peso total
 * e informações sobre a viabilidade da solução.
 */
class Solution
{
public:
    std::set<int> selected_items; ///< Conjunto de itens selecionados (índices base-0)
    int total_profit;             ///< Valor total da solução
    int total_weight;             ///< Peso total da solução
    bool is_feasible;             ///< Indica se a solução é viável
    double computation_time;      ///< Tempo de computação em segundos
    std::string method_name;      ///< Nome do método que gerou a solução

    /**
     * @brief Construtor padrão
     */
    Solution();

    /**
     * @brief Adiciona um item à solução
     * @param item Índice do item a ser adicionado (base 0)
     * @param profit Valor do item
     * @param weight Peso do item
     */
    void addItem(int item, int profit, int weight);

    /**
     * @brief Remove um item da solução
     * @param item Índice do item a ser removido (base 0)
     * @param profit Valor do item
     * @param weight Peso do item
     */
    void removeItem(int item, int profit, int weight);

    /**
     * @brief Verifica se um item está na solução
     * @param item Índice do item (base 0)
     * @return true se o item está na solução, false caso contrário
     */
    bool hasItem(int item) const;

    /**
     * @brief Retorna o número de itens na solução
     * @return Número de itens selecionados
     */
    int size() const;

    /**
     * @brief Limpa a solução
     */
    void clear();

    /**
     * @brief Cria uma cópia da solução
     * @return Nova solução idêntica a esta
     */
    Solution copy() const;

    /**
     * @brief Converte a solução para string
     * @return Representação em string da solução
     */
    std::string toString() const;

    /**
     * @brief Imprime informações da solução
     */
    void print() const;

    /**
     * @brief Salva a solução em arquivo
     * @param filename Caminho do arquivo de saída
     * @return true se salvou com sucesso, false caso contrário
     */
    bool saveToFile(const std::string &filename) const;

    /**
     * @brief Operador de comparação para ordenação por valor
     * @param other Outra solução para comparar
     * @return true se esta solução tem valor maior
     */
    bool operator>(const Solution &other) const;

    /**
     * @brief Operador de comparação para ordenação por valor
     * @param other Outra solução para comparar
     * @return true se esta solução tem valor menor
     */
    bool operator<(const Solution &other) const;
};

#endif // SOLUTION_H
