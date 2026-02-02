/**
 * @file grasp.h
 * @brief Heurística construtiva GRASP para o DCKP
 *
 * Implementa a metaheurística GRASP (Greedy Randomized Adaptive Search Procedure)
 * na fase construtiva, com lista restrita de candidatos (RCL).
 *
 * @author Thalles e Luiz
 * @version 2.0
 */

#ifndef GRASP_H
#define GRASP_H

#include "../utils/instance_reader.h"
#include "../utils/solution.h"
#include "../utils/validator.h"

#include <random>
#include <vector>

/**
 * @class GRASPConstructive
 * @brief Implementa a fase construtiva do GRASP
 *
 * Constrói soluções usando aleatoriedade controlada através de uma
 * Lista Restrita de Candidatos (RCL), permitindo maior diversificação.
 *
 * @note Usa Mersenne Twister (std::mt19937) para geração de números aleatórios.
 */
class GRASPConstructive
{
public:
    /**
     * @brief Construtor
     * @param inst Referência para a instância do problema
     * @param seed Semente para o gerador aleatório (default: 42)
     */
    explicit GRASPConstructive(const DCKPInstance &inst, unsigned int seed = 42) noexcept;

    /**
     * @brief Executa múltiplas iterações do GRASP
     * @param iterations Número de iterações (default: 100)
     * @param alpha Parâmetro de controle da aleatoriedade [0, 1] (default: 0.3)
     * @return Melhor solução encontrada
     *
     * @note alpha=0 → guloso puro; alpha=1 → totalmente aleatório
     */
    [[nodiscard]] Solution solve(int iterations = 100, double alpha = 0.3);

    /**
     * @brief Define nova semente para o gerador aleatório
     * @param seed Nova semente
     */
    void setSeed(unsigned int seed) noexcept;

private:
    const DCKPInstance &instance_; ///< Referência para a instância
    Validator validator_;          ///< Validador de soluções
    std::mt19937 rng_;             ///< Gerador de números aleatórios (Mersenne Twister)

    /**
     * @brief Estrutura para armazenar candidatos
     */
    struct Candidate
    {
        int item_id;
        double score;

        [[nodiscard]] bool operator>(const Candidate &other) const noexcept
        {
            return score > other.score;
        }
    };

    /**
     * @brief Calcula o score de um item baseado em valor/peso
     * @param item Índice do item
     * @param current_solution Solução parcial atual
     * @return Score calculado
     */
    [[nodiscard]] double calculateScore(int item, const Solution &current_solution) const noexcept;

    /**
     * @brief Constrói a Lista Restrita de Candidatos
     * @param current_solution Solução parcial atual
     * @param alpha Parâmetro de controle da RCL (0 = guloso, 1 = aleatório)
     * @return Vetor de candidatos na RCL
     */
    [[nodiscard]] std::vector<int> buildRCL(const Solution &current_solution, double alpha) const;

    /**
     * @brief Seleciona aleatoriamente um item da RCL
     * @param rcl Lista Restrita de Candidatos
     * @return Índice do item selecionado, ou -1 se RCL vazia
     */
    [[nodiscard]] int selectFromRCL(const std::vector<int> &rcl);

    /**
     * @brief Constrói uma única solução usando o procedimento GRASP
     * @param alpha Parâmetro de controle da aleatoriedade [0, 1]
     * @return Solução construída
     */
    [[nodiscard]] Solution constructSolution(double alpha);
};

#endif // GRASP_H
