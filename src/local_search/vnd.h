/**
 * @file vnd.h
 * @brief Variable Neighborhood Descent (VND) para o DCKP
 *
 * Implementa o VND com três estruturas de vizinhança para escapar de ótimos
 * locais através da troca sistemática entre vizinhanças de força crescente.
 *
 * @author Thalles e Luiz
 * @version 2.0
 */

#ifndef VND_H
#define VND_H

#include "../utils/instance_reader.h"
#include "../utils/solution.h"
#include "../utils/validator.h"

#include <utility>
#include <vector>

/**
 * @class VND
 * @brief Variable Neighborhood Descent para o DCKP
 *
 * Vizinhanças:
 *   N1 (Add/Drop): Adiciona ou remove um único item
 *   N2 (Swap 1-1): Troca um item dentro por um fora
 *   N3 (Swap 2-1): Remove dois itens para adicionar um (libera capacidade/conflitos)
 */
class VND
{
public:
    /**
     * @brief Construtor
     * @param inst Referência para a instância do DCKP
     */
    explicit VND(const DCKPInstance &inst) noexcept;

    /**
     * @brief Executa o VND a partir de uma solução inicial
     *
     * @param initial_solution Solução inicial (tipicamente de um construtivo)
     * @param max_iterations Número máximo total de iterações entre todas as vizinhanças
     * @return Melhor solução encontrada
     */
    [[nodiscard]] Solution solve(const Solution &initial_solution, int max_iterations = 1000);

private:
    const DCKPInstance &instance_; ///< Referência para a instância
    Validator validator_;          ///< Validador de soluções

    /**
     * @brief Tipos de vizinhança na ordem de exploração
     */
    enum class NeighborhoodType
    {
        ADD_DROP = 1, ///< Vizinhança N1: adicionar ou remover item
        SWAP_1_1 = 2, ///< Vizinhança N2: trocar 1 por 1
        SWAP_2_1 = 3  ///< Vizinhança N3: remover 2, adicionar 1
    };

    /**
     * @brief Gera a vizinhança Add/Drop (N1)
     *
     * Tenta adicionar qualquer item viável ou remover qualquer item da solução.
     *
     * @param current_sol Solução atual
     * @return Vetor de soluções vizinhas
     */
    [[nodiscard]] std::vector<Solution> generateAddDropNeighborhood(const Solution &current_sol) const;

    /**
     * @brief Gera a vizinhança Swap(1-1) (N2)
     *
     * Troca padrão de um item dentro por um item fora.
     *
     * @param current_sol Solução atual
     * @return Vetor de soluções vizinhas
     */
    [[nodiscard]] std::vector<Solution> generateSwap11Neighborhood(const Solution &current_sol) const;

    /**
     * @brief Gera a vizinhança Swap(2-1) (N3)
     *
     * Remove dois itens da solução e adiciona um. Útil quando
     * itens de alto lucro estão bloqueados por capacidade ou conflitos.
     *
     * @param current_sol Solução atual
     * @return Vetor de soluções vizinhas
     */
    [[nodiscard]] std::vector<Solution> generateSwap21Neighborhood(const Solution &current_sol) const;

    /**
     * @brief Explora uma vizinhança específica buscando a melhor melhoria
     *
     * @param current_sol Solução atual
     * @param type Vizinhança a explorar
     * @return Par (melhor_solucao, encontrou_melhoria)
     */
    [[nodiscard]] std::pair<Solution, bool> exploreNeighborhood(
        const Solution &current_sol,
        NeighborhoodType type) const;
};

#endif // VND_H
