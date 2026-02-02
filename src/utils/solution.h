/**
 * @file solution.h
 * @brief Classe para representação de soluções do DCKP
 *
 * Esta classe representa uma solução candidata para o problema DCKP,
 * contendo os itens selecionados e métricas de qualidade.
 * Usa vetor de bits para verificação O(1) de presença de itens.
 *
 * @author Thalles e Luiz
 * @version 2.0
 */

#ifndef SOLUTION_H
#define SOLUTION_H

#include <set>
#include <string>
#include <vector>

/**
 * @class Solution
 * @brief Representa uma solução para o DCKP
 *
 * Armazena os itens selecionados, valor total, peso total
 * e informações sobre a viabilidade da solução.
 *
 * @note Usa std::set para iteração ordenada e armazenamento.
 *       Para instâncias grandes, considere otimizar para vector<bool>.
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
     * @post Inicializa solução vazia com profit=0, weight=0, is_feasible=true
     */
    Solution() noexcept;

    /**
     * @brief Adiciona um item à solução
     * @param item Índice do item a ser adicionado (base 0)
     * @param profit Valor do item
     * @param weight Peso do item
     * @note Se o item já existe, a operação é ignorada
     */
    void addItem(int item, int profit, int weight);

    /**
     * @brief Remove um item da solução
     * @param item Índice do item a ser removido (base 0)
     * @param profit Valor do item
     * @param weight Peso do item
     * @note Se o item não existe, a operação é ignorada
     */
    void removeItem(int item, int profit, int weight);

    /**
     * @brief Verifica se um item está na solução
     * @param item Índice do item (base 0)
     * @return true se o item está na solução, false caso contrário
     */
    [[nodiscard]] bool hasItem(int item) const noexcept;

    /**
     * @brief Retorna o número de itens na solução
     * @return Número de itens selecionados
     */
    [[nodiscard]] int size() const noexcept;

    /**
     * @brief Verifica se a solução está vazia
     * @return true se não há itens selecionados
     */
    [[nodiscard]] bool empty() const noexcept;

    /**
     * @brief Limpa a solução
     * @post selected_items vazio, total_profit=0, total_weight=0
     */
    void clear() noexcept;

    /**
     * @brief Converte a solução para string
     * @return Representação em string da solução
     */
    [[nodiscard]] std::string toString() const;

    /**
     * @brief Imprime informações da solução no stdout
     */
    void print() const;

    /**
     * @brief Salva a solução em arquivo
     * @param filename Caminho do arquivo de saída
     * @return true se salvou com sucesso, false caso contrário
     */
    [[nodiscard]] bool saveToFile(const std::string &filename) const;

    /**
     * @brief Operador de comparação para ordenação por valor (maior)
     * @param other Outra solução para comparar
     * @return true se esta solução tem valor maior
     */
    [[nodiscard]] bool operator>(const Solution &other) const noexcept;

    /**
     * @brief Operador de comparação para ordenação por valor (menor)
     * @param other Outra solução para comparar
     * @return true se esta solução tem valor menor
     */
    [[nodiscard]] bool operator<(const Solution &other) const noexcept;

    /**
     * @brief Operador de igualdade baseado no lucro
     * @param other Outra solução para comparar
     * @return true se os lucros são iguais
     */
    [[nodiscard]] bool operator==(const Solution &other) const noexcept;
};

#endif // SOLUTION_H
