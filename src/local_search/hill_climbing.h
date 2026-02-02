/**
 * @file hill_climbing.h
 * @brief Hill Climbing com estratégia Best Improvement para o DCKP
 *
 * Implementa uma busca local de subida mais íngreme usando vizinhança Swap(1-1).
 * O algoritmo explora exaustivamente a vizinhança e move-se para o melhor
 * vizinho até atingir um ótimo local.
 *
 * @author Thalles e Luiz
 * @version 2.0
 */

#ifndef HILL_CLIMBING_H
#define HILL_CLIMBING_H

#include "../utils/instance_reader.h"
#include "../utils/solution.h"
#include "../utils/validator.h"

#include <optional>
#include <vector>

/**
 * @class HillClimbing
 * @brief Hill Climbing com Best Improvement para o DCKP
 *
 * Utiliza vizinhança Swap(1-1): troca um item dentro da solução
 * por um item fora, respeitando as restrições de capacidade e conflitos.
 */
class HillClimbing
{
public:
    /**
     * @brief Construtor
     * @param inst Referência para a instância do DCKP
     */
    explicit HillClimbing(const DCKPInstance &inst) noexcept;

    /**
     * @brief Executa o Hill Climbing a partir de uma solução inicial
     *
     * @param initial_solution Solução inicial (tipicamente de um construtivo)
     * @param max_iterations Número máximo de iterações sem melhoria (default: 100)
     * @return Melhor solução encontrada (ótimo local)
     */
    [[nodiscard]] Solution solve(const Solution &initial_solution, int max_iterations = 100);

private:
    const DCKPInstance &instance_; ///< Referência para a instância
    Validator validator_;          ///< Validador de soluções

    /**
     * @brief Gera a vizinhança Swap(1-1)
     *
     * Para cada item i na solução, tenta trocar com cada item j
     * fora da solução. Apenas trocas viáveis são incluídas.
     *
     * @param current_sol Solução atual
     * @return Vetor de soluções vizinhas viáveis
     */
    [[nodiscard]] std::vector<Solution> generateSwapNeighborhood(const Solution &current_sol) const;

    /**
     * @brief Encontra o melhor vizinho (Best Improvement)
     *
     * @param current_sol Solução atual para comparação
     * @param neighborhood Vizinhança gerada
     * @return Melhor vizinho que melhora, ou std::nullopt se nenhum melhora
     */
    [[nodiscard]] std::optional<Solution> findBestNeighbor(
        const Solution &current_sol,
        const std::vector<Solution> &neighborhood) const;
};

#endif // HILL_CLIMBING_H
