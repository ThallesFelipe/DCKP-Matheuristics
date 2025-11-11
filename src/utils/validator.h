/**
 * @file validator.h
 * @brief Classe para validação de soluções do DCKP
 *
 * Esta classe é responsável por verificar se uma solução
 * satisfaz todas as restrições do problema DCKP.
 */

#ifndef VALIDATOR_H
#define VALIDATOR_H

#include "instance_reader.h"
#include "solution.h"
#include <string>

/**
 * @class Validator
 * @brief Valida soluções do DCKP
 *
 * Verifica:
 * 1. Restrição de capacidade
 * 2. Restrições de conflitos entre itens
 */
class Validator
{
private:
    const DCKPInstance &instance; ///< Referência para a instância

public:
    /**
     * @brief Construtor
     * @param inst Referência para a instância do problema
     */
    explicit Validator(const DCKPInstance &inst);

    /**
     * @brief Valida uma solução completa
     * @param solution Solução a ser validada
     * @return true se a solução é viável, false caso contrário
     */
    bool validate(Solution &solution) const;

    /**
     * @brief Verifica se adicionar um item viola a capacidade
     * @param current_weight Peso atual da solução
     * @param item_weight Peso do item a ser adicionado
     * @return true se não viola a capacidade, false caso contrário
     */
    bool checkCapacity(int current_weight, int item_weight) const;

    /**
     * @brief Verifica se um item conflita com itens já selecionados
     * @param item Índice do item a ser verificado
     * @param selected_items Conjunto de itens já selecionados
     * @return true se não há conflitos, false caso contrário
     */
    bool checkConflicts(int item, const std::set<int> &selected_items) const;

    /**
     * @brief Valida e retorna informações detalhadas
     * @param solution Solução a ser validada
     * @return String com detalhes da validação
     */
    std::string validateDetailed(const Solution &solution) const;

    /**
     * @brief Recalcula o valor e peso de uma solução
     * @param solution Solução a ser recalculada
     */
    void recalculateMetrics(Solution &solution) const;
};

#endif // VALIDATOR_H
