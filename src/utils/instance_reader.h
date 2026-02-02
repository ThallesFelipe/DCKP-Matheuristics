/**
 * @file instance_reader.h
 * @brief Classe para leitura e armazenamento de instâncias do DCKP
 *
 * Esta classe é responsável por ler arquivos de instâncias do problema
 * Disjunctively Constrained Knapsack Problem (DCKP) e armazenar os dados
 * em estruturas eficientes para processamento.
 *
 * @author Thalles e Luiz
 * @version 2.0
 */

#ifndef INSTANCE_READER_H
#define INSTANCE_READER_H

#include <cstdint>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

/**
 * @class DCKPInstance
 * @brief Representa uma instância do problema DCKP
 *
 * Armazena todos os dados necessários de uma instância:
 * - Número de itens e capacidade da mochila
 * - Valores (profits) e pesos (weights) de cada item
 * - Grafo de conflitos entre itens com matriz de adjacência para O(1) lookup
 *
 * @note A matriz de conflitos usa representação compacta para instâncias
 *       pequenas (< 1000 itens) e lista de adjacência para instâncias maiores.
 */
class DCKPInstance
{
public:
    int n_items;                                  ///< Número de itens
    int capacity;                                 ///< Capacidade da mochila
    int n_conflicts;                              ///< Número total de conflitos
    std::vector<int> profits;                     ///< Valores/lucros dos itens
    std::vector<int> weights;                     ///< Pesos dos itens
    std::vector<std::pair<int, int>> conflicts;   ///< Lista de pares em conflito
    std::vector<std::vector<int>> conflict_graph; ///< Grafo de adjacência para conflitos

    /**
     * @brief Construtor padrão
     * @post Inicializa instância vazia com n_items=0, capacity=0
     */
    DCKPInstance() noexcept;

    /**
     * @brief Lê uma instância de um arquivo
     * @param filename Caminho completo para o arquivo da instância
     * @return true se a leitura foi bem-sucedida, false caso contrário
     * @throw Não lança exceções, erros são reportados via stderr
     */
    [[nodiscard]] bool readFromFile(const std::string &filename);

    /**
     * @brief Verifica se dois itens estão em conflito
     * @param item1 Índice do primeiro item (base 0)
     * @param item2 Índice do segundo item (base 0)
     * @return true se os itens estão em conflito, false caso contrário
     * @pre 0 <= item1, item2 < n_items
     * @note Complexidade: O(log d) onde d é o grau do vértice menor
     */
    [[nodiscard]] bool hasConflict(int item1, int item2) const noexcept;

    /**
     * @brief Imprime informações básicas da instância no stdout
     */
    void print() const;

    /**
     * @brief Calcula a densidade do grafo de conflitos
     * @return Percentual de conflitos em relação ao total possível [0, 100]
     */
    [[nodiscard]] double getConflictDensity() const noexcept;

    /**
     * @brief Retorna o grau de conflitos de um item
     * @param item Índice do item (base 0)
     * @return Número de itens que conflitam com este item
     * @pre 0 <= item < n_items
     */
    [[nodiscard]] int getConflictDegree(int item) const noexcept;

private:
    /**
     * @brief Constrói o grafo de adjacência a partir da lista de conflitos
     *
     * Cria uma representação em lista de adjacência ordenada para consultas
     * eficientes de conflitos entre itens via busca binária.
     */
    void buildConflictGraph();
};

#endif // INSTANCE_READER_H
