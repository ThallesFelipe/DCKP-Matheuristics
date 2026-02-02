/**
 * @file validator.h
 * @brief Classe para validação de soluções do DCKP
 *
 * Esta classe é responsável por verificar se uma solução
 * satisfaz todas as restrições do problema DCKP.
 *
 * @author Thalles e Luiz
 * @version 2.0
 */

#ifndef VALIDATOR_H
#define VALIDATOR_H

#include "instance_reader.h"
#include "solution.h"

#include <set>
#include <string>

/**
 * @class Validator
 * @brief Valida soluções do DCKP
 *
 * Verifica:
 * 1. Restrição de capacidade: peso total <= capacidade
 * 2. Restrições de conflitos: nenhum par de itens em conflito
 */
class Validator
{
public:
    /**
     * @brief Construtor
     * @param inst Referência para a instância do problema
     */
    explicit Validator(const DCKPInstance &inst) noexcept;

    /**
     * @brief Valida uma solução completa
     * @param solution Solução a ser validada (modificada: atualiza is_feasible e métricas)
     * @return true se a solução é viável, false caso contrário
     */
    bool validate(Solution &solution) const;

    /**
     * @brief Verifica se adicionar um item viola a capacidade
     * @param current_weight Peso atual da solução
     * @param item_weight Peso do item a ser adicionado
     * @return true se NÃO viola a capacidade, false caso contrário
     */
    [[nodiscard]] bool checkCapacity(int current_weight, int item_weight) const noexcept;

    /**
     * @brief Verifica se um item conflita com itens já selecionados
     * @param item Índice do item a ser verificado
     * @param selected_items Conjunto de itens já selecionados
     * @return true se NÃO há conflitos, false caso contrário
     */
    [[nodiscard]] bool checkConflicts(int item, const std::set<int> &selected_items) const noexcept;

    /**
     * @brief Valida e retorna informações detalhadas
     * @param solution Solução a ser validada (somente leitura)
     * @return String com detalhes da validação
     */
    [[nodiscard]] std::string validateDetailed(const Solution &solution) const;

    /**
     * @brief Recalcula o valor e peso de uma solução
     * @param solution Solução a ser recalculada (modificada)
     */
    void recalculateMetrics(Solution &solution) const noexcept;

private:
    const DCKPInstance &instance_; ///< Referência para a instância
};

#endif // VALIDATOR_H
