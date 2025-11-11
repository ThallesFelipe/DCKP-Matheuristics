/**
 * @file grasp.h
 * @brief Heurística construtiva GRASP para o DCKP
 *
 * Implementa a metaheurística GRASP (Greedy Randomized Adaptive Search Procedure)
 * na fase construtiva, com lista restrita de candidatos (RCL).
 */

#ifndef GRASP_H
#define GRASP_H

#include "../utils/instance_reader.h"
#include "../utils/solution.h"
#include "../utils/validator.h"
#include <vector>
#include <random>

/**
 * @class GRASPConstructive
 * @brief Implementa a fase construtiva do GRASP
 *
 * Constrói soluções usando aleatoriedade controlada através de uma
 * Lista Restrita de Candidatos (RCL), permitindo maior diversificação.
 */
class GRASPConstructive
{
private:
    const DCKPInstance &instance; ///< Referência para a instância
    Validator validator;          ///< Validador de soluções
    std::mt19937 rng;             ///< Gerador de números aleatórios

    /**
     * @brief Estrutura para armazenar candidatos
     */
    struct Candidate
    {
        int item_id;
        double score;

        bool operator>(const Candidate &other) const
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
    double calculateScore(int item, const Solution &current_solution) const;

    /**
     * @brief Constrói a Lista Restrita de Candidatos
     * @param current_solution Solução parcial atual
     * @param alpha Parâmetro de controle da RCL (0 = guloso, 1 = aleatório)
     * @return Vetor de candidatos na RCL
     */
    std::vector<int> buildRCL(const Solution &current_solution, double alpha) const;

    /**
     * @brief Seleciona aleatoriamente um item da RCL
     * @param rcl Lista Restrita de Candidatos
     * @return Índice do item selecionado
     */
    int selectFromRCL(const std::vector<int> &rcl);

public:
    /**
     * @brief Construtor
     * @param inst Referência para a instância do problema
     * @param seed Semente para o gerador aleatório
     */
    explicit GRASPConstructive(const DCKPInstance &inst, unsigned int seed = 42);

    /**
     * @brief Constrói uma solução usando GRASP
     * @param alpha Parâmetro de controle da aleatoriedade [0, 1]
     * @return Solução construída
     */
    Solution construct(double alpha = 0.3);

    /**
     * @brief Executa múltiplas iterações do GRASP
     * @param iterations Número de iterações
     * @param alpha Parâmetro de controle da aleatoriedade
     * @return Melhor solução encontrada
     */
    Solution multiStart(int iterations, double alpha = 0.3);

    /**
     * @brief Executa GRASP com diferentes valores de alpha
     * @param iterations Iterações por valor de alpha
     * @return Vetor com as melhores soluções para cada alpha
     */
    std::vector<Solution> tuneAlpha(int iterations = 10);

    /**
     * @brief Define nova semente para o gerador aleatório
     * @param seed Nova semente
     */
    void setSeed(unsigned int seed);
};

#endif // GRASP_H
