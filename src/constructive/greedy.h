/**
 * @file greedy.h
 * @brief Heurística construtiva Gulosa para o DCKP
 *
 * Implementa diferentes estratégias gulosas para construir
 * soluções viáveis do problema DCKP.
 *
 * @author Thalles e Luiz
 * @version 2.0
 */

#ifndef GREEDY_H
#define GREEDY_H

#include "../utils/instance_reader.h"
#include "../utils/solution.h"
#include "../utils/validator.h"

#include <string>
#include <string_view>
#include <vector>

/**
 * @enum GreedyStrategy
 * @brief Estratégias de ordenação para a heurística gulosa
 */
enum class GreedyStrategy
{
    MAX_PROFIT,        ///< Ordena por maior valor
    MIN_WEIGHT,        ///< Ordena por menor peso
    MAX_PROFIT_WEIGHT, ///< Ordena por maior razão valor/peso
    MIN_CONFLICTS      ///< Ordena por menor número de conflitos
};

/**
 * @class GreedyConstructive
 * @brief Implementa heurísticas construtivas gulosas
 *
 * Constrói soluções viáveis usando diferentes critérios de ordenação
 * e sempre respeitando as restrições de capacidade e conflitos.
 */
class GreedyConstructive
{
public:
    /**
     * @brief Construtor
     * @param inst Referência para a instância do problema
     */
    explicit GreedyConstructive(const DCKPInstance &inst) noexcept;

    /**
     * @brief Constrói uma solução usando estratégia gulosa
     * @param strategy Estratégia de construção
     * @return Solução construída
     */
    [[nodiscard]] Solution construct(GreedyStrategy strategy);

    /**
     * @brief Constrói soluções com todas as estratégias
     * @return Vetor com todas as soluções geradas
     */
    [[nodiscard]] std::vector<Solution> constructAll();

    /**
     * @brief Converte estratégia para string
     * @param strategy Estratégia
     * @return Nome da estratégia
     */
    [[nodiscard]] static std::string_view strategyToString(GreedyStrategy strategy) noexcept;

private:
    const DCKPInstance &instance_; ///< Referência para a instância
    Validator validator_;          ///< Validador de soluções

    /**
     * @brief Estrutura auxiliar para ordenação de itens
     */
    struct ItemScore
    {
        int item_id;
        double score;

        [[nodiscard]] bool operator>(const ItemScore &other) const noexcept
        {
            return score > other.score;
        }
    };

    /**
     * @brief Calcula o score de um item baseado na estratégia
     * @param item Índice do item
     * @param strategy Estratégia de scoring
     * @return Score calculado
     */
    [[nodiscard]] double calculateScore(int item, GreedyStrategy strategy) const noexcept;

    /**
     * @brief Ordena itens pela estratégia escolhida
     * @param strategy Estratégia de ordenação
     * @return Vetor de itens ordenados
     */
    [[nodiscard]] std::vector<int> sortItemsByStrategy(GreedyStrategy strategy) const;
};

#endif // GREEDY_H
