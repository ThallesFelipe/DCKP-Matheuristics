/**
 * @file ils.h
 * @brief Iterated Local Search (ILS) para o DCKP
 *
 * Implementa a metaheurística ILS que aplica repetidas perturbações
 * seguidas de busca local (VND) para escapar de ótimos locais.
 *
 * @author Thalles e Luiz
 * @version 3.0
 */

#ifndef ILS_H
#define ILS_H

#include "../utils/instance_reader.h"
#include "../utils/solution.h"
#include "../utils/validator.h"

#include <random>

/**
 * @class ILS
 * @brief Iterated Local Search para o DCKP
 *
 * Estratégia:
 *   1. Aplica VND na solução inicial para obter ótimo local.
 *   2. Repete até max_iterations:
 *      a) Perturba a solução corrente (remove itens aleatórios + insere viáveis).
 *      b) Aplica VND na solução perturbada.
 *      c) Aceita se melhorar (ou empatar, para diversificação).
 *      d) Atualiza melhor global.
 *   3. Retorna a melhor solução encontrada.
 */
class ILS
{
public:
    /**
     * @brief Construtor
     * @param inst Referência para a instância do DCKP
     * @param seed Semente para o gerador aleatório (default: 42)
     */
    explicit ILS(const DCKPInstance &inst, unsigned int seed = 42) noexcept;

    /**
     * @brief Executa o ILS a partir de uma solução inicial
     *
     * @param initial_solution Solução inicial (tipicamente gerada pelo GRASP)
     * @param max_iterations Número máximo de iterações ILS (default: 100)
     * @param perturbation_strength Número de itens a remover na perturbação (default: 3)
     * @param vnd_max_iter Limite de iterações do VND interno (default: 1000)
     * @return Melhor solução encontrada
     */
    [[nodiscard]] Solution solve(
        const Solution &initial_solution,
        int max_iterations = 100,
        int perturbation_strength = 3,
        int vnd_max_iter = 1000);

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
     * @brief Perturba a solução removendo itens aleatórios e inserindo viáveis
     *
     * @param solution Solução a ser perturbada
     * @param strength Número de itens a remover
     * @return Solução perturbada
     */
    [[nodiscard]] Solution perturb(const Solution &solution, int strength);

    /**
     * @brief Tenta inserir itens viáveis na solução de forma gulosa-aleatória
     *
     * @param solution Solução parcial onde itens serão inseridos
     */
    void greedyRandomInsert(Solution &solution);
};

#endif // ILS_H
