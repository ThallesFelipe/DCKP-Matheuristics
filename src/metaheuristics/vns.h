/**
 * @file vns.h
 * @brief Variable Neighborhood Search (VNS) para o DCKP
 *
 * Implementa a metaheurística VNS com ciclo shake + busca local (VND),
 * variando sistematicamente a vizinhança de perturbação para escapar
 * de ótimos locais.
 *
 * @author Thalles e Luiz
 * @version 3.0
 */

#ifndef VNS_H
#define VNS_H

#include "../utils/instance_reader.h"
#include "../utils/solution.h"
#include "../utils/validator.h"

#include <random>

/**
 * @class VNS
 * @brief Variable Neighborhood Search para o DCKP
 *
 * Vizinhanças de shaking:
 *   k=1: Add/Drop aleatório
 *   k=2: Swap 1-1 aleatório
 *   k=3: Swap 2-1 aleatório
 *
 * Após cada shaking, aplica VND como busca local.
 * Se melhorar, aceita e reseta k=1; senão, k++.
 */
class VNS
{
public:
    /**
     * @brief Construtor
     * @param inst Referência para a instância do DCKP
     * @param seed Semente para o gerador aleatório (default: 42)
     */
    explicit VNS(const DCKPInstance &inst, unsigned int seed = 42) noexcept;

    /**
     * @brief Executa o VNS a partir de uma solução inicial
     *
     * @param initial_solution Solução inicial (tipicamente gerada pelo GRASP)
     * @param max_iterations Número máximo de iterações globais (default: 100)
     * @param k_max Número máximo de vizinhanças de shaking (default: 3)
     * @param shake_strength Intensidade do shaking por vizinhança (default: 2)
     * @param vnd_max_iter Limite de iterações do VND interno (default: 1000)
     * @return Melhor solução encontrada
     */
    [[nodiscard]] Solution solve(
        const Solution &initial_solution,
        int max_iterations = 100,
        int k_max = 3,
        int shake_strength = 2,
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
     * @brief Realiza shaking na k-ésima vizinhança
     *
     * @param solution Solução base
     * @param k Índice da vizinhança (1 = Add/Drop, 2 = Swap 1-1, 3 = Swap 2-1)
     * @param strength Intensidade do shaking (número de movimentos)
     * @return Solução perturbada
     */
    [[nodiscard]] Solution shake(const Solution &solution, int k, int strength);

    /**
     * @brief Shaking por Add/Drop aleatório
     * @param solution Solução base
     * @param strength Número de movimentos
     * @return Solução perturbada
     */
    [[nodiscard]] Solution shakeAddDrop(const Solution &solution, int strength);

    /**
     * @brief Shaking por Swap 1-1 aleatório
     * @param solution Solução base
     * @param strength Número de swaps
     * @return Solução perturbada
     */
    [[nodiscard]] Solution shakeSwap11(const Solution &solution, int strength);

    /**
     * @brief Shaking por Swap 2-1 aleatório
     * @param solution Solução base
     * @param strength Número de movimentos
     * @return Solução perturbada
     */
    [[nodiscard]] Solution shakeSwap21(const Solution &solution, int strength);

    /**
     * @brief Tenta inserir itens viáveis na solução de forma gulosa-aleatória
     * @param solution Solução parcial onde itens serão inseridos
     */
    void greedyRandomInsert(Solution &solution);
};

#endif // VNS_H
