/**
 * @file instance_reader.h
 * @brief Classe para leitura e armazenamento de instâncias do DCKP
 *
 * Esta classe é responsável por ler arquivos de instâncias do problema
 * Disjunctively Constrained Knapsack Problem (DCKP) e armazenar os dados
 * em estruturas eficientes para processamento.
 */

#ifndef INSTANCE_READER_H
#define INSTANCE_READER_H

#include <vector>
#include <string>
#include <utility>

/**
 * @class DCKPInstance
 * @brief Representa uma instância do problema DCKP
 *
 * Armazena todos os dados necessários de uma instância:
 * - Número de itens e capacidade da mochila
 * - Valores (profits) e pesos (weights) de cada item
 * - Grafo de conflitos entre itens
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
     */
    DCKPInstance();

    /**
     * @brief Lê uma instância de um arquivo
     * @param filename Caminho completo para o arquivo da instância
     * @return true se a leitura foi bem-sucedida, false caso contrário
     */
    bool readFromFile(const std::string &filename);

    /**
     * @brief Constrói o grafo de adjacência a partir da lista de conflitos
     *
     * Cria uma representação em lista de adjacência para consultas
     * eficientes de conflitos entre itens.
     */
    void buildConflictGraph();

    /**
     * @brief Verifica se dois itens estão em conflito
     * @param item1 Índice do primeiro item (base 0)
     * @param item2 Índice do segundo item (base 0)
     * @return true se os itens estão em conflito, false caso contrário
     */
    bool hasConflict(int item1, int item2) const;

    /**
     * @brief Imprime informações básicas da instância
     */
    void print() const;

    /**
     * @brief Calcula a densidade do grafo de conflitos
     * @return Percentual de conflitos em relação ao total possível
     */
    double getConflictDensity() const;
};

#endif // INSTANCE_READER_H
