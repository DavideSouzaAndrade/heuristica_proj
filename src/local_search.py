"""Busca local 2-opt para TSPTW, com critério de dominância de Pareto.

Vizinhança 2-opt: para cada par i<j, gerar a permutação obtida ao
inverter o subsegmento perm[i:j+1]. O número de vizinhos é O(n²).

A versão de single-objective do CP1 (Hill Climbing/SA com 2-opt)
aceitava melhorias na distância. Aqui aceitamos melhorias na **fronteira
de Pareto multiobjetivo** (distância, violação):

    Um vizinho domina o atual se:
        f1(viz) <= f1(atual)  E  f2(viz) <= f2(atual)
        E pelo menos uma das duas desigualdades é estrita.

Implementamos *first-improvement* (aceita o primeiro vizinho dominante)
para limitar custo, e iteramos até atingir um máximo local Pareto ou
um teto de iterações (parâmetro `max_iter`).

Uso típico (chamado pela hibridização memetic):
    new_perm, new_eval = two_opt_pareto(inst, perm, max_iter=10)
"""

from __future__ import annotations

import numpy as np

from .evaluation import Evaluation, evaluate
from .instance import TSPTWInstance


def _dominates(a: Evaluation, b: Evaluation) -> bool:
    """True se a domina b (em distância e violação, com sentido de minimização)."""
    le = (a.distance <= b.distance) and (a.violation <= b.violation)
    lt = (a.distance < b.distance) or (a.violation < b.violation)
    return le and lt


def two_opt_pareto(
    inst: TSPTWInstance,
    perm: np.ndarray | list[int],
    max_iter: int = 10,
) -> tuple[np.ndarray, Evaluation]:
    """Local search 2-opt com dominância de Pareto.

    Retorna a melhor permutação encontrada (potencialmente igual à de
    entrada se já era ótimo local Pareto) e sua avaliação.
    """
    cur = np.asarray(perm, dtype=np.int64).copy()
    cur_ev = evaluate(inst, cur)
    n = cur.size

    for _ in range(max_iter):
        improved = False
        for i in range(n - 1):
            for j in range(i + 1, n):
                cand = cur.copy()
                cand[i : j + 1] = cand[i : j + 1][::-1]
                cand_ev = evaluate(inst, cand)
                if _dominates(cand_ev, cur_ev):
                    cur = cand
                    cur_ev = cand_ev
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break

    return cur, cur_ev


if __name__ == "__main__":
    from .instance import load_dumas

    inst = load_dumas("data/dumas/n20w20.001.txt")
    rng = np.random.default_rng(0)
    perm = rng.permutation(np.arange(1, inst.n))
    before = evaluate(inst, perm)
    new_perm, new_ev = two_opt_pareto(inst, perm, max_iter=20)
    print(f"antes: dist={before.distance:.0f}  viol={before.violation:.0f}")
    print(f"depois: dist={new_ev.distance:.0f}  viol={new_ev.violation:.0f}")
