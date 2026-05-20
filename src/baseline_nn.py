"""Heurística construtiva Nearest Neighbor com janelas de tempo.

A partir do depósito, escolhe sempre o próximo cliente que minimiza um
critério local sensível às janelas. Dois critérios estão implementados:

    * 'travel'  — apenas distância (NN clássico). Quebra empate por l_j.
    * 'urgency' — combinação t_chegada * (1 - α) + l_j * α, com α = 0.5
      por padrão. Privilegia clientes cuja janela está prestes a fechar.

Se nenhum cliente puder ser visitado dentro da janela, o NN ainda
escolhe (a melhor heurística aceita pequenas violações em vez de
abortar), gerando um tour mesmo em instâncias apertadas. A solução
final é entregue ao avaliador padrão.
"""

from __future__ import annotations

from typing import Literal

import numpy as np

from .instance import TSPTWInstance

Criterion = Literal["travel", "urgency"]


def nearest_neighbor(
    inst: TSPTWInstance, criterion: Criterion = "urgency", alpha: float = 0.5
) -> np.ndarray:
    n = inst.n
    dist = inst.dist
    e = inst.e
    l = inst.l
    depot = inst.depot

    unvisited = set(range(n))
    unvisited.discard(depot)

    perm = np.empty(n - 1, dtype=np.int64)
    current = depot
    time = 0.0

    for k in range(n - 1):
        best_j = -1
        best_score = np.inf
        for j in unvisited:
            t_arr = time + float(dist[current, j])
            start = max(t_arr, float(e[j]))
            if criterion == "travel":
                score = float(dist[current, j])
                if best_j != -1 and score == best_score and l[j] < l[best_j]:
                    best_j = j
                    continue
            else:
                score = (1 - alpha) * start + alpha * float(l[j])
            late = max(0.0, t_arr - float(l[j]))
            score += 1e6 * late
            if score < best_score:
                best_score = score
                best_j = j

        perm[k] = best_j
        time = max(time + float(dist[current, best_j]), float(e[best_j]))
        current = best_j
        unvisited.discard(best_j)

    return perm


if __name__ == "__main__":
    from .evaluation import evaluate
    from .instance import load_dumas

    inst = load_dumas("data/dumas/n20w20.001.txt")
    for crit in ("travel", "urgency"):
        perm = nearest_neighbor(inst, criterion=crit)
        ev = evaluate(inst, perm)
        flag = "OK" if ev.feasible else f"{ev.n_violations} late"
        print(f"NN-{crit:<7} dist={ev.distance:6.0f}  "
              f"violation={ev.violation:6.0f}  [{flag}]")
